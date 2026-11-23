"""Atomic accepted-recruit player identity and session activation (PKG-004)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable
from uuid import UUID

from runtime.postgres_sessions import IssuedGameSession, PostgresSessionLifecycle


class PlayerActivationError(RuntimeError):
    """Accepted-player identity activation failed closed."""


@dataclass(frozen=True, slots=True)
class ActivatedPlayer:
    player_id: UUID
    principal_id: UUID
    person_id: int
    session: IssuedGameSession


class PostgresPlayerActivationService:
    """Bind a resolved player principal to an accepted recruit and issue a session.

    The identity-binding SQL function and session insert execute on one shared
    connection/transaction. Any error rolls back both changes.
    """

    def __init__(self, connect: Callable, sessions: PostgresSessionLifecycle | None = None):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect
        self._sessions = sessions or PostgresSessionLifecycle(connect)

    def activate(
        self,
        principal_id: UUID,
        player_id: UUID,
        *,
        lifetime: timedelta = timedelta(hours=12),
        authentication_strength: str = "standard",
        now: datetime | None = None,
    ) -> ActivatedPlayer:
        if not isinstance(principal_id, UUID) or not isinstance(player_id, UUID):
            raise TypeError("principal_id and player_id must be UUID values")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_player.bind_accepted_identity(%s,%s)",
                        (principal_id, player_id),
                    )
                    row = cur.fetchone()
                    if row is None or row[0] is None:
                        raise PlayerActivationError("identity binding returned no canonical person")
                    person_id = int(row[0])
                    session = self._sessions.issue_in_transaction(
                        cur,
                        principal_id,
                        lifetime=lifetime,
                        active_person_id=person_id,
                        authentication_strength=authentication_strength,
                        now=now,
                    )
            return ActivatedPlayer(player_id, principal_id, person_id, session)
        except PlayerActivationError:
            raise
        except Exception as exc:
            raise PlayerActivationError(f"player activation failed: {exc}") from exc
