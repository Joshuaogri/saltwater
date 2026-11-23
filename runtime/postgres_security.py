"""PostgreSQL-backed game session verification and durable authorization audit."""
from __future__ import annotations

import hashlib
from typing import Callable
from uuid import UUID

from runtime.security import (
    AuditSink,
    PrincipalKind,
    PrincipalStatus,
    SecurityAuditRecord,
    SessionStatus,
    VerifiedSession,
)


class PostgresSessionVerifier:
    """Resolve an opaque high-entropy game token to a persisted actor session.

    Only SHA-256(token) is queried/stored. The raw token is never sent to SQL.
    The caller supplies a connection factory; no provider or secret is assumed.
    """

    def __init__(self, connect: Callable):
        self._connect = connect

    def verify(self, credential: str) -> VerifiedSession | None:
        if not credential:
            return None
        digest = hashlib.sha256(credential.encode("utf-8")).digest()
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.session_id, p.principal_id, p.principal_kind,
                           p.status, s.status, s.issued_at, s.expires_at,
                           s.active_person_id, s.authentication_strength,
                           s.policy_version, s.correlation_id, pv.active
                    FROM sw_auth.session s
                    JOIN sw_auth.principal p ON p.principal_id=s.principal_id
                    JOIN sw_auth.policy_version pv ON pv.policy_version=s.policy_version
                    WHERE s.credential_digest=%s
                    """,
                    (digest,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                (session_id, principal_id, principal_kind, principal_status,
                 session_status, issued_at, expires_at, active_person_id,
                 authentication_strength, policy_version, correlation_id,
                 policy_active) = row
                cur.execute(
                    """
                    SELECT role_code FROM sw_auth.principal_role
                    WHERE principal_id=%s AND revoked_at IS NULL
                    ORDER BY role_code
                    """,
                    (principal_id,),
                )
                roles = frozenset(item[0] for item in cur.fetchall())

        # A session minted under an inactive policy is restricted until renewed.
        resolved_status = SessionStatus(session_status)
        if not policy_active and resolved_status == SessionStatus.ACTIVE:
            resolved_status = SessionStatus.RESTRICTED
        return VerifiedSession(
            session_id=UUID(str(session_id)),
            principal_id=UUID(str(principal_id)),
            principal_kind=PrincipalKind(principal_kind),
            principal_status=PrincipalStatus(principal_status),
            session_status=resolved_status,
            issued_at=issued_at,
            expires_at=expires_at,
            roles=roles,
            active_person_id=active_person_id,
            authentication_strength=authentication_strength,
            policy_version=policy_version,
            correlation_id=UUID(str(correlation_id)) if correlation_id else None,
        )


class PostgresAuditSink(AuditSink):
    """Durable append-only authorization audit adapter."""

    def __init__(self, connect: Callable):
        self._connect = connect

    def append(self, record: SecurityAuditRecord) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sw_auth.audit
                      (decided_at, principal_id, session_id, action, resource,
                       purpose, allowed, reason, policy_version)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        record.decided_at, record.principal_id, record.session_id,
                        record.action, record.resource, record.purpose,
                        record.allowed, record.reason, record.policy_version,
                    ),
                )
