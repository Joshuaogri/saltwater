"""Fail-closed actor authorization and central hidden-truth reveal gate.

The verifier and audit sink are deployment adapters. No identity provider,
credential format, secret store or player account is assumed by this module.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class PrincipalKind(StrEnum):
    PLAYER = "player"
    OFFICER = "officer"
    ADMINISTRATOR = "administrator"
    OPERATOR = "operator"
    DEVELOPER = "developer"
    SERVICE = "service"
    SYSTEM = "system"
    TEST = "test"


class PrincipalStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    DISABLED = "disabled"


class SessionStatus(StrEnum):
    ACTIVE = "active"
    RESTRICTED = "restricted"
    EXPIRED = "expired"
    REVOKED = "revoked"
    TERMINATED = "terminated"


class Effect(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class VerifiedSession:
    session_id: UUID
    principal_id: UUID
    principal_kind: PrincipalKind
    principal_status: PrincipalStatus
    session_status: SessionStatus
    issued_at: datetime
    expires_at: datetime
    roles: frozenset[str] = frozenset()
    active_person_id: int | None = None
    authentication_strength: str = "standard"
    policy_version: str = "1"
    correlation_id: UUID | None = None


class SessionVerifier(Protocol):
    """Trusted adapter verifies opaque credentials and revocation state."""

    def verify(self, credential: str) -> VerifiedSession | None: ...


@dataclass(frozen=True, slots=True)
class Grant:
    action: str
    resource_pattern: str
    purpose: str
    effect: Effect
    principal_id: UUID | None = None
    principal_kind: PrincipalKind | None = None
    role: str | None = None
    expires_at: datetime | None = None

    def __post_init__(self):
        if not self.action or not self.resource_pattern or not self.purpose:
            raise ValueError("grant action, resource and purpose are required")
        if self.principal_id is None and self.principal_kind is None and self.role is None:
            raise ValueError("grant must identify a principal, principal kind or role")


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    allowed: bool
    reason: str
    principal_id: UUID | None
    session_id: UUID | None
    action: str
    resource: str
    purpose: str
    policy_version: str
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class SecurityAuditRecord:
    principal_id: UUID | None
    session_id: UUID | None
    action: str
    resource: str
    purpose: str
    allowed: bool
    reason: str
    policy_version: str
    decided_at: datetime


class AuditSink(Protocol):
    def append(self, record: SecurityAuditRecord) -> None: ...


@dataclass
class InMemoryAuditSink:
    """Test-only sink. Production requires a durable append-only implementation."""

    records: list[SecurityAuditRecord] = field(default_factory=list)

    def append(self, record: SecurityAuditRecord) -> None:
        self.records.append(record)


def _resource_matches(pattern: str, resource: str) -> bool:
    if pattern == resource:
        return True
    if pattern.endswith("*"):
        return resource.startswith(pattern[:-1])
    return False


class AuthorizationService:
    """Default-deny authorization with explicit-deny precedence and audit."""

    def __init__(
        self,
        verifier: SessionVerifier,
        audit_sink: AuditSink,
        grants: tuple[Grant, ...] = (),
        *,
        policy_version: str = "1",
    ):
        self._verifier = verifier
        self._audit = audit_sink
        self._grants = grants
        self._policy_version = policy_version

    def decide(
        self,
        credential: str,
        *,
        action: str,
        resource: str,
        purpose: str,
        now: datetime | None = None,
        reveal_trigger: str | None = None,
    ) -> AuthorizationDecision:
        at = now or datetime.now(timezone.utc)
        session = self._verifier.verify(credential) if credential else None
        reason = "default_deny"
        allowed = False

        if not action or not resource or not purpose:
            reason = "incomplete_request"
        elif session is None:
            reason = "invalid_or_unverifiable_session"
        elif session.principal_status != PrincipalStatus.ACTIVE:
            reason = "principal_not_active"
        elif session.session_status != SessionStatus.ACTIVE:
            reason = "session_not_active"
        elif at.tzinfo is None or session.expires_at.tzinfo is None or session.issued_at.tzinfo is None:
            reason = "invalid_security_time"
        elif at < session.issued_at or at >= session.expires_at:
            reason = "session_outside_validity_window"
        elif action == "reveal_hidden_truth" and (
            session.principal_kind != PrincipalKind.PLAYER or reveal_trigger != "bingo"
        ):
            reason = "hidden_truth_requires_exact_player_trigger"
        else:
            matching = [
                grant for grant in self._grants
                if grant.action == action
                and _resource_matches(grant.resource_pattern, resource)
                and grant.purpose == purpose
                and (grant.expires_at is None or (grant.expires_at.tzinfo is not None and at < grant.expires_at))
                and (grant.principal_id is None or grant.principal_id == session.principal_id)
                and (grant.principal_kind is None or grant.principal_kind == session.principal_kind)
                and (grant.role is None or grant.role in session.roles)
            ]
            if any(grant.effect == Effect.DENY for grant in matching):
                reason = "explicit_deny"
            elif any(grant.effect == Effect.ALLOW for grant in matching):
                allowed = True
                reason = "explicit_allow"
            else:
                reason = "no_matching_grant"

        decision = AuthorizationDecision(
            allowed=allowed,
            reason=reason,
            principal_id=session.principal_id if session else None,
            session_id=session.session_id if session else None,
            action=action,
            resource=resource,
            purpose=purpose,
            policy_version=session.policy_version if session else self._policy_version,
            decided_at=at,
        )
        audit = SecurityAuditRecord(
            principal_id=decision.principal_id,
            session_id=decision.session_id,
            action=action,
            resource=resource,
            purpose=purpose,
            allowed=allowed,
            reason=reason,
            policy_version=decision.policy_version,
            decided_at=at,
        )
        try:
            self._audit.append(audit)
        except Exception:
            # A protected action must fail closed if its audit cannot be recorded.
            return AuthorizationDecision(
                allowed=False,
                reason="audit_unavailable",
                principal_id=decision.principal_id,
                session_id=decision.session_id,
                action=action,
                resource=resource,
                purpose=purpose,
                policy_version=decision.policy_version,
                decided_at=at,
            )
        return decision
