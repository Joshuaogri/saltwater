"""Game-native PostgreSQL session issuance and revocation.

Opaque credentials are returned once to the trusted caller; only SHA-256 digests
are persisted. This module does not expose HTTP routes or write production data.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class IssuedGameSession:
    session_id: UUID
    principal_id: UUID
    credential: str
    issued_at: datetime
    expires_at: datetime
    policy_version: str


class PostgresSessionLifecycle:
    """Issue and revoke game sessions against the active policy and principals."""

    def __init__(self, connect: Callable):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect

    def issue(
        self,
        principal_id: UUID,
        *,
        lifetime: timedelta = timedelta(hours=12),
        active_person_id: int | None = None,
        authentication_strength: str = "standard",
        now: datetime | None = None,
    ) -> IssuedGameSession:
        if not isinstance(principal_id, UUID):
            raise TypeError("principal_id must be a UUID")
        if not isinstance(lifetime, timedelta) or lifetime <= timedelta(0):
            raise ValueError("lifetime must be a positive timedelta")
        if authentication_strength not in {"standard", "strong", "recovery"}:
            raise ValueError("unsupported authentication strength")
        issued_at = now or datetime.now(timezone.utc)
        if issued_at.tzinfo is None or issued_at.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        expires_at = issued_at + lifetime
        credential = secrets.token_urlsafe(32)
        digest = hashlib.sha256(credential.encode("utf-8")).digest()
        session_id = uuid4()
        correlation_id = uuid4()

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT status FROM sw_auth.principal WHERE principal_id=%s FOR SHARE",
                    (principal_id,),
                )
                principal = cur.fetchone()
                if principal is None or principal[0] != "active":
                    raise PermissionError("principal is missing or not active")
                cur.execute(
                    "SELECT policy_version FROM sw_auth.policy_version WHERE active=true FOR SHARE"
                )
                policy = cur.fetchone()
                if policy is None:
                    raise RuntimeError("no active authorization policy")
                policy_version = policy[0]
                cur.execute(
                    """
                    INSERT INTO sw_auth.session
                      (session_id,principal_id,credential_digest,status,issued_at,
                       expires_at,active_person_id,authentication_strength,
                       policy_version,correlation_id)
                    VALUES (%s,%s,%s,'active',%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        session_id, principal_id, digest, issued_at, expires_at,
                        active_person_id, authentication_strength, policy_version,
                        correlation_id,
                    ),
                )
        return IssuedGameSession(
            session_id=session_id,
            principal_id=principal_id,
            credential=credential,
            issued_at=issued_at,
            expires_at=expires_at,
            policy_version=policy_version,
        )

    def revoke(
        self,
        session_id: UUID,
        *,
        principal_id: UUID | None = None,
        now: datetime | None = None,
    ) -> bool:
        if not isinstance(session_id, UUID):
            raise TypeError("session_id must be a UUID")
        if principal_id is not None and not isinstance(principal_id, UUID):
            raise TypeError("principal_id must be a UUID when supplied")
        revoked_at = now or datetime.now(timezone.utc)
        if revoked_at.tzinfo is None or revoked_at.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sw_auth.session
                    SET status='revoked', revoked_at=%s
                    WHERE session_id=%s
                      AND status IN ('active','restricted')
                      AND (%s::uuid IS NULL OR principal_id=%s)
                    RETURNING session_id
                    """,
                    (revoked_at, session_id, principal_id, principal_id),
                )
                return cur.fetchone() is not None
