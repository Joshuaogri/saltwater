"""Read/write adapter for BP12's cross-domain operational event timeline."""
from __future__ import annotations

from typing import Any, Callable
from datetime import date, datetime


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


def reconcile_incident_command_handover(
    incident_id: int,
    *,
    incident_status: str,
    assignment_snapshot: list[dict],
    timeline_rows: list[dict],
    snapshot_source_ref: str,
    as_of_world_tick: int,
) -> dict:
    """Reconcile authorised BP08/BP10 assignment state with BP12 event mirrors.

    The caller must obtain incident, assignment and timeline snapshots through
    their owning systems' authorised readers. This function does not fetch,
    authorise, persist or mutate any operational state.
    """
    if type(incident_id) is not int or incident_id < 1:
        raise ValueError("A positive incident ID is required.")
    if incident_status not in {
        "RECEIVED", "AWAITING_TRIAGE", "ASSESSED", "ALLOCATED", "DISPATCHED",
        "RESPONDING", "ATTENDED", "ACTIVE_MANAGEMENT", "MONITORING",
        "RESOLVED", "CLOSED", "CANCELLED", "DUPLICATE_LINKED", "REOPENED"
    }:
        raise ValueError("Unsupported incident status.")
    if not isinstance(snapshot_source_ref, str) or not snapshot_source_ref.strip():
        raise ValueError("Assignment snapshot provenance is required.")
    if type(as_of_world_tick) is not int or as_of_world_tick < 0:
        raise ValueError("A non-negative snapshot world tick is required.")
    if not isinstance(assignment_snapshot, list) or not isinstance(timeline_rows, list):
        raise TypeError("Authorised assignment and timeline snapshots must be lists.")

    assignments = {}
    allowed_states = {"ASSIGNED", "EN_ROUTE", "ON_SCENE", "COMPLETED", "CANCELLED", "RELEASED"}
    for item in assignment_snapshot:
        if not isinstance(item, dict):
            raise ValueError("Assignment snapshot contains an invalid record.")
        assignment_ref = item.get("assignment_ref")
        unit_ref = item.get("unit_ref")
        status = item.get("status")
        source_ref = item.get("source_ref")
        if not all(isinstance(v, str) and v.strip() for v in (assignment_ref, unit_ref, source_ref)):
            raise ValueError("Assignment snapshot is missing identity or provenance.")
        if status not in allowed_states:
            raise ValueError("Assignment snapshot contains an unsupported state.")
        if assignment_ref in assignments:
            raise ValueError("Assignment snapshot contains duplicate assignment references.")
        assignments[assignment_ref] = {
            "assignment_ref": assignment_ref, "unit_ref": unit_ref,
            "status": status, "source_ref": source_ref,
        }

    arrivals = {}
    previous_key = None
    for event in timeline_rows:
        if not isinstance(event, dict) or event.get("incident_id") != incident_id:
            raise ValueError("Timeline contains a conflicting incident identity.")
        if event.get("event_code") != "UNIT_ARRIVED":
            continue
        attrs = event.get("attributes")
        if not isinstance(attrs, dict):
            raise ValueError("Arrival event attributes are invalid.")
        assignment_ref, unit_ref = attrs.get("assignment_ref"), attrs.get("unit_ref")
        if not assignment_ref or not unit_ref or not event.get("source_ref"):
            raise ValueError("Arrival event is missing assignment or source provenance.")
        tick, event_id = event.get("world_tick"), event.get("event_id")
        if type(tick) is not int or tick < 0 or type(event_id) is not int or event_id < 1:
            raise ValueError("Arrival event ordering fields are invalid.")
        key = (tick, event_id)
        if previous_key is not None and key < previous_key:
            raise ValueError("Timeline is not in canonical event order.")
        previous_key = key
        if assignment_ref in arrivals:
            # Preserve the first arrival; subsequent arrivals for one assignment
            # are a material discrepancy, not a silent overwrite.
            raise ValueError("Multiple arrival events exist for one assignment.")
        arrivals[assignment_ref] = {
            "unit_ref": unit_ref, "event_id": event_id,
            "world_tick": tick, "source_ref": event["source_ref"],
        }

    unresolved = []
    discrepancies = []
    reconciled = []
    terminal_incident = incident_status in {"RESOLVED", "CLOSED", "CANCELLED", "DUPLICATE_LINKED"}
    for assignment_ref, assignment in assignments.items():
        arrival = arrivals.pop(assignment_ref, None)
        if arrival and arrival["unit_ref"] != assignment["unit_ref"]:
            discrepancies.append({
                "type": "ARRIVAL_UNIT_MISMATCH",
                "assignment_ref": assignment_ref,
                "assignment_unit_ref": assignment["unit_ref"],
                "arrival_unit_ref": arrival["unit_ref"],
            })
        arrived = arrival is not None
        active = assignment["status"] in {"ASSIGNED", "EN_ROUTE", "ON_SCENE"}
        if terminal_incident and active:
            discrepancies.append({
                "type": "ACTIVE_ASSIGNMENT_ON_TERMINAL_INCIDENT",
                "assignment_ref": assignment_ref,
                "assignment_status": assignment["status"],
                "incident_status": incident_status,
            })
        if active and not arrived:
            unresolved.append(assignment_ref)
        if arrived and assignment["status"] in {"ASSIGNED", "EN_ROUTE", "CANCELLED", "RELEASED"}:
            discrepancies.append({
                "type": "ARRIVAL_ASSIGNMENT_STATE_MISMATCH",
                "assignment_ref": assignment_ref,
                "assignment_status": assignment["status"],
                "arrival_event_id": arrival["event_id"],
            })
        reconciled.append({
            **assignment,
            "arrival_recorded": arrived,
            "arrival_event_id": arrival["event_id"] if arrival else None,
            "arrival_world_tick": arrival["world_tick"] if arrival else None,
        })
    for assignment_ref, arrival in arrivals.items():
        discrepancies.append({
            "type": "ARRIVAL_WITHOUT_CURRENT_ASSIGNMENT",
            "assignment_ref": assignment_ref,
            "arrival_event_id": arrival["event_id"],
        })

    return {
        "incident_id": incident_id,
        "incident_status": incident_status,
        "snapshot_source_ref": snapshot_source_ref,
        "as_of_world_tick": as_of_world_tick,
        "assignments": reconciled,
        "unresolved_assignment_refs": sorted(unresolved),
        "discrepancies": discrepancies,
        "handover_ready": not unresolved and not discrepancies,
        "read_only": True,
    }


