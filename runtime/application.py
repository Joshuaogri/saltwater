"""Trusted composition root for the durable Saltwater player application.

This module wires existing PostgreSQL adapters; it does not open connections,
apply migrations, seed data, or change production configuration. Construct and
expose this object only inside a trusted server-side process after the host has
authenticated the player and applied its authorization policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from runtime.kernel import PostgresRuntimeStore, RuntimeKernel
from runtime.player_interface import PlayerCommandInterface, PlayerProfile
from runtime.recruitment import PostgresRecruitmentService


@dataclass(frozen=True, slots=True)
class PostgresPlayerApplication:
    """One player's command surface over shared durable PostgreSQL services."""

    kernel: RuntimeKernel
    recruitment: PostgresRecruitmentService
    commands: PlayerCommandInterface


def create_postgres_player_application(
    connect: Callable[[], Any],
    profile: PlayerProfile,
) -> PostgresPlayerApplication:
    """Build the durable application using one trusted connection factory.

    The factory is lazy: this function does not connect to PostgreSQL. The
    database must already contain the approved foundation and proposal schemas.
    Authentication, authorization, credential management and HTTP/ChatGPT
    transport remain responsibilities of the trusted host around this object.
    """
    if not callable(connect):
        raise TypeError("connect must be a trusted PostgreSQL connection factory")
    if not isinstance(profile, PlayerProfile):
        raise TypeError("profile must be a PlayerProfile")

    kernel = RuntimeKernel(PostgresRuntimeStore(connect))
    recruitment = PostgresRecruitmentService(connect)
    commands = PlayerCommandInterface(kernel, profile, recruitment)
    return PostgresPlayerApplication(
        kernel=kernel,
        recruitment=recruitment,
        commands=commands,
    )
