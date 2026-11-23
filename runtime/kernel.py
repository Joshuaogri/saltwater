"""Deterministic Saltwater runtime kernel and PostgreSQL persistence adapter."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from threading import RLock
from typing import Any, Callable, Protocol
from uuid import UUID, uuid4


class Lifecycle(StrEnum):
    STOPPED = "stopped"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    RECOVERING = "recovering"
    SAFE_HALT = "safe_halt"


TRANSITIONS = {
    Lifecycle.STOPPED: {Lifecycle.READY},
    Lifecycle.READY: {Lifecycle.STOPPED, Lifecycle.RUNNING, Lifecycle.RECOVERING},
    Lifecycle.RUNNING: {Lifecycle.STOPPED, Lifecycle.PAUSED, Lifecycle.RECOVERING},
    Lifecycle.PAUSED: {Lifecycle.STOPPED, Lifecycle.RUNNING, Lifecycle.RECOVERING},
    Lifecycle.RECOVERING: {Lifecycle.READY, Lifecycle.SAFE_HALT},
    Lifecycle.SAFE_HALT: {Lifecycle.RECOVERING},
}

LIFECYCLE_EVENT = {
    (Lifecycle.STOPPED, Lifecycle.READY): "RUNTIME_READY",
    (Lifecycle.READY, Lifecycle.RUNNING): "RUNTIME_START",
    (Lifecycle.PAUSED, Lifecycle.RUNNING): "RUNTIME_RESUME",
    (Lifecycle.RUNNING, Lifecycle.PAUSED): "RUNTIME_PAUSE",
    (Lifecycle.RUNNING, Lifecycle.STOPPED): "RUNTIME_STOP",
    (Lifecycle.READY, Lifecycle.STOPPED): "RUNTIME_STOP",
    (Lifecycle.PAUSED, Lifecycle.STOPPED): "RUNTIME_STOP",
    (Lifecycle.READY, Lifecycle.RECOVERING): "RUNTIME_RECOVERY",
    (Lifecycle.RUNNING, Lifecycle.RECOVERING): "RUNTIME_RECOVERY",
    (Lifecycle.PAUSED, Lifecycle.RECOVERING): "RUNTIME_RECOVERY",
    (Lifecycle.RECOVERING, Lifecycle.READY): "RUNTIME_RECOVERY",
    (Lifecycle.RECOVERING, Lifecycle.SAFE_HALT): "RUNTIME_RECOVERY",
    (Lifecycle.SAFE_HALT, Lifecycle.RECOVERING): "RUNTIME_RECOVERY",
}


class KernelError(RuntimeError):
    """A requested operation violates a runtime invariant."""


@dataclass(frozen=True, slots=True)
class Event:
    event_id: int
    code: str
    world_tick: int
    occurred_at_tick: int
    causation_id: int | None = None
    correlation_id: UUID | None = None
    idempotency_key: str | None = None


@dataclass(slots=True)
class RuntimeState:
    lifecycle: Lifecycle = Lifecycle.STOPPED
    player_present: bool = False
    bootstrap_open: bool = True
    world_tick: int = 0
    calendar_day: int = 0
    minute_of_day: int = 0
    last_event_id: int | None = None


class RuntimeStore(Protocol):
    """Atomic persistence boundary implemented by a durable store."""

    def snapshot(self) -> RuntimeState: ...
    def transition(self, target: Lifecycle, player_present: bool) -> RuntimeState: ...
    def append_tick(self, event: Event) -> RuntimeState: ...
    def append_event(self, event: Event) -> Event: ...
    def close_bootstrap(self) -> RuntimeState: ...


@dataclass
class InMemoryRuntimeStore:
    """Test-only store; never use this adapter for an authoritative game session."""

    state: RuntimeState = field(default_factory=RuntimeState)
    events: list[Event] = field(default_factory=list)
    idempotency: dict[str, Event] = field(default_factory=dict)
    _next_event_id: int = 1
    _lock: RLock = field(default_factory=RLock, repr=False)

    def snapshot(self) -> RuntimeState:
        with self._lock:
            return replace(self.state)

    def _append(self, event: Event) -> Event:
        stored = replace(event, event_id=self._next_event_id)
        self._next_event_id += 1
        self.events.append(stored)
        if stored.idempotency_key:
            self.idempotency[stored.idempotency_key] = stored
        self.state.last_event_id = stored.event_id
        return stored

    def close_bootstrap(self) -> RuntimeState:
        with self._lock:
            if not self.state.bootstrap_open:
                return self.snapshot()
            if self.state.lifecycle != Lifecycle.READY or self.state.world_tick != 0:
                raise KernelError("bootstrap can close only in ready state at world tick zero")
            self.state.bootstrap_open = False
            return self.snapshot()

    def transition(self, target: Lifecycle, player_present: bool) -> RuntimeState:
        with self._lock:
            old = self.state.lifecycle
            if target != old and target not in TRANSITIONS[old]:
                raise KernelError(f"invalid lifecycle transition: {old} -> {target}")
            if target == old:
                if player_present != self.state.player_present:
                    raise KernelError("presence changes require a lifecycle transition")
                return self.snapshot()
            if target == Lifecycle.RUNNING and (self.state.bootstrap_open or not player_present):
                raise KernelError("runtime requires closed bootstrap and a present player")
            if target == Lifecycle.STOPPED and player_present:
                raise KernelError("stopped runtime cannot have a present player")
            self.state.lifecycle = target
            self.state.player_present = player_present
            code = LIFECYCLE_EVENT.get((old, target))
            if code:
                self._append(Event(0, code, self.state.world_tick, self.state.world_tick))
            return self.snapshot()

    def append_event(self, event: Event) -> Event:
        with self._lock:
            if event.idempotency_key and event.idempotency_key in self.idempotency:
                existing = self.idempotency[event.idempotency_key]
                if existing.code != event.code:
                    raise KernelError("idempotency key was already used for a different event")
                return existing
            if event.world_tick != self.state.world_tick:
                raise KernelError("event tick must equal committed runtime tick")
            if self.state.lifecycle != Lifecycle.RUNNING or not self.state.player_present:
                raise KernelError("world events require a running, player-present runtime")
            if event.causation_id and event.causation_id not in {e.event_id for e in self.events}:
                raise KernelError("causation event does not exist")
            return self._append(event)

    def append_tick(self, event: Event) -> RuntimeState:
        with self._lock:
            if event.idempotency_key and event.idempotency_key in self.idempotency:
                existing = self.idempotency[event.idempotency_key]
                if existing.code != "CLOCK_ADVANCE":
                    raise KernelError("idempotency key was already used for a different event")
                return self.snapshot()
            if self.state.lifecycle != Lifecycle.RUNNING or not self.state.player_present:
                raise KernelError("world time is frozen unless player is present and runtime is running")
            if event.world_tick != self.state.world_tick + 1:
                raise KernelError("tick must advance exactly once")
            self.state.world_tick += 1
            self._append(event)
            return self.snapshot()


class PostgresRuntimeStore:
    """Transactional PostgreSQL adapter using a psycopg-compatible connection factory.

    The adapter never creates schemas or seeds world data. Apply the approved
    schema proposal separately to a disposable database before using this class.
    """

    def __init__(self, connect: Callable[[], Any]):
        self._connect = connect

    def _open(self):
        conn = self._connect()
        return conn

    @staticmethod
    def _state(cur) -> RuntimeState:
        cur.execute(
            "SELECT state,player_present,bootstrap_open,world_tick,calendar_day,minute_of_day,last_event_id "
            "FROM sw_runtime.state WHERE singleton=1"
        )
        row = cur.fetchone()
        if row is None:
            raise KernelError("runtime singleton is missing")
        return RuntimeState(
            lifecycle=list(Lifecycle)[int(row[0])],
            player_present=row[1],
            bootstrap_open=row[2],
            world_tick=row[3],
            calendar_day=row[4],
            minute_of_day=row[5],
            last_event_id=row[6],
        )

    def snapshot(self) -> RuntimeState:
        conn = self._open()
        try:
            with conn:
                with conn.cursor() as cur:
                    return self._state(cur)
        finally:
            conn.close()

    def close_bootstrap(self) -> RuntimeState:
        conn = self._open()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT state,bootstrap_open,world_tick FROM sw_runtime.state "
                        "WHERE singleton=1 FOR UPDATE"
                    )
                    row = cur.fetchone()
                    if row is None:
                        raise KernelError("runtime singleton is missing")
                    if row[1]:
                        if row[0] != 1 or row[2] != 0:
                            raise KernelError("bootstrap can close only in ready state at world tick zero")
                        cur.execute("UPDATE sw_runtime.state SET bootstrap_open=false WHERE singleton=1")
                    return self._state(cur)
        finally:
            conn.close()

    def transition(self, target: Lifecycle, player_present: bool) -> RuntimeState:
        conn = self._open()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT state,player_present,bootstrap_open,world_tick "
                        "FROM sw_runtime.state WHERE singleton=1 FOR UPDATE"
                    )
                    row = cur.fetchone()
                    if row is None:
                        raise KernelError("runtime singleton is missing")
                    old = list(Lifecycle)[int(row[0])]
                    if target == old:
                        if player_present != row[1]:
                            raise KernelError("presence changes require a lifecycle transition")
                        return self._state(cur)
                    if target not in TRANSITIONS[old]:
                        raise KernelError(f"invalid lifecycle transition: {old} -> {target}")
                    if target == Lifecycle.RUNNING and (row[2] or not player_present):
                        raise KernelError("runtime requires closed bootstrap and a present player")
                    if target == Lifecycle.STOPPED and player_present:
                        raise KernelError("stopped runtime cannot have a present player")
                    code = LIFECYCLE_EVENT.get((old, target))
                    cur.execute(
                        "UPDATE sw_runtime.state SET state=%s,player_present=%s WHERE singleton=1",
                        (list(Lifecycle).index(target), player_present),
                    )
                    if code:
                        event_id = self._insert_event(cur, code, row[3], None, None, None)
                        cur.execute(
                            "UPDATE sw_runtime.state SET last_event_id=%s WHERE singleton=1",
                            (event_id,),
                        )
                    return self._state(cur)
        finally:
            conn.close()

    def _insert_event(self, cur, code: str, tick: int, causation_id: int | None,
                      correlation_id: UUID | None, idempotency_key: str | None) -> int:
        cur.execute("SELECT event_type_id FROM sw_core.event_type WHERE event_code=%s", (code,))
        type_row = cur.fetchone()
        if type_row is None:
            raise KernelError(f"unknown event code: {code}")
        cur.execute(
            "INSERT INTO sw_core.simulation_event "
            "(event_type_id,occurred_at,world_tick,causation_event_id,correlation_id,idempotency_key) "
            "VALUES (%s,%s,%s,%s,%s,%s) RETURNING event_id",
            (type_row[0], datetime.now(timezone.utc), tick, causation_id, correlation_id, idempotency_key),
        )
        return cur.fetchone()[0]

    def append_event(self, event: Event) -> Event:
        conn = self._open()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT state,player_present,world_tick FROM sw_runtime.state "
                        "WHERE singleton=1 FOR UPDATE"
                    )
                    row = cur.fetchone()
                    if row is None:
                        raise KernelError("runtime singleton is missing")
                    if event.idempotency_key:
                        cur.execute(
                            "SELECT e.event_id,t.event_code,e.world_tick,e.causation_event_id,e.correlation_id,e.idempotency_key "
                            "FROM sw_core.simulation_event e JOIN sw_core.event_type t USING(event_type_id) "
                            "WHERE e.idempotency_key=%s",
                            (event.idempotency_key,),
                        )
                        prior = cur.fetchone()
                        if prior:
                            if prior[1] != event.code:
                                raise KernelError("idempotency key was already used for a different event")
                            return Event(prior[0], prior[1], prior[2], prior[2], prior[3], prior[4], prior[5])
                    if row[0] != 2 or not row[1]:
                        raise KernelError("world events require a running, player-present runtime")
                    if event.world_tick != row[2]:
                        raise KernelError("event tick must equal committed runtime tick")
                    event_id = self._insert_event(
                        cur, event.code, row[2], event.causation_id,
                        event.correlation_id, event.idempotency_key,
                    )
                    cur.execute("UPDATE sw_runtime.state SET last_event_id=%s WHERE singleton=1", (event_id,))
                    return replace(event, event_id=event_id)
        finally:
            conn.close()

    def append_tick(self, event: Event) -> RuntimeState:
        conn = self._open()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT state,player_present,world_tick FROM sw_runtime.state "
                        "WHERE singleton=1 FOR UPDATE"
                    )
                    row = cur.fetchone()
                    if row is None:
                        raise KernelError("runtime singleton is missing")
                    if event.idempotency_key:
                        cur.execute(
                            "SELECT t.event_code FROM sw_core.simulation_event e "
                            "JOIN sw_core.event_type t USING(event_type_id) WHERE e.idempotency_key=%s",
                            (event.idempotency_key,),
                        )
                        prior = cur.fetchone()
                        if prior:
                            if prior[0] != "CLOCK_ADVANCE":
                                raise KernelError("idempotency key was already used for a different event")
                            return self._state(cur)
                    if row[0] != 2 or not row[1]:
                        raise KernelError("world time is frozen unless player is present and runtime is running")
                    next_tick = row[2] + 1
                    if event.world_tick != next_tick:
                        raise KernelError("tick must advance exactly once")
                    cur.execute("UPDATE sw_runtime.state SET world_tick=%s WHERE singleton=1", (next_tick,))
                    event_id = self._insert_event(cur, "CLOCK_ADVANCE", next_tick, None, None, event.idempotency_key)
                    cur.execute("UPDATE sw_runtime.state SET last_event_id=%s WHERE singleton=1", (event_id,))
                    return self._state(cur)
        finally:
            conn.close()


class RuntimeKernel:
    def __init__(self, store: RuntimeStore):
        self.store = store

    def status(self) -> RuntimeState:
        return self.store.snapshot()

    def close_bootstrap(self) -> RuntimeState:
        return self.store.close_bootstrap()

    def transition(self, target: Lifecycle, *, player_present: bool = False) -> RuntimeState:
        return self.store.transition(target, player_present)

    def record(self, code: str, *, idempotency_key: str | None = None,
               causation_id: int | None = None, correlation_id: UUID | None = None) -> Event:
        state = self.store.snapshot()
        event = Event(0, code, state.world_tick, state.world_tick,
                      causation_id, correlation_id, idempotency_key)
        return self.store.append_event(event)

    def advance_tick(self, *, idempotency_key: str | None = None) -> RuntimeState:
        state = self.store.snapshot()
        event = Event(0, "CLOCK_ADVANCE", state.world_tick + 1,
                      state.world_tick + 1, idempotency_key=idempotency_key)
        return self.store.append_tick(event)
