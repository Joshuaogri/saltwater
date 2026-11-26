"""Read/write adapter for BP12's cross-domain operational event timeline."""
from __future__ import annotations

from typing import Any, Callable


class PostgresIncidentOperationalEventWriter:
    """Append dispatch/arrival event mirrors without owning BP11/BP10 state."""

    _CODES = frozenset({"DISPATCH_ACKNOWLEDGED", "UNIT_ARRIVED"})

    def __init__(self, connect: Callable[[], Any]):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect

    def record(
        self, *, incident_id: int, event_code: str, actor_ref: str,
        authority_ref: str, source_ref: str, description: str,
        idempotency_key: str, dispatch_ref: str | None = None,
        unit_ref: str | None = None, assignment_ref: str | None = None,
        field_activity_ref: str | None = None,
    ) -> int:
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        if event_code not in self._CODES:
            raise ValueError("Unsupported incident operational event.")
        for name, value in (
            ("actor_ref", actor_ref), ("authority_ref", authority_ref),
            ("source_ref", source_ref), ("description", description),
            ("idempotency_key", idempotency_key),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required.")
        if event_code == "DISPATCH_ACKNOWLEDGED" and not dispatch_ref:
            raise ValueError("A dispatch reference is required.")
        if event_code == "UNIT_ARRIVED" and not all(
            (unit_ref, assignment_ref, field_activity_ref)
        ):
            raise ValueError("Unit, deployment and field activity references are required.")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT sw_incident.record_operational_timeline_event(
                           %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (
                            incident_id, event_code, actor_ref, authority_ref,
                            source_ref, dispatch_ref, unit_ref, assignment_ref,
                            field_activity_ref, description, idempotency_key,
                        ),
                    )
                    row = cur.fetchone()
                conn.commit()
            if not row or type(row[0]) is not int:
                raise RuntimeError("BP12 did not return an operational event ID.")
            return row[0]
        except Exception as exc:
            try:
                conn.rollback()
            except Exception:
                pass
            raise RuntimeError("Incident operational event could not be recorded.") from exc
