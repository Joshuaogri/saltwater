"""BP39-01 checkpoint and explicit event-claim recovery adapter.

This module never creates schema or connects to a production database. It calls
proposal 0008 functions through an injected psycopg-compatible connection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from uuid import UUID


class RecoveryError(RuntimeError):
    """A checkpoint or recovery operation violates its contract."""


@dataclass(frozen=True, slots=True)
class CheckpointSource:
    environment: str
    project: str
    branch: str
    database: str
    actor_ref: str
    approval_ref: str

    def validate(self) -> None:
        for name, value, limit in (
            ("environment", self.environment, 80), ("project", self.project, 120),
            ("branch", self.branch, 120), ("database", self.database, 120),
            ("actor reference", self.actor_ref, 200), ("approval reference", self.approval_ref, 200),
        ):
            if not isinstance(value, str) or not 1 <= len(value) <= limit:
                raise RecoveryError(f"invalid checkpoint {name}")


@dataclass(frozen=True, slots=True)
class ClaimReconciliation:
    event_id: int
    claim_token: UUID
    decision: str
    owner_domain: str
    owner_response_ref: str
    outcome_ref: str | None
    actor_ref: str
    approval_ref: str
    reason_code: str
    recovery_key: str
    checkpoint_id: UUID | None = None

    def validate(self) -> None:
        if type(self.event_id) is not int or self.event_id < 1:
            raise RecoveryError("invalid event ID")
        if not isinstance(self.claim_token, UUID):
            raise RecoveryError("claim token must be a UUID")
        if self.decision not in {"effect_committed", "effect_absent", "indeterminate"}:
            raise RecoveryError("unsupported owner reconciliation decision")
        if self.decision == "effect_committed":
            if not isinstance(self.outcome_ref, str) or not 1 <= len(self.outcome_ref) <= 200:
                raise RecoveryError("committed effect requires a durable outcome reference")
        elif self.outcome_ref is not None:
            raise RecoveryError("only a committed effect may include an outcome reference")
        for name, value, limit in (
            ("owner domain", self.owner_domain, 48), ("owner response reference", self.owner_response_ref, 200),
            ("actor reference", self.actor_ref, 200), ("approval reference", self.approval_ref, 200),
            ("reason code", self.reason_code, 64), ("recovery key", self.recovery_key, 128),
        ):
            if not isinstance(value, str) or not 1 <= len(value) <= limit:
                raise RecoveryError(f"invalid {name}")


class PostgresRecoveryStore:
    """Small adapter; connection target is supplied by the caller, never inferred."""

    def __init__(self, connect: Callable[[], Any]):
        self._connect = connect

    def capture_checkpoint(self, source: CheckpointSource) -> UUID:
        source.validate()
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                    cur.execute(
                        "SELECT sw_runtime.capture_checkpoint_manifest(%s,%s,%s,%s,%s,%s)",
                        (source.environment, source.project, source.branch,
                         source.database, source.actor_ref, source.approval_ref),
                    )
                    return cur.fetchone()[0]
        finally:
            conn.close()

    def validate_checkpoint(self, checkpoint_id: UUID) -> dict:
        if not isinstance(checkpoint_id, UUID):
            raise RecoveryError("checkpoint ID must be a UUID")
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT sw_runtime.validate_checkpoint_manifest(%s)", (checkpoint_id,))
                    result = cur.fetchone()[0]
                    if isinstance(result, str):
                        import json
                        result = json.loads(result)
                    return result
        finally:
            conn.close()

    def begin_claim_recovery(self, actor_ref: str, approval_ref: str) -> int:
        if not all(isinstance(x, str) and 1 <= len(x) <= 200 for x in (actor_ref, approval_ref)):
            raise RecoveryError("recovery actor and approval references are required")
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT sw_runtime.begin_event_claim_recovery(%s,%s)", (actor_ref, approval_ref))
                    return cur.fetchone()[0]
        finally:
            conn.close()

    def reconcile_claim(self, decision: ClaimReconciliation) -> str:
        decision.validate()
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_runtime.reconcile_event_claim(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (decision.event_id, decision.claim_token, decision.decision,
                         decision.owner_domain, decision.owner_response_ref, decision.outcome_ref,
                         decision.actor_ref, decision.approval_ref, decision.reason_code,
                         decision.recovery_key, decision.checkpoint_id),
                    )
                    return cur.fetchone()[0]
        finally:
            conn.close()

    def resolve_quarantined_claim(self, decision: ClaimReconciliation) -> str:
        decision.validate()
        if decision.decision == "indeterminate":
            raise RecoveryError("quarantine resolution requires a conclusive owner decision")
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_runtime.resolve_quarantined_event_claim(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (decision.event_id, decision.claim_token, decision.decision,
                         decision.owner_domain, decision.owner_response_ref, decision.outcome_ref,
                         decision.actor_ref, decision.approval_ref, decision.reason_code,
                         decision.recovery_key, decision.checkpoint_id),
                    )
                    return cur.fetchone()[0]
        finally:
            conn.close()

    def finish_claim_recovery(self) -> bool:
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT sw_runtime.finish_event_claim_recovery()")
                    return bool(cur.fetchone()[0])
        finally:
            conn.close()
