"""BP35-01 deterministic event intake and dispatch.

The engine owns eligibility and dispatch, never domain truth. Owner handlers
must make their own effects idempotent using the stable event/idempotency key.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from threading import RLock
from typing import Callable, Protocol
from uuid import UUID, uuid4

from runtime.kernel import Lifecycle, RuntimeKernel

_CODE = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
_OWNER = re.compile(r"^[a-z][a-z0-9_]{1,47}$")
_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$")
_ERROR = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class EventEngineError(RuntimeError):
    """An event definition or dispatch operation violates an engine invariant."""


@dataclass(frozen=True, slots=True)
class EventWorkDefinition:
    event_code: str
    owner_domain: str
    handler_key: str
    handler_version: int
    schema_version: int
    due_tick: int
    idempotency_key: str
    priority: int = 0
    actor_ref: str | None = None
    source_division: str = "system"
    source_ref: str | None = None
    causation_event_id: int | None = None
    correlation_id: UUID | None = None
    visibility_class: str = "internal"
    prerequisite_event_ids: tuple[int, ...] = ()
    max_attempts: int = 3

    def validate(self, current_tick: int) -> None:
        if not isinstance(self.event_code, str) or not _CODE.fullmatch(self.event_code):
            raise EventEngineError("invalid event code")
        if not isinstance(self.owner_domain, str) or not _OWNER.fullmatch(self.owner_domain):
            raise EventEngineError("invalid owner domain")
        if not isinstance(self.handler_key, str) or not _KEY.fullmatch(self.handler_key):
            raise EventEngineError("invalid handler key")
        for name, value in (("handler version", self.handler_version),
                            ("schema version", self.schema_version)):
            if type(value) is not int or value < 1:
                raise EventEngineError(f"invalid {name}")
        if type(self.due_tick) is not int or self.due_tick < current_tick:
            raise EventEngineError("due tick precedes committed world tick")
        if not isinstance(self.idempotency_key, str) or not _KEY.fullmatch(self.idempotency_key):
            raise EventEngineError("invalid idempotency key")
        if type(self.priority) is not int or not -1000 <= self.priority <= 1000:
            raise EventEngineError("priority outside supported range")
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 100:
            raise EventEngineError("max attempts outside supported range")
        if not isinstance(self.source_division, str) or not _OWNER.fullmatch(self.source_division):
            raise EventEngineError("invalid source division")
        if not isinstance(self.visibility_class, str) or not _OWNER.fullmatch(self.visibility_class):
            raise EventEngineError("invalid visibility class")
        for name, value in (("actor reference", self.actor_ref), ("source reference", self.source_ref)):
            if value is not None and (not isinstance(value, str) or not 1 <= len(value) <= 200):
                raise EventEngineError(f"invalid {name}")
        if self.causation_event_id is not None and (
            type(self.causation_event_id) is not int or self.causation_event_id < 1
        ):
            raise EventEngineError("invalid causation event ID")
        if (not isinstance(self.prerequisite_event_ids, tuple)
                or any(type(x) is not int or x < 1 for x in self.prerequisite_event_ids)
                or len(set(self.prerequisite_event_ids)) != len(self.prerequisite_event_ids)):
            raise EventEngineError("invalid or duplicate causal prerequisites")


@dataclass(frozen=True, slots=True)
class EventWork:
    event_id: int
    event_code: str
    owner_domain: str
    handler_key: str
    handler_version: int
    schema_version: int
    due_tick: int
    priority: int
    attempt_count: int
    claim_token: UUID
    idempotency_key: str
    actor_ref: str | None
    source_division: str
    source_ref: str | None
    causation_event_id: int | None
    correlation_id: UUID | None
    visibility_class: str
    prerequisite_event_ids: tuple[int, ...]
    max_attempts: int


@dataclass(frozen=True, slots=True)
class HandlerReceipt:
    success: bool
    outcome_ref: str | None = None
    error_code: str | None = None
    retry_after_tick: int | None = None
    retryable: bool = True


@dataclass(frozen=True, slots=True)
class HandlerSpec:
    owner_domain: str
    handler_key: str
    handler_version: int
    event_codes: frozenset[str]
    schema_versions: frozenset[int]
    permission_action: str
    handle: Callable[[EventWork, int], HandlerReceipt]


@dataclass(frozen=True, slots=True)
class DispatchResult:
    event_id: int
    status: str


class EventWorkStore(Protocol):
    def submit(self, definition: EventWorkDefinition, current_tick: int) -> int: ...
    def claim_due(self, world_tick: int) -> EventWork | None: ...
    def finish(self, work: EventWork, receipt: HandlerReceipt, world_tick: int) -> str: ...


class InMemoryEventWorkStore:
    """Deterministic test store; authoritative sessions use PostgresEventWorkStore."""

    def __init__(self) -> None:
        self._rows: dict[int, dict] = {}
        self._keys: dict[str, int] = {}
        self._next_id = 1
        self._attempts: list[dict] = []
        self._lock = RLock()

    def submit(self, definition: EventWorkDefinition, current_tick: int) -> int:
        definition.validate(current_tick)
        with self._lock:
            prior_id = self._keys.get(definition.idempotency_key)
            if prior_id is not None:
                if self._rows[prior_id]["definition"] != definition:
                    raise EventEngineError("event idempotency key conflicts with prior definition")
                return prior_id
            event_id = self._next_id
            for parent_id in definition.prerequisite_event_ids:
                if parent_id == event_id or parent_id not in self._rows:
                    raise EventEngineError("causal prerequisite is missing or self-referential")
            if definition.causation_event_id == event_id:
                raise EventEngineError("event cannot cause itself")
            self._next_id += 1
            self._keys[definition.idempotency_key] = event_id
            self._rows[event_id] = {
                "definition": definition, "status": "pending", "attempt_count": 0,
                "retry_after_tick": 0, "claim_token": None, "outcome_ref": None,
                "error_code": None,
            }
            return event_id

    def claim_due(self, world_tick: int) -> EventWork | None:
        with self._lock:
            eligible = []
            for event_id, row in self._rows.items():
                d = row["definition"]
                if (row["status"] not in {"pending", "failed"}
                        or d.due_tick > world_tick or row["retry_after_tick"] > world_tick):
                    continue
                if any(self._rows[p]["status"] != "completed" for p in d.prerequisite_event_ids):
                    continue
                eligible.append((event_id, row))
            if not eligible:
                return None
            event_id, row = min(
                eligible,
                key=lambda item: (item[1]["definition"].due_tick,
                                  -item[1]["definition"].priority, item[0]),
            )
            token = uuid4()
            row["status"] = "claimed"
            row["claim_token"] = token
            row["attempt_count"] += 1
            d = row["definition"]
            self._attempts.append({"event_id": event_id, "attempt": row["attempt_count"],
                                   "status": "claimed", "tick": world_tick})
            return EventWork(
                event_id, d.event_code, d.owner_domain, d.handler_key,
                d.handler_version, d.schema_version, d.due_tick, d.priority,
                row["attempt_count"], token, d.idempotency_key, d.actor_ref,
                d.source_division, d.source_ref, d.causation_event_id,
                d.correlation_id, d.visibility_class, d.prerequisite_event_ids,
                d.max_attempts,
            )

    def finish(self, work: EventWork, receipt: HandlerReceipt, world_tick: int) -> str:
        with self._lock:
            row = self._rows.get(work.event_id)
            if (row is None or row["status"] != "claimed"
                    or row["claim_token"] != work.claim_token):
                raise EventEngineError("claim token is stale or does not own event work")
            if receipt.success:
                if (not isinstance(receipt.outcome_ref, str)
                        or not 1 <= len(receipt.outcome_ref) <= 200
                        or receipt.error_code is not None
                        or receipt.retry_after_tick is not None):
                    raise EventEngineError("successful dispatch requires an outcome reference only")
                status = "completed"
                row["outcome_ref"] = receipt.outcome_ref
                row["error_code"] = None
            else:
                if (not isinstance(receipt.error_code, str)
                        or not _ERROR.fullmatch(receipt.error_code)
                        or type(receipt.retry_after_tick) is not int
                        or receipt.retry_after_tick < world_tick):
                    raise EventEngineError("failed handler requires a safe error code and retry tick")
                status = ("failed" if receipt.retryable
                          and row["attempt_count"] < work.max_attempts else "quarantined")
                row["error_code"] = receipt.error_code
            row["status"] = status
            row["claim_token"] = None
            self._attempts.append({
                "event_id": work.event_id, "attempt": work.attempt_count,
                "status": status, "tick": world_tick,
                "error_code": row["error_code"], "outcome_ref": row["outcome_ref"],
            })
            if status == "failed":
                row["retry_after_tick"] = receipt.retry_after_tick
            return status

    def inspect(self, event_id: int) -> dict:
        with self._lock:
            row = self._rows[event_id]
            return {"event_id": event_id, "status": row["status"],
                    "attempt_count": row["attempt_count"], "error_code": row["error_code"],
                    "outcome_ref": row["outcome_ref"]}

    def attempts(self, event_id: int) -> tuple[dict, ...]:
        with self._lock:
            return tuple(dict(x) for x in self._attempts if x["event_id"] == event_id)


class PostgresEventWorkStore:
    """PostgreSQL adapter for proposal 0007; no schema creation or migration."""

    def __init__(self, connect: Callable[[], object]):
        self._connect = connect

    def submit(self, definition: EventWorkDefinition, current_tick: int) -> int:
        definition.validate(current_tick)
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_runtime.submit_event_work(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (definition.event_code, definition.owner_domain, definition.handler_key,
                         definition.handler_version, definition.schema_version, definition.due_tick,
                         definition.priority, definition.idempotency_key, definition.actor_ref,
                         definition.source_division, definition.source_ref,
                         definition.causation_event_id, definition.correlation_id,
                         definition.visibility_class, definition.max_attempts),
                    )
                    event_id = cur.fetchone()[0]
                    for parent_id in definition.prerequisite_event_ids:
                        cur.execute("SELECT sw_runtime.add_event_prerequisite(%s,%s)",
                                    (event_id, parent_id))
                    return event_id
        finally:
            conn.close()

    def claim_due(self, world_tick: int) -> EventWork | None:
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM sw_runtime.claim_due_event_work()")
                    row = cur.fetchone()
                    return EventWork(*row) if row else None
        finally:
            conn.close()

    def finish(self, work: EventWork, receipt: HandlerReceipt, world_tick: int) -> str:
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_runtime.finish_event_work(%s,%s,%s,%s,%s,%s,%s)",
                        (work.event_id, work.claim_token, receipt.success,
                         receipt.outcome_ref, receipt.error_code,
                         receipt.retry_after_tick, receipt.retryable),
                    )
                    return cur.fetchone()[0]
        finally:
            conn.close()


class EventEngine:
    """Pause-safe dispatcher with owner-domain and authorization boundaries."""

    def __init__(
        self, kernel: RuntimeKernel, store: EventWorkStore,
        authorizer: Callable[[EventWork, HandlerSpec], bool],
    ) -> None:
        if not callable(authorizer):
            raise EventEngineError("an explicit event authorizer is required")
        self.kernel = kernel
        self.store = store
        self.authorizer = authorizer
        self._handlers: dict[str, HandlerSpec] = {}

    def register(self, spec: HandlerSpec) -> None:
        if (not _OWNER.fullmatch(spec.owner_domain)
                or not _KEY.fullmatch(spec.handler_key)
                or type(spec.handler_version) is not int or spec.handler_version < 1
                or not spec.event_codes or any(not _CODE.fullmatch(x) for x in spec.event_codes)
                or not spec.schema_versions or any(type(x) is not int or x < 1 for x in spec.schema_versions)
                or not isinstance(spec.permission_action, str) or not 1 <= len(spec.permission_action) <= 120
                or not callable(spec.handle)):
            raise EventEngineError("invalid owner handler contract")
        if spec.handler_key in self._handlers:
            raise EventEngineError("handler key is already registered")
        self._handlers[spec.handler_key] = spec

    def submit(self, definition: EventWorkDefinition) -> int:
        state = self.kernel.status()
        if state.lifecycle != Lifecycle.RUNNING or not state.player_present:
            raise EventEngineError("event intake requires running player-present runtime")
        spec = self._handlers.get(definition.handler_key)
        if spec is None:
            raise EventEngineError("unregistered event handler")
        if (spec.owner_domain != definition.owner_domain
                or spec.handler_version != definition.handler_version
                or definition.event_code not in spec.event_codes
                or definition.schema_version not in spec.schema_versions):
            raise EventEngineError("event does not match registered owner handler contract")
        return self.store.submit(definition, state.world_tick)

    def dispatch_one(self) -> DispatchResult | None:
        state = self.kernel.status()
        if state.lifecycle != Lifecycle.RUNNING or not state.player_present:
            return None
        work = self.store.claim_due(state.world_tick)
        if work is None:
            return None
        state = self.kernel.status()
        if state.lifecycle != Lifecycle.RUNNING or not state.player_present:
            return None
        spec = self._handlers.get(work.handler_key)
        if spec is None or (spec.owner_domain != work.owner_domain
                or spec.handler_version != work.handler_version
                or work.event_code not in spec.event_codes
                or work.schema_version not in spec.schema_versions):
            receipt = HandlerReceipt(False, error_code="handler_contract_invalid",
                                     retry_after_tick=state.world_tick, retryable=False)
        else:
            try:
                allowed = self.authorizer(work, spec)
            except Exception:
                allowed = False
            if allowed is not True:
                receipt = HandlerReceipt(False, error_code="permission_denied",
                                         retry_after_tick=state.world_tick, retryable=False)
            else:
                try:
                    receipt = spec.handle(work, state.world_tick)
                except Exception:
                    receipt = HandlerReceipt(False, error_code="owner_handler_error",
                                             retry_after_tick=state.world_tick + 1)
                if not isinstance(receipt, HandlerReceipt) or type(receipt.success) is not bool:
                    receipt = HandlerReceipt(False, error_code="invalid_handler_result",
                                             retry_after_tick=state.world_tick, retryable=False)
                elif receipt.success and (
                    not isinstance(receipt.outcome_ref, str)
                    or not 1 <= len(receipt.outcome_ref) <= 200
                    or receipt.error_code is not None
                    or receipt.retry_after_tick is not None
                ):
                    receipt = HandlerReceipt(False, error_code="invalid_handler_result",
                                             retry_after_tick=state.world_tick, retryable=False)
                elif not receipt.success and (
                    not isinstance(receipt.error_code, str)
                    or not _ERROR.fullmatch(receipt.error_code)
                    or type(receipt.retry_after_tick) is not int
                    or receipt.retry_after_tick < state.world_tick
                    or type(receipt.retryable) is not bool
                ):
                    receipt = HandlerReceipt(False, error_code="invalid_handler_result",
                                             retry_after_tick=state.world_tick, retryable=False)
        final_state = self.kernel.status()
        if final_state.lifecycle != Lifecycle.RUNNING or not final_state.player_present:
            return None
        status = self.store.finish(work, receipt, final_state.world_tick)
        return DispatchResult(work.event_id, status)
