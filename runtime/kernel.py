"""Deterministic shared runtime kernel contract for Saltwater.

This reference implementation is deliberately storage-adapter neutral. The
in-memory adapter exists only for unit tests; production activation requires a
transactional PostgreSQL adapter and authenticated player-session provider.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from threading import RLock
from typing import Protocol
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


class KernelError(RuntimeError):
    """A requested operation violates a runtime invariant."""


@dataclass(frozen=True, slots=True)
class Event:
    event_id: UUID
    code: str
    world_tick: int
    occurred_at_tick: int
    causation_id: UUID | None = None
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
    last_event_id: UUID | None = None


class RuntimeStore(Protocol):
    """Atomic persistence boundary implemented by the future PostgreSQL adapter."""

    def snapshot(self) -> RuntimeState: ...
    def transition(self, target: Lifecycle, player_present: bool) -> RuntimeState: ...
    def append_tick(self, event: Event) -> RuntimeState: ...
    def append_event(self, event: Event) -> Event: ...
    def close_bootstrap(self) -> RuntimeState: ...


@dataclass
class InMemoryRuntimeStore:
    """Test-only store; it is not a production persistence implementation."""

    state: RuntimeState = field(default_factory=RuntimeState)
    events: list[Event] = field(default_factory=list)
    idempotency: dict[str, UUID] = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock, repr=False)

    def snapshot(self) -> RuntimeState:
        with self._lock:
            return RuntimeState(**vars(self.state))

    def close_bootstrap(self) -> RuntimeState:
        with self._lock:
            if not self.state.bootstrap_open:
                return self.snapshot()
            self.state.bootstrap_open = False
            return self.snapshot()

    def transition(self, target: Lifecycle, player_present: bool) -> RuntimeState:
        with self._lock:
            old = self.state.lifecycle
            if target != old and target not in TRANSITIONS[old]:
                raise KernelError(f"invalid lifecycle transition: {old} -> {target}")
            if target == Lifecycle.RUNNING and (self.state.bootstrap_open or not player_present):
                raise KernelError("runtime requires closed bootstrap and a present player")
            if target == Lifecycle.STOPPED and player_present:
                raise KernelError("stopped runtime cannot have a present player")
            self.state.lifecycle = target
            self.state.player_present = player_present
            return self.snapshot()

    def append_event(self, event: Event) -> Event:
        with self._lock:
            if event.idempotency_key and event.idempotency_key in self.idempotency:
                raise KernelError("duplicate idempotency key")
            if event.world_tick != self.state.world_tick:
                raise KernelError("event tick must equal committed runtime tick")
            if self.state.lifecycle != Lifecycle.RUNNING or not self.state.player_present:
                raise KernelError("world events require a running, player-present runtime")
            if event.causation_id and event.causation_id not in {e.event_id for e in self.events}:
                raise KernelError("causation event does not exist")
            self.events.append(event)
            if event.idempotency_key:
                self.idempotency[event.idempotency_key] = event.event_id
            self.state.last_event_id = event.event_id
            return event

    def append_tick(self, event: Event) -> RuntimeState:
        with self._lock:
            if self.state.lifecycle != Lifecycle.RUNNING or not self.state.player_present:
                raise KernelError("world time is frozen unless player is present and runtime is running")
            if event.world_tick != self.state.world_tick + 1:
                raise KernelError("tick must advance exactly once")
            if event.idempotency_key and event.idempotency_key in self.idempotency:
                raise KernelError("duplicate idempotency key")
            self.state.world_tick += 1
            self.events.append(event)
            if event.idempotency_key:
                self.idempotency[event.idempotency_key] = event.event_id
            self.state.last_event_id = event.event_id
            return self.snapshot()


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
               causation_id: UUID | None = None, correlation_id: UUID | None = None) -> Event:
        state = self.store.snapshot()
        event = Event(uuid4(), code, state.world_tick, state.world_tick,
                      causation_id, correlation_id, idempotency_key)
        return self.store.append_event(event)

    def advance_tick(self, *, idempotency_key: str | None = None) -> RuntimeState:
        state = self.store.snapshot()
        event = Event(uuid4(), "CLOCK_ADVANCE", state.world_tick + 1,
                      state.world_tick + 1, idempotency_key=idempotency_key)
        return self.store.append_tick(event)
