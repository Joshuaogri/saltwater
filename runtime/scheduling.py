"""Canonical tick-based scheduling primitives for BP37-01.

No wall clock, calendar, timezone or tick-duration conversion exists here.
The runtime kernel owns clock advancement; this module owns schedule eligibility
and delegates actions exclusively to injected owner-domain handlers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable, Protocol
from uuid import UUID, uuid4

from runtime.kernel import Lifecycle, RuntimeKernel

_OWNER = re.compile(r"^[a-z][a-z0-9_]{1,47}$")


class SchedulingError(RuntimeError):
    """A schedule definition or lifecycle operation violates an invariant."""


@dataclass(frozen=True, slots=True)
class ScheduleDefinition:
    owner_domain: str
    subject_ref: str
    due_tick: int
    idempotency_key: str
    interval_ticks: int | None = None
    priority: int = 0
    expires_at_tick: int | None = None

    def validate(self, current_tick: int) -> None:
        if not isinstance(self.owner_domain, str) or not _OWNER.fullmatch(self.owner_domain):
            raise SchedulingError("invalid owner domain")
        if not isinstance(self.subject_ref, str) or not 1 <= len(self.subject_ref) <= 128:
            raise SchedulingError("invalid schedule subject reference")
        if type(self.due_tick) is not int or self.due_tick < current_tick:
            raise SchedulingError("due tick must not precede the committed world tick")
        if self.interval_ticks is not None and (
            type(self.interval_ticks) is not int or self.interval_ticks <= 0
        ):
            raise SchedulingError("interval must be a positive number of ticks")
        if type(self.priority) is not int or not -1000 <= self.priority <= 1000:
            raise SchedulingError("priority is outside the supported range")
        if self.expires_at_tick is not None and (
            type(self.expires_at_tick) is not int or self.expires_at_tick < self.due_tick
        ):
            raise SchedulingError("expiry must not precede due tick")
        if not isinstance(self.idempotency_key, str) or not 1 <= len(self.idempotency_key) <= 128:
            raise SchedulingError("invalid schedule idempotency key")


@dataclass(frozen=True, slots=True)
class DueSchedule:
    schedule_id: int
    owner_domain: str
    subject_ref: str
    due_tick: int
    interval_ticks: int | None
    priority: int
    attempt_count: int
    claim_token: UUID
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ScheduleExecutionResult:
    success: bool
    error_code: str | None = None
    retry_after_tick: int | None = None


class OwnerScheduleHandler(Protocol):
    def __call__(self, schedule: DueSchedule, *, world_tick: int) -> ScheduleExecutionResult: ...


class ScheduleStore(Protocol):
    def create(self, definition: ScheduleDefinition, current_tick: int) -> int: ...
    def claim_due(self, world_tick: int) -> DueSchedule | None: ...
    def finish(
        self, schedule: DueSchedule, result: ScheduleExecutionResult, world_tick: int
    ) -> bool: ...


class InMemoryScheduleStore:
    """Deterministic test adapter; production uses PostgresScheduleStore."""

    def __init__(self) -> None:
        self._rows: dict[int, dict[str, Any]] = {}
        self._keys: dict[str, int] = {}
        self._next_id = 1
        self._lock = RLock()

    def create(self, definition: ScheduleDefinition, current_tick: int) -> int:
        definition.validate(current_tick)
        with self._lock:
            prior_id = self._keys.get(definition.idempotency_key)
            if prior_id is not None:
                prior = self._rows[prior_id]["definition"]
                if prior != definition:
                    raise SchedulingError("schedule idempotency key conflicts with prior definition")
                return prior_id
            schedule_id = self._next_id
            self._next_id += 1
            self._keys[definition.idempotency_key] = schedule_id
            self._rows[schedule_id] = {
                "definition": definition, "status": "pending", "attempt_count": 0,
                "retry_after_tick": 0, "claim_token": None, "claimed_at_tick": None,
                "completed_at_tick": None, "last_error_code": None,
            }
            return schedule_id

    def claim_due(self, world_tick: int) -> DueSchedule | None:
        with self._lock:
            eligible = [
                (sid, row) for sid, row in self._rows.items()
                if row["status"] in {"pending", "failed"}
                and row["definition"].due_tick <= world_tick
                and row["retry_after_tick"] <= world_tick
                and (row["definition"].expires_at_tick is None
                     or row["definition"].expires_at_tick >= world_tick)
            ]
            if not eligible:
                for row in self._rows.values():
                    definition = row["definition"]
                    if (row["status"] in {"pending", "failed"}
                            and definition.expires_at_tick is not None
                            and definition.expires_at_tick < world_tick):
                        row["status"] = "expired"
                return None
            schedule_id, row = min(
                eligible,
                key=lambda pair: (
                    pair[1]["definition"].due_tick,
                    -pair[1]["definition"].priority,
                    pair[0],
                ),
            )
            token = uuid4()
            row["status"] = "claimed"
            row["claim_token"] = token
            row["claimed_at_tick"] = world_tick
            row["attempt_count"] += 1
            d = row["definition"]
            return DueSchedule(
                schedule_id, d.owner_domain, d.subject_ref, d.due_tick,
                d.interval_ticks, d.priority, row["attempt_count"], token,
                d.idempotency_key,
            )

    def finish(
        self, schedule: DueSchedule, result: ScheduleExecutionResult, world_tick: int
    ) -> bool:
        with self._lock:
            row = self._rows.get(schedule.schedule_id)
            if (row is None or row["status"] != "claimed"
                    or row["claim_token"] != schedule.claim_token):
                return False
            if result.success:
                if schedule.interval_ticks is None:
                    row["status"] = "completed"
                    row["completed_at_tick"] = world_tick
                else:
                    d = row["definition"]
                    row["definition"] = ScheduleDefinition(
                        d.owner_domain, d.subject_ref,
                        world_tick + d.interval_ticks, d.idempotency_key,
                        d.interval_ticks, d.priority, d.expires_at_tick,
                    )
                    row["status"] = "pending"
                    row["retry_after_tick"] = 0
                row["last_error_code"] = None
            else:
                if (not result.error_code or len(result.error_code) > 64
                        or result.retry_after_tick is None
                        or result.retry_after_tick < world_tick):
                    raise SchedulingError("failed handler requires error code and retry tick")
                row["status"] = "failed"
                row["retry_after_tick"] = result.retry_after_tick
                row["last_error_code"] = result.error_code
            row["claim_token"] = None
            row["claimed_at_tick"] = None
            return True

    def inspect(self, schedule_id: int) -> dict[str, Any]:
        with self._lock:
            row = self._rows[schedule_id]
            return dict(row)


class PostgresScheduleStore:
    """Thin adapter over the BP37-01 disposable/approved PostgreSQL functions."""

    def __init__(self, connect: Callable[[], Any]):
        self._connect = connect

    def create(self, definition: ScheduleDefinition, current_tick: int) -> int:
        definition.validate(current_tick)
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_runtime.create_schedule(%s,%s,%s,%s,%s,%s,%s)",
                        (definition.owner_domain, definition.subject_ref,
                         definition.due_tick, definition.interval_ticks,
                         definition.priority, definition.expires_at_tick,
                         definition.idempotency_key),
                    )
                    return cur.fetchone()[0]
        finally:
            conn.close()

    def claim_due(self, world_tick: int) -> DueSchedule | None:
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL re-reads and locks the authoritative runtime row; the
                    # argument is deliberately not trusted for eligibility.
                    cur.execute("SELECT * FROM sw_runtime.claim_due_schedule()")
                    row = cur.fetchone()
                    if row is None:
                        return None
                    return DueSchedule(*row)
        finally:
            conn.close()

    def finish(
        self, schedule: DueSchedule, result: ScheduleExecutionResult, world_tick: int
    ) -> bool:
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_runtime.finish_schedule(%s,%s,%s,%s,%s)",
                        (schedule.schedule_id, schedule.claim_token, result.success,
                         result.retry_after_tick, result.error_code),
                    )
                    return bool(cur.fetchone()[0])
        finally:
            conn.close()


class TickScheduler:
    """Clock-gated scheduler; due status never conveys domain action authority."""

    def __init__(
        self,
        kernel: RuntimeKernel,
        store: ScheduleStore,
        handlers: dict[str, OwnerScheduleHandler],
    ) -> None:
        self.kernel = kernel
        self.store = store
        self.handlers = dict(handlers)

    def register(self, definition: ScheduleDefinition) -> int:
        state = self.kernel.status()
        if state.lifecycle != Lifecycle.RUNNING or not state.player_present:
            raise SchedulingError("scheduling is frozen unless player is present and runtime is running")
        return self.store.create(definition, state.world_tick)

    def dispatch_one(self) -> bool:
        state = self.kernel.status()
        if state.lifecycle != Lifecycle.RUNNING or not state.player_present:
            return False
        schedule = self.store.claim_due(state.world_tick)
        if schedule is None:
            return False
        # Re-check immediately before handing work to its owner domain.
        state = self.kernel.status()
        if state.lifecycle != Lifecycle.RUNNING or not state.player_present:
            return False
        handler = self.handlers.get(schedule.owner_domain)
        if handler is None:
            result = ScheduleExecutionResult(
                False, error_code="owner_handler_missing",
                retry_after_tick=state.world_tick + 1,
            )
        else:
            try:
                result = handler(schedule, world_tick=state.world_tick)
                if not isinstance(result, ScheduleExecutionResult):
                    result = ScheduleExecutionResult(
                        False, error_code="invalid_handler_result",
                        retry_after_tick=state.world_tick + 1,
                    )
            except Exception:
                result = ScheduleExecutionResult(
                    False, error_code="owner_handler_error",
                    retry_after_tick=state.world_tick + 1,
                )
        # The store enforces the running/present gate again transactionally.
        return self.store.finish(schedule, result, self.kernel.status().world_tick)