def build_incident_command_handover_record(
    reconciliation: dict,
    *,
    handover_ref: str,
    outgoing_commander_ref: str,
    incoming_commander_ref: str,
    prepared_by_ref: str,
    authority_ref: str,
    source_ref: str,
    effective_world_tick: int,
    commander_decisions: list[dict],
    outstanding_actions: list[dict],
    responsibility_transfers: list[dict],
    acknowledgements: list[dict],
) -> dict:
    """Build a provenance-complete command handover record from owner snapshots.

    This is a validated read-only record projection, not a persistence command.
    Each supplied register must already have been obtained through its owning
    system's authorised reader. Durable append-only recording is a separate
    BP12 operation and is deliberately not implied by this function.
    """
    if not isinstance(reconciliation, dict) or not reconciliation.get("read_only"):
        raise ValueError("A read-only incident command reconciliation is required.")
    for name, value in (
        ("handover_ref", handover_ref),
        ("outgoing_commander_ref", outgoing_commander_ref),
        ("incoming_commander_ref", incoming_commander_ref),
        ("prepared_by_ref", prepared_by_ref),
        ("authority_ref", authority_ref),
        ("source_ref", source_ref),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} is required.")
    if outgoing_commander_ref == incoming_commander_ref:
        raise ValueError("Outgoing and incoming commanders must be different.")
    if type(effective_world_tick) is not int or effective_world_tick < reconciliation.get("as_of_world_tick", 0):
        raise ValueError("Handover effective tick cannot precede the assignment snapshot.")
    registers = {
        "commander_decisions": commander_decisions,
        "outstanding_actions": outstanding_actions,
        "responsibility_transfers": responsibility_transfers,
        "acknowledgements": acknowledgements,
    }
    validated = {}
    for register_name, rows in registers.items():
        if not isinstance(rows, list):
            raise TypeError(f"{register_name} must be an authorised list.")
        seen = set()
        output = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"{register_name} contains an invalid record.")
            record_ref = row.get("record_ref")
            record_source = row.get("source_ref")
            tick = row.get("world_tick")
            actor = row.get("actor_ref")
            if not all(isinstance(v, str) and v.strip() for v in (record_ref, record_source, actor)):
                raise ValueError(f"{register_name} record is missing identity or provenance.")
            if record_ref in seen:
                raise ValueError(f"{register_name} contains duplicate record references.")
            if type(tick) is not int or tick < 0 or tick > effective_world_tick:
                raise ValueError(f"{register_name} contains an invalid or future world tick.")
            seen.add(record_ref)
            output.append(dict(row))
        output.sort(key=lambda item: (item["world_tick"], item["record_ref"]))
        validated[register_name] = output

    for decision in validated["commander_decisions"]:
        if decision.get("commander_ref") not in {outgoing_commander_ref, incoming_commander_ref}:
            raise ValueError("Commander decision is not attributable to either handover commander.")
        if not all(isinstance(decision.get(key), str) and decision[key].strip()
                   for key in ("decision", "rationale")):
            raise ValueError("Commander decision requires a decision and rationale.")
    for action in validated["outstanding_actions"]:
        if not all(isinstance(action.get(key), str) and action[key].strip()
                   for key in ("action", "owner_ref", "status")):
            raise ValueError("Outstanding action requires action, owner and status.")
        if action["status"] not in {"OPEN", "IN_PROGRESS", "BLOCKED", "COMPLETED", "CANCELLED"}:
            raise ValueError("Outstanding action has an unsupported status.")
    for transfer in validated["responsibility_transfers"]:
        if not all(isinstance(transfer.get(key), str) and transfer[key].strip()
                   for key in ("responsibility_ref", "from_ref", "to_ref")):
            raise ValueError("Responsibility transfer is missing its ownership references.")
        if transfer["from_ref"] == transfer["to_ref"]:
            raise ValueError("Responsibility transfer must change the responsible party.")
    for acknowledgement in validated["acknowledgements"]:
        if acknowledgement.get("handover_ref") != handover_ref:
            raise ValueError("Acknowledgement references a different handover.")
        if acknowledgement.get("recipient_ref") not in {outgoing_commander_ref, incoming_commander_ref}:
            raise ValueError("Acknowledgement recipient is not a handover commander.")
        if acknowledgement.get("acknowledgement") not in {"ACCEPTED", "DECLINED", "CONDITIONAL"}:
            raise ValueError("Unsupported handover acknowledgement.")
        if not isinstance(acknowledgement.get("notes", ""), str):
            raise ValueError("Acknowledgement notes must be text.")

    return {
        "handover_ref": handover_ref,
        "incident_id": reconciliation["incident_id"],
        "incident_status": reconciliation["incident_status"],
        "outgoing_commander_ref": outgoing_commander_ref,
        "incoming_commander_ref": incoming_commander_ref,
        "prepared_by_ref": prepared_by_ref,
        "authority_ref": authority_ref,
        "source_ref": source_ref,
        "effective_world_tick": effective_world_tick,
        "assignment_reconciliation": reconciliation,
        **validated,
        "handover_ready": (
            reconciliation["handover_ready"]
            and any(t["from_ref"] == outgoing_commander_ref
                    and t["to_ref"] == incoming_commander_ref
                    for t in validated["responsibility_transfers"])
            and not any(a["acknowledgement"] == "DECLINED"
                        for a in validated["acknowledgements"])
            and any(a["recipient_ref"] == incoming_commander_ref
                    and a["acknowledgement"] == "ACCEPTED"
                    for a in validated["acknowledgements"])
        ),
        "record_status": "PROJECTED_NOT_PERSISTED",
        "read_only": True,
    }



