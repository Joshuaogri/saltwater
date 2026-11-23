"""Trusted composition root for the durable Saltwater player application.

This module wires existing PostgreSQL adapters; it does not open connections,
apply migrations, seed data, or change production configuration. Construct and
expose this object only inside a trusted server-side process.
"""
from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Any, Callable
from uuid import UUID

from runtime.kernel import PostgresRuntimeStore, RuntimeKernel
from runtime.player_interface import CommandResult, PlayerCommandInterface, PlayerProfile
from runtime.recruitment import PostgresRecruitmentService
from runtime.postgres_sessions import PostgresSessionLifecycle
from runtime.security import AuthorizationService


@dataclass(frozen=True, slots=True)
class PostgresPlayerApplication:
    """One player's command surface over shared durable PostgreSQL services."""

    kernel: RuntimeKernel
    recruitment: PostgresRecruitmentService
    sessions: PostgresSessionLifecycle
    commands: PlayerCommandInterface


@dataclass(frozen=True, slots=True)
class AuthorizedPlayerCommandGateway:
    """Session- and grant-checked boundary around a player's command router."""

    commands: PlayerCommandInterface
    authorization: AuthorizationService
    principal_id: UUID
    player_resource: str
    purpose: str = "gameplay"

    def execute(self, credential: str, line: str) -> CommandResult:
        """Authorize one known command before dispatch; deny by default."""
        try:
            parts = shlex.split(line)
        except ValueError:
            return CommandResult(False, "Invalid command.")
        if not parts or len(parts) != 1:
            return CommandResult(False, "Invalid command.")

        command = parts[0].casefold()
        allowed_commands = {
            "help", "status", "profile", "recruit", "career",
            "start", "pause", "resume", "quit",
        }
        if command not in allowed_commands:
            return CommandResult(False, "Access denied.")

        decision = self.authorization.decide(
            credential,
            action=f"player.command.{command}",
            resource=self.player_resource,
            purpose=self.purpose,
            expected_principal_id=self.principal_id,
        )
        if not decision.allowed:
            return CommandResult(False, "Access denied.")
        return self.commands.execute(line)


def create_postgres_player_application(
    connect: Callable[[], Any],
    profile: PlayerProfile,
) -> PostgresPlayerApplication:
    """Build the durable application using one trusted connection factory.

    The factory is lazy: this function does not connect to PostgreSQL. The
    database must already contain the approved foundation and proposal schemas.
    Authentication, credential management and HTTP/ChatGPT transport remain
    responsibilities of the trusted host around this object.
    """
    if not callable(connect):
        raise TypeError("connect must be a trusted PostgreSQL connection factory")
    if not isinstance(profile, PlayerProfile):
        raise TypeError("profile must be a PlayerProfile")

    kernel = RuntimeKernel(PostgresRuntimeStore(connect))
    recruitment = PostgresRecruitmentService(connect)
    sessions = PostgresSessionLifecycle(connect)
    commands = PlayerCommandInterface(kernel, profile, recruitment)
    return PostgresPlayerApplication(
        kernel=kernel,
        recruitment=recruitment,
        sessions=sessions,
        commands=commands,
    )


def bind_authorized_player_commands(
    application: PostgresPlayerApplication,
    authorization: AuthorizationService,
    principal_id: UUID,
) -> AuthorizedPlayerCommandGateway:
    """Bind a trusted authenticated principal to this application's player."""
    if not isinstance(application, PostgresPlayerApplication):
        raise TypeError("application must be a PostgresPlayerApplication")
    if not isinstance(authorization, AuthorizationService):
        raise TypeError("authorization must be an AuthorizationService")
    if not isinstance(principal_id, UUID):
        raise TypeError("principal_id must be a UUID")
    return AuthorizedPlayerCommandGateway(
        commands=application.commands,
        authorization=authorization,
        principal_id=principal_id,
        player_resource=f"player:{application.commands.profile.player_id}",
    )
