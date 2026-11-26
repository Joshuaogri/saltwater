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


class PostgresIncidentOperationalTimelineReader:
    """Read BP12 dispatch/arrival chronology without mutating operational state."""

    _CODES = frozenset({"DISPATCH_ACKNOWLEDGED", "UNIT_ARRIVED"})

    def __init__(self, connect: Callable[[], Any]):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect

    def read(self, incident_id: int) -> list[dict]:
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT event_id,incident_id,event_code,occurred_at,"
                        "world_tick,source_ref,attributes "
                        "FROM sw_incident.operational_timeline(%s)",
                        (incident_id,),
                    )
                    rows = cur.fetchall()
            result = []
            for row in rows:
                if len(row) != 7:
                    raise ValueError("BP12 returned an invalid operational timeline row.")
                event_id, row_incident_id, event_code, occurred_at, world_tick, source_ref, attributes = row
                if row_incident_id != incident_id:
                    raise ValueError("BP12 returned a conflicting incident identity.")
                if event_code not in self._CODES:
                    raise ValueError("BP12 returned an unsupported operational event.")
                if not isinstance(source_ref, str) or not source_ref.strip():
                    raise ValueError("BP12 operational event is missing source provenance.")
                if type(event_id) is not int or event_id < 1 or type(world_tick) is not int or world_tick < 0:
                    raise ValueError("BP12 operational event identity or world tick is invalid.")
                if occurred_at is None or not isinstance(attributes, dict):
                    raise ValueError("BP12 operational event attributes or timestamp are invalid.")
                if attributes.get("source_ref") != source_ref:
                    raise ValueError("BP12 operational event source provenance does not reconcile.")
                if not attributes.get("actor_ref") or not attributes.get("authority_ref"):
                    raise ValueError("BP12 operational event is missing actor or authority provenance.")
                if event_code == "DISPATCH_ACKNOWLEDGED" and not attributes.get("dispatch_ref"):
                    raise ValueError("Dispatch acknowledgement is missing its dispatch reference.")
                if event_code == "UNIT_ARRIVED" and not all(
                    attributes.get(key) for key in ("unit_ref", "assignment_ref", "field_activity_ref")
                ):
                    raise ValueError("Unit arrival is missing deployment or field activity provenance.")
                result.append({
                    "event_id": event_id,
                    "incident_id": row_incident_id,
                    "event_code": event_code,
                    "occurred_at": occurred_at,
                    "world_tick": world_tick,
                    "source_ref": source_ref,
                    "attributes": attributes,
                })
            return result
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            raise RuntimeError("Incident operational timeline is unavailable.") from exc


def build_incident_operational_timeline_view(rows: list[dict]) -> list[dict]:
    """Create a minimal dispatcher/incident-commander presentation from authorised rows.

    Callers must obtain rows through the audited officer access method first.
    This projection is read-only and does not replace BP11/BP08/BP10 ownership.
    """
    if not isinstance(rows, list):
        raise TypeError("Authorised operational timeline rows must be a list.")
    view = []
    previous_key = None
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Operational timeline contains an invalid row.")
        code = row.get("event_code")
        attributes = row.get("attributes")
        if code not in {"DISPATCH_ACKNOWLEDGED", "UNIT_ARRIVED"}:
            raise ValueError("Operational timeline contains an unsupported event.")
        if not isinstance(attributes, dict):
            raise ValueError("Operational timeline attributes are invalid.")
        event_id = row.get("event_id")
        world_tick = row.get("world_tick")
        occurred_at = row.get("occurred_at")
        if type(event_id) is not int or event_id < 1 or type(world_tick) is not int or world_tick < 0:
            raise ValueError("Operational timeline ordering fields are invalid.")
        if occurred_at is None or not row.get("source_ref"):
            raise ValueError("Operational timeline chronology or provenance is incomplete.")
        order_key = (world_tick, event_id)
        if previous_key is not None and order_key < previous_key:
            raise ValueError("Operational timeline is not in canonical event order.")
        previous_key = order_key
        if code == "DISPATCH_ACKNOWLEDGED":
            if not attributes.get("dispatch_ref"):
                raise ValueError("Dispatch acknowledgement is missing its dispatch reference.")
            label = "Dispatch acknowledged"
            references = {"dispatch_ref": attributes["dispatch_ref"]}
        else:
            required = ("unit_ref", "assignment_ref", "field_activity_ref")
            if not all(attributes.get(key) for key in required):
                raise ValueError("Unit arrival is missing deployment or field activity provenance.")
            label = "Unit arrived"
            references = {key: attributes[key] for key in required}
        view.append({
            "event_id": event_id,
            "label": label,
            "occurred_at": occurred_at,
            "world_tick": world_tick,
            "references": references,
            "actor_ref": attributes.get("actor_ref"),
            "authority_ref": attributes.get("authority_ref"),
            "source_ref": row["source_ref"],
        })
    return view
