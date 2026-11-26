"""BP12 incident command service for authorised police operations.

This service owns the officer-facing incident intake and read surface. It uses
BP12's existing database functions and tables; it does not create a shadow CAD,
dispatch, or incident store. Dispatch assignment remains a BP11/BP08 workflow.
"""
from __future__ import annotations

from typing import Any, Callable
from uuid import UUID

from runtime.security import AuthorizationService, PrincipalKind


_SOURCE_TYPES = frozenset({
    "communications_contact", "police_call", "cad_event", "officer_report",
    "alarm", "interagency", "system", "other",
})
_CALLER_STATES = frozenset({
    "known", "claimed", "anonymous", "withheld", "unknown", "not_applicable",
})
_SEVERITIES = frozenset({"critical", "high", "moderate", "low", "unassessed"})
_LOCATION_TYPES = frozenset({
    "canonical_spatial", "property", "premises", "road", "landmark",
    "public_space", "raw", "external",
})
_CONFIDENCES = frozenset({"high", "medium", "low", "unverified", "unknown"})


class IncidentServiceError(RuntimeError):
    """Incident operation failed without exposing database internals."""


class PostgresIncidentService:
    """Audited officer service over the canonical BP12 incident records."""

    def __init__(
        self,
        connect: Callable[[], Any],
        authorization: AuthorizationService,
        principal_id: UUID,
        *,
        purpose: str = "police_workflow",
    ):
        if not callable(connect):
            raise TypeError("connect must be a trusted connection factory")
        if not isinstance(authorization, AuthorizationService):
            raise TypeError("authorization must be an AuthorizationService")
        if not isinstance(principal_id, UUID):
            raise TypeError("principal_id must be a UUID")
        if purpose != "police_workflow":
            raise ValueError("incident service purpose must be police_workflow")
        self._connect = connect
        self._authorization = authorization
        self._principal_id = principal_id
        self._purpose = purpose

    def _require(self, credential: str, action: str, resource: str):
        decision = self._authorization.decide(
            credential,
            action=action,
            resource=resource,
            purpose=self._purpose,
            expected_principal_id=self._principal_id,
            expected_principal_kind=PrincipalKind.OFFICER,
        )
        if not decision.allowed:
            raise PermissionError("Access denied.")
        return decision

    @staticmethod
    def _positive_id(incident_id: int) -> int:
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        return incident_id

    def list_open(self, credential: str, *, limit: int = 20) -> list[dict]:
        """Return a bounded operational queue, without exposing hidden case truth."""
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("Incident queue limit must be between 1 and 100.")
        self._require(credential, "bp12.incident.list", "incidents:open")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT incident_id, incident_ref, status, source_type,
                               category_code, priority, severity_code,
                               priority_rationale, received_tick, created_tick,
                               updated_tick, location_count, source_count
                        FROM sw_incident.incident_current
                        WHERE status NOT IN
                          ('CLOSED','CANCELLED','DUPLICATE_LINKED')
                        ORDER BY priority ASC NULLS LAST, created_tick,
                                 incident_id
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            keys = (
                "incident_id", "incident_ref", "status", "source_type",
                "category_code", "priority", "severity_code",
                "priority_rationale", "received_tick", "created_tick",
                "updated_tick", "location_count", "source_count",
            )
            return [dict(zip(keys, row)) for row in rows]
        except PermissionError:
            raise
        except Exception as exc:
            raise IncidentServiceError("Incident queue is unavailable.") from exc

    def inspect(self, credential: str, incident_id: int) -> dict | None:
        """Read one incident and its recorded locations through separate grants."""
        incident_id = self._positive_id(incident_id)
        self._require(
            credential, "bp12.incident.inspect", f"incident:{incident_id}"
        )
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT incident_id, incident_ref, record_version, status,
                               source_type, source_record_id, caller_identity_state,
                               original_report_text, operational_summary,
                               category_code, priority, severity_code,
                               priority_rationale, received_tick, created_tick,
                               updated_tick, owning_function, lead_unit_id,
                               commander_personnel_id, resolution_code,
                               closure_reason, duplicate_of_incident_id,
                               location_count, source_count
                        FROM sw_incident.incident_current
                        WHERE incident_id=%s
                        """,
                        (incident_id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        return None
                    keys = (
                        "incident_id", "incident_ref", "record_version", "status",
                        "source_type", "source_record_id", "caller_identity_state",
                        "original_report_text", "operational_summary",
                        "category_code", "priority", "severity_code",
                        "priority_rationale", "received_tick", "created_tick",
                        "updated_tick", "owning_function", "lead_unit_id",
                        "commander_personnel_id", "resolution_code",
                        "closure_reason", "duplicate_of_incident_id",
                        "location_count", "source_count",
                    )
                    incident = dict(zip(keys, row))
                    cur.execute(
                        """
                        SELECT incident_location_id, location_role, location_type,
                               spatial_id, location_ref, raw_description,
                               confidence, effective_tick, source_event_id,
                               source_ref
                        FROM sw_incident.incident_location
                        WHERE incident_id=%s
                        ORDER BY effective_tick, incident_location_id
                        """,
                        (incident_id,),
                    )
                    location_rows = cur.fetchall()
            location_keys = (
                "incident_location_id", "location_role", "location_type",
                "spatial_id", "location_ref", "raw_description", "confidence",
                "effective_tick", "source_event_id", "source_ref",
            )
            incident["locations"] = [
                dict(zip(location_keys, item)) for item in location_rows
            ]
            return incident
        except PermissionError:
            raise
        except Exception as exc:
            raise IncidentServiceError("Incident record is unavailable.") from exc

    def create(
        self,
        credential: str,
        *,
        source_type: str,
        source_record_id: str,
        narrative: str,
        idempotency_key: str,
        caller_identity_state: str = "unknown",
        category_code: str = "unclassified",
        priority: int | None = None,
        severity_code: str = "unassessed",
        location_raw: str | None = None,
        location_ref: str | None = None,
        location_type: str = "raw",
        location_confidence: str = "unknown",
    ) -> int:
        """Create a canonical BP12 incident from an attributable operational source."""
        values = {
            "source_record_id": source_record_id,
            "narrative": narrative,
            "idempotency_key": idempotency_key,
            "category_code": category_code,
        }
        if source_type not in _SOURCE_TYPES:
            raise ValueError("Unsupported incident source type.")
        if caller_identity_state not in _CALLER_STATES:
            raise ValueError("Unsupported caller identity state.")
        if severity_code not in _SEVERITIES:
            raise ValueError("Unsupported incident severity.")
        if priority is not None and (type(priority) is not int or not 1 <= priority <= 5):
            raise ValueError("Incident priority must be between 1 and 5.")
        for name, value in values.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required.")
        if location_raw is not None:
            if not isinstance(location_raw, str) or not location_raw.strip():
                raise ValueError("Location description must be non-empty when supplied.")
            if location_type not in _LOCATION_TYPES:
                raise ValueError("Unsupported incident location type.")
            if location_confidence not in _CONFIDENCES:
                raise ValueError("Unsupported incident location confidence.")
            if location_type == "canonical_spatial":
                raise ValueError("Canonical spatial IDs are not accepted by this intake adapter.")
        elif location_ref is not None:
            raise ValueError("A location reference requires a location description.")

        decision = self._require(
            credential, "bp12.incident.create", "incidents:intake"
        )
        if type(decision.active_person_id) is not int or decision.active_person_id < 1:
            raise PermissionError("Access denied.")
        actor_ref = f"officer-person:{decision.active_person_id}"
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT sw_incident.create_incident(
                          %s,%s,%s,%s,%s,NULL,%s,%s,%s,%s,%s,%s,%s,%s,NULL
                        )
                        """,
                        (
                            source_type, source_record_id, narrative, actor_ref,
                            idempotency_key, caller_identity_state, category_code,
                            priority, severity_code, location_raw, location_ref,
                            location_type, location_confidence,
                        ),
                    )
                    row = cur.fetchone()
                    if row is None or type(row[0]) is not int or row[0] < 1:
                        raise IncidentServiceError("Incident creation returned no identity.")
                conn.commit()
            return row[0]
        except PermissionError:
            raise
        except IncidentServiceError:
            raise
        except Exception as exc:
            raise IncidentServiceError("Incident intake could not be completed.") from exc
