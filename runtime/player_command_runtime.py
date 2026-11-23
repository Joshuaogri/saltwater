"""Authenticated PostgreSQL-backed player command execution (PKG-005).

The opaque session is the sole identity input. Player identity/profile/career are
resolved from immutable database records; command authorization is re-evaluated
by the existing gateway for every command.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from runtime.application import (
    AuthorizedPlayerCommandGateway,
    bind_authorized_player_commands,
    create_postgres_player_application,
)
from runtime.player_interface import CommandResult, PlayerProfile
from runtime.security import AuthorizationService, PrincipalKind, SessionVerifier


class PlayerContextError(RuntimeError):
    """Authenticated principal has no single consistent player context."""


@dataclass(frozen=True, slots=True)
class ResolvedPlayerContext:
    profile: PlayerProfile
    person_id: int


class PostgresPlayerContextResolver:
    """Resolve one immutable player binding and its authoritative career view."""

    def __init__(self, connect: Callable[[], Any]):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect

    def resolve(self, principal_id, active_person_id: int) -> ResolvedPlayerContext:
        if active_person_id is None or not isinstance(active_person_id, int) or active_person_id <= 0:
            raise PlayerContextError("active player person is not bound to this session")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT b.player_id, b.person_id, p.person_id,
                               profile.display_name,
                               career.career_id, career.career_stage,
                               career.career_status, career.service_status
                        FROM sw_player.identity_binding b
                        JOIN sw_auth.principal p ON p.principal_id=b.principal_id
                        JOIN sw_player.profile profile ON profile.player_id=b.player_id
                        LEFT JOIN LATERAL (
                            SELECT c.career_id, c.career_stage, c.career_status,
                                   personnel.service_status
                            FROM sw_police.career_episode c
                            JOIN sw_police.personnel personnel
                              ON personnel.personnel_id=c.personnel_id
                            WHERE c.player_id=b.player_id
                            ORDER BY c.episode_no DESC, c.started_tick DESC, c.career_id
                            LIMIT 1
                        ) career ON TRUE
                        WHERE b.principal_id=%s
                        """,
                        (principal_id,),
                    )
                    rows = cur.fetchall()
        except Exception as exc:
            raise PlayerContextError("player context could not be resolved") from exc

        if len(rows) != 1:
            raise PlayerContextError("player identity binding is missing or ambiguous")
        (player_id, bound_person_id, principal_person_id, display_name,
         career_id, career_stage, career_status, service_status) = rows[0]
        if bound_person_id != active_person_id or principal_person_id != bound_person_id:
            raise PlayerContextError("session and immutable player identity do not match")
        if not display_name or not str(display_name).strip():
            raise PlayerContextError("authoritative player display name is invalid")

        if career_id is None:
            resolved_career_id = None
            resolved_stage = "not_started"
        else:
            resolved_career_id = str(career_id)
            if career_status == "ended" or service_status == "separated":
                resolved_stage = "former"
            else:
                resolved_stage = career_stage

        try:
            profile = PlayerProfile(
                player_id=str(player_id),
                display_name=str(display_name),
                officer_person_id=int(bound_person_id),
                career_id=resolved_career_id,
                career_stage=resolved_stage,
            )
        except (TypeError, ValueError) as exc:
            raise PlayerContextError("authoritative player profile is inconsistent") from exc
        return ResolvedPlayerContext(profile=profile, person_id=int(bound_person_id))


class PostgresPlayerCommandRuntime:
    """Single trusted in-process entry point for an authenticated player."""

    def __init__(
        self,
        connect: Callable[[], Any],
        verifier: SessionVerifier,
        authorization: AuthorizationService,
    ):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        if not callable(getattr(verifier, "verify", None)):
            raise TypeError("verifier must provide verify(credential)")
        if not isinstance(authorization, AuthorizationService):
            raise TypeError("authorization must be an AuthorizationService")
        self._connect = connect
        self._verifier = verifier
        self._authorization = authorization
        self._resolver = PostgresPlayerContextResolver(connect)

    def execute(self, credential: str, command_text: str) -> CommandResult:
        """Resolve the session identity, then authorize and dispatch one command."""
        if not isinstance(credential, str) or not credential:
            return CommandResult(False, "Access denied.")
        try:
            session = self._verifier.verify(credential)
            if session is None or session.principal_kind != PrincipalKind.PLAYER:
                return CommandResult(False, "Access denied.")
            context = self._resolver.resolve(
                session.principal_id, session.active_person_id
            )
            application = create_postgres_player_application(
                self._connect, context.profile
            )
            gateway: AuthorizedPlayerCommandGateway = bind_authorized_player_commands(
                application, self._authorization, session.principal_id
            )
            # The gateway independently re-verifies the credential and reloads
            # grants; revocation between context resolution and dispatch denies.
            return gateway.execute(credential, command_text)
        except PlayerContextError:
            return CommandResult(False, "Access denied.")
        except Exception:
            # Do not expose SQL errors, credentials, or internal security details.
            return CommandResult(False, "Command unavailable.")
