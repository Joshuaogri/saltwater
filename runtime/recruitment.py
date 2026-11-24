"""Recruit-entry persistence adapter for the PKG-003 PostgreSQL contract.

The adapter is deliberately thin: invariants and atomicity live in PostgreSQL.
Use a trusted server-side connection; never expose this connection to the player.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import UUID


class RecruitmentError(RuntimeError):
    """Recruitment operation failed or its outcome could not be verified."""


@dataclass(frozen=True, slots=True)
class RecruitStatus:
    player_id: UUID
    intake_id: UUID
    intake_status: str
    requested_tick: int
    career_id: UUID | None
    career_stage: str | None
    career_status: str | None
    started_tick: int | None
    person_id: int | None
    service_number: str | None
    service_standing: str | None
    service_status: str | None
    supervisor_person_id: int | None


class PostgresRecruitmentService:
    """Trusted application adapter for request, authorised acceptance and status."""

    def __init__(self, connect: Callable):
        self._connect = connect

    def _fetch_one(self, sql: str, params: tuple, operation: str):
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    return cur.fetchone()
        except Exception as exc:
            raise RecruitmentError(f"{operation} failed: {exc}") from exc

    def _fetch_all(self, sql: str, params: tuple, operation: str):
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    return cur.fetchall()
        except Exception as exc:
            raise RecruitmentError(f"{operation} failed: {exc}") from exc

    def request_intake(self, player_id: UUID, display_name: str, idempotency_key: str) -> UUID:
        if not isinstance(player_id, UUID):
            raise ValueError("player_id must be a UUID")
        if not display_name or not display_name.strip():
            raise ValueError("display_name is required")
        if not idempotency_key or len(idempotency_key.strip()) < 8:
            raise ValueError("idempotency_key must contain at least 8 characters")
        row = self._fetch_one(
            "SELECT sw_police.request_recruit_intake(%s,%s,%s)",
            (player_id, display_name.strip(), idempotency_key),
            "recruit intake request",
        )
        if row is None or row[0] is None:
            raise RecruitmentError("intake request returned no identifier")
        return UUID(str(row[0]))

    def accept_intake(
        self,
        intake_id: UUID,
        *,
        supervisor_person_id: int,
        appointment_source: str,
        idempotency_key: str,
        authorised_by_principal_id: UUID,
        given_name: str | None = None,
        middle_name: str | None = None,
        family_name: str | None = None,
    ) -> UUID:
        if not isinstance(intake_id, UUID) or not isinstance(authorised_by_principal_id, UUID):
            raise ValueError("intake and approver identifiers must be UUIDs")
        if supervisor_person_id <= 0:
            raise ValueError("a valid supervisor person ID is required")
        if not appointment_source or not appointment_source.strip():
            raise ValueError("appointment source is required")
        if not given_name or not given_name.strip() or not family_name or not family_name.strip():
            raise ValueError("canonical person given_name and family_name are required")
        if middle_name is not None and not middle_name.strip():
            middle_name = None
        if not idempotency_key or len(idempotency_key.strip()) < 8:
            raise ValueError("idempotency_key must contain at least 8 characters")
        row = self._fetch_one(
            """SELECT sw_police.accept_recruit_intake(
                 %s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                intake_id, supervisor_person_id, appointment_source.strip(),
                idempotency_key, authorised_by_principal_id,
                given_name, middle_name, family_name,
            ),
            "recruit appointment",
        )
        if row is None or row[0] is None:
            raise RecruitmentError("appointment returned no career identifier")
        return UUID(str(row[0]))

    def status(self, player_id: UUID) -> tuple[RecruitStatus, ...]:
        if not isinstance(player_id, UUID):
            raise ValueError("player_id must be a UUID")
        rows = self._fetch_all(
            """SELECT player_id,intake_id,intake_status,requested_tick,
                      career_id,career_stage,career_status,started_tick,
                      person_id,service_number,service_standing,service_status,
                      supervisor_person_id
               FROM sw_police.player_career_status
               WHERE player_id=%s ORDER BY requested_tick,intake_id""",
            (player_id,),
            "career status lookup",
        )
        return tuple(RecruitStatus(*row) for row in rows)