class PostgresIncidentCommandHandoverWriter:
    """Persist a validated BP12 handover projection through the append-only SQL API."""

    def __init__(self, connect: Callable[[], Any]):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect

    def record(self, document: dict, *, idempotency_key: str) -> int:
        if not isinstance(document, dict):
            raise TypeError("A validated command handover document is required.")
        if document.get("record_status") != "PROJECTED_NOT_PERSISTED" or document.get("read_only") is not True:
            raise ValueError("Only an unpersisted read-only handover projection may be submitted.")
        if document.get("handover_ready") is not True:
            raise ValueError("Only a reconciled, accepted and ready handover may be persisted.")
        required = (
            "handover_ref", "incident_id", "outgoing_commander_ref",
            "incoming_commander_ref", "prepared_by_ref", "authority_ref",
            "source_ref", "effective_world_tick", "assignment_reconciliation",
            "commander_decisions", "outstanding_actions", "responsibility_transfers",
            "acknowledgements",
        )
        if any(key not in document for key in required):
            raise ValueError("Command handover projection is missing required fields.")
        if type(document["incident_id"]) is not int or document["incident_id"] < 1:
            raise ValueError("A positive incident ID is required.")
        if type(document["effective_world_tick"]) is not int or document["effective_world_tick"] < 0:
            raise ValueError("A non-negative effective world tick is required.")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ValueError("A non-empty idempotency key is required.")
        for key in ("commander_decisions", "outstanding_actions", "responsibility_transfers", "acknowledgements"):
            if not isinstance(document[key], list):
                raise ValueError(f"{key} must be a list.")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT sw_incident.record_command_handover("
                        "%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)",
                        (
                            document["incident_id"], document["handover_ref"],
                            document["outgoing_commander_ref"], document["incoming_commander_ref"],
                            document["prepared_by_ref"], document["authority_ref"],
                            document["source_ref"], document["effective_world_tick"],
                            __import__("json").dumps(
                                document, separators=(",", ":"), sort_keys=True,
                                default=lambda value: value.isoformat()
                                if isinstance(value, (date, datetime))
                                else (_ for _ in ()).throw(TypeError(
                                    f"Unsupported command handover JSON value: {type(value).__name__}"
                                )),
                            ),
                            idempotency_key,
                        ),
                    )
                    row = cur.fetchone()
                conn.commit()
            if not row or type(row[0]) is not int or row[0] < 1:
                raise RuntimeError("BP12 did not return a command handover record ID.")
            return row[0]
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            raise RuntimeError("Command handover could not be persisted.") from exc


class PostgresIncidentCommandHandoverHistoryReader:
    """Read the immutable BP12 command handover register in canonical chronology."""

    def __init__(self, connect: Callable[[], Any]):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect

    def read(self, incident_id: int) -> list[dict]:
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        query = (
            "SELECT command_handover_id,handover_ref,incident_id,"
            "outgoing_commander_ref,incoming_commander_ref,prepared_by_ref,"
            "authority_ref,source_ref,effective_world_tick,handover_document,"
            "source_event_id,occurred_at,event_world_tick "
            "FROM sw_incident.command_handover_history(%s)"
        )
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (incident_id,))
                    rows = cur.fetchall()
            result = []
            previous = None
            for row in rows:
                if len(row) != 13:
                    raise ValueError("BP12 returned an invalid command handover history row.")
                (record_id, handover_ref, row_incident_id, outgoing, incoming,
                 prepared_by, authority, source_ref, effective_tick, document,
                 event_id, occurred_at, event_tick) = row
                if row_incident_id != incident_id:
                    raise ValueError("BP12 returned a conflicting incident identity.")
                if any(not isinstance(value, str) or not value.strip() for value in
                       (handover_ref, outgoing, incoming, prepared_by, authority, source_ref)):
                    raise ValueError("BP12 command handover history is missing provenance.")
                if type(record_id) is not int or record_id < 1 or type(event_id) is not int or event_id < 1:
                    raise ValueError("BP12 command handover history identity is invalid.")
                if type(effective_tick) is not int or effective_tick < 0 or type(event_tick) is not int or event_tick < 0:
                    raise ValueError("BP12 command handover history tick is invalid.")
                if occurred_at is None or not isinstance(document, dict):
                    raise ValueError("BP12 command handover history document or timestamp is invalid.")
                if document.get("record_status") != "PERSISTED" or document.get("read_only") is not True:
                    raise ValueError("BP12 persisted handover document status is inconsistent.")
                order = (effective_tick, record_id)
                if previous is not None and order < previous:
                    raise ValueError("BP12 command handover history is not chronologically ordered.")
                previous = order
                result.append({
                    "command_handover_id": record_id, "handover_ref": handover_ref,
                    "incident_id": row_incident_id, "outgoing_commander_ref": outgoing,
                    "incoming_commander_ref": incoming, "prepared_by_ref": prepared_by,
                    "authority_ref": authority, "source_ref": source_ref,
                    "effective_world_tick": effective_tick, "handover_document": document,
                    "source_event_id": event_id, "occurred_at": occurred_at,
                    "event_world_tick": event_tick,
                })
            return result
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            raise RuntimeError("Command handover history is unavailable.") from exc
