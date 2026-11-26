"""Officer-authorised BP04 property and location lookup adapter.

This is deliberately separate from the public player command surface. Every
search or inspection is re-authorised against current grants and written to
the configured audit sink. The supplied AuthorizationService must use a
durable append-only audit adapter in production; audit failure denies access.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from runtime.security import AuthorizationService, PrincipalKind


SEARCH_TYPES = frozenset({"address", "property", "business"})
INSPECT_TYPES = frozenset({
    "property", "address", "building", "premises", "unit",
    "access_point", "business", "establishment",
})


class BP04PoliceLookupAccess:
    """Read-only police workflow facade over a shared BP04Lookup instance."""

    def __init__(
        self,
        lookup: Any,
        authorization: AuthorizationService,
        principal_id: UUID,
        *,
        purpose: str = "police_workflow",
    ):
        if lookup is None:
            raise TypeError("lookup is required")
        if not isinstance(authorization, AuthorizationService):
            raise TypeError("authorization must be an AuthorizationService")
        if not isinstance(principal_id, UUID):
            raise TypeError("principal_id must be a UUID")
        if purpose != "police_workflow":
            raise ValueError("police lookup purpose must be police_workflow")
        self._lookup = lookup
        self._authorization = authorization
        self._principal_id = principal_id
        self._purpose = purpose

    def _require(self, credential: str, action: str, resource: str) -> None:
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

    def search(
        self, credential: str, entity_type: str, query: str, limit: int = 20
    ) -> list[dict]:
        kind = str(entity_type).casefold()
        if kind not in SEARCH_TYPES:
            raise ValueError("Police search supports address, property or business.")
        self._require(
            credential,
            f"bp04.lookup.search.{kind}",
            f"bp04:{kind}:search",
        )
        return self._lookup.search(kind, query, limit=limit)

    def inspect(self, credential: str, entity_type: str, identifier: str) -> dict | None:
        kind = str(entity_type).casefold()
        if kind not in INSPECT_TYPES:
            raise ValueError("Unsupported BP04 inspection type.")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("A stable BP04 identifier is required.")
        self._require(
            credential,
            f"bp04.lookup.inspect.{kind}",
            f"bp04:{kind}:{identifier}",
        )
        if kind == "property":
            return self._lookup.property_detail(identifier)
        if kind == "address":
            return self._lookup.address_detail(identifier)
        if kind == "business":
            return self._lookup.business_detail(identifier)
        return self._lookup.get(kind, identifier)

    def resolve_address(self, credential: str, address_id: str) -> dict | None:
        """Resolve a dispatch/investigation address through an audited read."""
        return self.inspect(credential, "address", address_id)




class BP04IncidentLocationResolver:
    """Prepare a provenance-preserving incident/address candidate without writing.

    Incident and address reads are independently authorised and audited.
    Persistence remains the responsibility of the BP12 event-backed location
    command; this resolver cannot mutate incident history.
    """

    def __init__(self, police_access: BP04PoliceLookupAccess, incident_reader):
        if not isinstance(police_access, BP04PoliceLookupAccess):
            raise TypeError("police_access must be BP04PoliceLookupAccess")
        if not callable(incident_reader):
            raise TypeError("incident_reader must be a trusted callable")
        self._access = police_access
        self._incident_reader = incident_reader

    def prepare_address_candidate(
        self, credential: str, incident_id: int, address_id: str, *,
        location_role: str = "primary", confidence: str = "unverified",
        source_ref: str,
    ) -> dict:
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        if location_role not in {"primary", "secondary", "staging", "origin",
                                 "last_known", "search_area", "other"}:
            raise ValueError("Unsupported incident location role.")
        if confidence not in {"high", "medium", "low", "unverified", "unknown"}:
            raise ValueError("Unsupported location confidence.")
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise ValueError("The originating location source reference is required.")

        self._access._require(
            credential, "bp12.incident.inspect.location", f"incident:{incident_id}"
        )
        incident = self._incident_reader(incident_id)
        if not incident:
            raise LookupError("Incident not found.")
        if incident.get("incident_id") != incident_id:
            raise ValueError("Incident reader returned a conflicting incident identity.")

        address = self._access.resolve_address(credential, address_id)
        if not address:
            raise LookupError("Address not found.")
        address_record = address.get("address", address)
        if address_record.get("address_id") != address_id:
            raise ValueError("Address lookup returned a conflicting identity.")
        return {
            "record_type": "incident_location_candidate",
            "incident_id": incident_id,
            "incident_ref": incident.get("incident_ref"),
            "incident_source_ref": incident.get("source_ref") or
                f"{incident.get('source_type')}:{incident.get('source_record_id')}",
            "location_role": location_role,
            "location_type": "property",
            "address_id": address_id,
            "address": address_record,
            "confidence": confidence,
            "source_ref": source_ref,
            "address_source_ref": address_record.get("source_ref") or
                f"bp04-address:{address_id}",
            "approval_required": True,
            "persisted": False,
        }


    def record_address_location(
        self, credential: str, incident_id: int, address_id: str, *,
        location_writer, actor_ref: str, authority_ref: str,
        idempotency_key: str, location_role: str = "primary",
        confidence: str = "unverified", source_ref: str,
        raw_description: str,
    ) -> dict:
        """Record a reviewed address through a trusted BP12 event-backed writer."""
        if not callable(location_writer):
            raise TypeError("A trusted BP12 location writer is required")
        for name, value in (
            ("actor_ref", actor_ref), ("authority_ref", authority_ref),
            ("idempotency_key", idempotency_key),
            ("raw_description", raw_description),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        candidate = self.prepare_address_candidate(
            credential, incident_id, address_id,
            location_role=location_role, confidence=confidence,
            source_ref=source_ref,
        )
        location_id = location_writer(
            p_incident_id=incident_id,
            p_location_role=candidate["location_role"],
            p_location_type=candidate["location_type"],
            p_location_ref=address_id,
            p_spatial_id=None,
            p_raw_description=raw_description,
            p_confidence=candidate["confidence"],
            p_actor_ref=actor_ref,
            p_authority_ref=authority_ref,
            p_source_ref=candidate["source_ref"],
            p_address_source_ref=candidate["address_source_ref"],
            p_idempotency_key=idempotency_key,
        )
        return {
            **candidate,
            "approval_required": False,
            "persisted": True,
            "incident_location_id": location_id,
        }


    def read_location_history(
        self, credential: str, incident_id: int, *, location_history_reader
    ) -> list[dict]:
        """Read the complete BP12 location chronology under an explicit grant."""
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        if not callable(location_history_reader):
            raise TypeError("A trusted BP12 location history reader is required")
        self._access._require(
            credential,
            "bp12.incident.inspect.location.history",
            f"incident:{incident_id}",
        )
        rows = location_history_reader(incident_id)
        if rows is None:
            raise RuntimeError("Incident location history reader returned no result.")
        result = [dict(row) for row in rows]
        for row in result:
            if row.get("incident_id") != incident_id:
                raise ValueError("Location history contains a conflicting incident identity.")
            if not row.get("source_ref") or not row.get("source_event_id"):
                raise ValueError("Location history is missing mandatory provenance.")
        return result


    def prepare_dispatch_address_candidate(
        self, credential: str, incident_id: int, address_id: str, *,
        location_role: str = "primary",
        confidence: str = "unverified", source_ref: str,
    ) -> dict:
        """BP11 dispatch handoff: authorise dispatch intent, then BP12/BP04 reads."""
        self._access._require(
            credential, "bp11.dispatch.location.resolve", f"incident:{incident_id}"
        )
        candidate = self.prepare_address_candidate(
            credential, incident_id, address_id,
            location_role=location_role, confidence=confidence,
            source_ref=source_ref,
        )
        # Dispatch consumes a reference and confidence, not a copied address record.
        return {
            "record_type": "dispatch_incident_location",
            "incident_id": incident_id,
            "incident_ref": candidate["incident_ref"],
            "location_role": candidate["location_role"],
            "address_id": candidate["address_id"],
            "confidence": candidate["confidence"],
            "source_ref": candidate["source_ref"],
            "address_source_ref": candidate["address_source_ref"],
            "dispatch_use_only": True,
        }

    def record_dispatch_address_location(
        self, credential: str, incident_id: int, address_id: str, *,
        dispatch_ref: str, dispatch_incident_verifier, location_writer,
        actor_ref: str, authority_ref: str, idempotency_key: str,
        raw_description: str, location_role: str = "primary",
        confidence: str = "unverified",
    ) -> dict:
        """Record a verified dispatch-originated location through BP12."""
        for name, value in (
            ("dispatch_ref", dispatch_ref), ("actor_ref", actor_ref),
            ("authority_ref", authority_ref), ("idempotency_key", idempotency_key),
            ("raw_description", raw_description),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not callable(location_writer):
            raise TypeError("A trusted BP12 location writer is required")
        if not callable(dispatch_incident_verifier):
            raise TypeError("A trusted BP11 dispatch-to-incident verifier is required")
        self._access._require(
            credential, "bp11.dispatch.location.record", f"incident:{incident_id}"
        )
        self._access._require(
            credential, "bp11.dispatch.inspect.assignment", f"dispatch:{dispatch_ref}"
        )
        if dispatch_incident_verifier(dispatch_ref, incident_id) is not True:
            raise PermissionError("Access denied.")
        candidate = self.prepare_dispatch_address_candidate(
            credential, incident_id, address_id,
            location_role=location_role, confidence=confidence,
            source_ref=f"dispatch:{dispatch_ref}",
        )
        location_id = location_writer(
            p_incident_id=incident_id,
            p_location_role=candidate["location_role"],
            p_location_type="property",
            p_location_ref=address_id,
            p_spatial_id=None,
            p_raw_description=raw_description,
            p_confidence=candidate["confidence"],
            p_actor_ref=actor_ref,
            p_authority_ref=authority_ref,
            p_source_ref=candidate["source_ref"],
            p_address_source_ref=candidate["address_source_ref"],
            p_idempotency_key=idempotency_key,
        )
        return {
            **candidate,
            "dispatch_ref": dispatch_ref,
            "persisted": True,
            "incident_location_id": location_id,
        }

    def record_dispatch_acknowledgement(
        self, credential: str, incident_id: int, *, dispatch_ref: str,
        dispatch_incident_verifier, event_writer, actor_ref: str,
        authority_ref: str, idempotency_key: str, acknowledgement_ref: str,
        description: str,
    ) -> dict:
        """Mirror a verified BP11 acknowledgement into BP12 incident chronology."""
        if not callable(dispatch_incident_verifier) or not callable(event_writer):
            raise TypeError("Trusted BP11 verifier and BP12 event writer are required")
        for name, value in (
            ("dispatch_ref", dispatch_ref), ("actor_ref", actor_ref),
            ("authority_ref", authority_ref), ("idempotency_key", idempotency_key),
            ("acknowledgement_ref", acknowledgement_ref), ("description", description),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        self._access._require(
            credential, "bp11.dispatch.acknowledgement.record", f"incident:{incident_id}"
        )
        self._access._require(
            credential, "bp11.dispatch.inspect.assignment", f"dispatch:{dispatch_ref}"
        )
        if dispatch_incident_verifier(dispatch_ref, incident_id) is not True:
            raise PermissionError("Access denied.")
        event_id = event_writer(
            incident_id=incident_id, event_code="DISPATCH_ACKNOWLEDGED",
            actor_ref=actor_ref, authority_ref=authority_ref,
            source_ref=f"dispatch-ack:{acknowledgement_ref}",
            dispatch_ref=dispatch_ref, unit_ref=None, assignment_ref=None,
            field_activity_ref=None, description=description,
            idempotency_key=idempotency_key,
        )
        return {
            "incident_id": incident_id, "dispatch_ref": dispatch_ref,
            "acknowledgement_ref": acknowledgement_ref,
            "event_code": "DISPATCH_ACKNOWLEDGED", "event_id": event_id,
            "persisted": True,
        }

    def record_field_unit_arrival(
        self, credential: str, incident_id: int, *, unit_ref: str,
        assignment_ref: str, field_activity_ref: str,
        deployment_activity_verifier, event_writer, actor_ref: str,
        authority_ref: str, idempotency_key: str, description: str,
    ) -> dict:
        """Mirror a verified BP10 arrival; BP08/BP10 remain authoritative."""
        if not callable(deployment_activity_verifier) or not callable(event_writer):
            raise TypeError("Trusted BP08/BP10 verifier and BP12 event writer are required")
        for name, value in (
            ("unit_ref", unit_ref), ("assignment_ref", assignment_ref),
            ("field_activity_ref", field_activity_ref), ("actor_ref", actor_ref),
            ("authority_ref", authority_ref), ("idempotency_key", idempotency_key),
            ("description", description),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        self._access._require(
            credential, "bp10.patrol.record_arrival", f"incident:{incident_id}"
        )
        self._access._require(
            credential, "bp08.deployment.inspect.assignment", f"assignment:{assignment_ref}"
        )
        self._access._require(
            credential, "bp10.patrol.inspect.field_activity",
            f"field_activity:{field_activity_ref}",
        )
        if deployment_activity_verifier(
            unit_ref, assignment_ref, field_activity_ref, incident_id
        ) is not True:
            raise PermissionError("Access denied.")
        event_id = event_writer(
            incident_id=incident_id, event_code="UNIT_ARRIVED",
            actor_ref=actor_ref, authority_ref=authority_ref,
            source_ref=f"bp10-arrival:{field_activity_ref}",
            dispatch_ref=None, unit_ref=unit_ref,
            assignment_ref=assignment_ref,
            field_activity_ref=field_activity_ref, description=description,
            idempotency_key=idempotency_key,
        )
        return {
            "incident_id": incident_id, "unit_ref": unit_ref,
            "assignment_ref": assignment_ref,
            "field_activity_ref": field_activity_ref,
            "event_code": "UNIT_ARRIVED", "event_id": event_id,
            "persisted": True,
        }

    def read_operational_timeline(
        self, credential: str, incident_id: int, *, operational_timeline_reader
    ) -> list[dict]:
        """Read verified BP11/BP10 event mirrors under a dedicated BP12 grant."""
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        if not callable(operational_timeline_reader):
            raise TypeError("A trusted BP12 operational timeline reader is required")
        self._access._require(
            credential,
            "bp12.incident.inspect.operational_timeline",
            f"incident:{incident_id}",
        )
        rows = operational_timeline_reader(incident_id)
        if rows is None:
            raise RuntimeError("Incident operational timeline reader returned no result.")
        result = [dict(row) for row in rows]
        allowed_codes = {"DISPATCH_ACKNOWLEDGED", "UNIT_ARRIVED"}
        for row in result:
            if row.get("incident_id") != incident_id:
                raise ValueError("Operational timeline contains a conflicting incident identity.")
            if row.get("event_code") not in allowed_codes:
                raise ValueError("Operational timeline contains an unsupported event.")
            if not row.get("source_ref") or not row.get("event_id"):
                raise ValueError("Operational timeline is missing event provenance.")
            attributes = row.get("attributes")
            if not isinstance(attributes, dict) or not attributes.get("actor_ref") or not attributes.get("authority_ref"):
                raise ValueError("Operational timeline is missing actor or authority provenance.")
        return result

    def build_authorised_command_handover(
        self, credential: str, incident_id: int, *,
        assignment_snapshot_reader, operational_timeline_reader,
    ) -> dict:
        """Build a command handover from independently authorised owner snapshots."""
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        if not callable(assignment_snapshot_reader) or not callable(operational_timeline_reader):
            raise TypeError("Trusted BP08 assignment and BP12 timeline readers are required")
        self._access._require(
            credential, "bp12.incident.inspect.command_handover",
            f"incident:{incident_id}",
        )
        incident = self._incident_reader(incident_id)
        if not isinstance(incident, dict) or incident.get("incident_id") != incident_id:
            raise LookupError("Incident not found.")
        self._access._require(
            credential, "bp08.deployment.inspect.incident_assignments",
            f"incident:{incident_id}",
        )
        snapshot = assignment_snapshot_reader(incident_id)
        if not isinstance(snapshot, dict):
            raise ValueError("BP08 assignment snapshot is invalid.")
        from runtime.bp12_incident_operational_events import reconcile_incident_command_handover
        timeline = self.read_operational_timeline(
            credential, incident_id,
            operational_timeline_reader=operational_timeline_reader,
        )
        return reconcile_incident_command_handover(
            incident_id,
            incident_status=incident.get("status"),
            assignment_snapshot=snapshot.get("assignments"),
            timeline_rows=timeline,
            snapshot_source_ref=snapshot.get("source_ref"),
            as_of_world_tick=snapshot.get("as_of_world_tick"),
        )

    def record_authorised_command_handover(
        self, credential: str, incident_id: int, *,
        assignment_snapshot_reader, operational_timeline_reader,
        handover_fields: dict, handover_writer, idempotency_key: str,
    ) -> dict:
        """Persist a ready handover after separate audited domain permissions."""
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        if not isinstance(handover_fields, dict):
            raise TypeError("Validated handover fields must be supplied as a mapping.")
        if not callable(getattr(handover_writer, "record", None)):
            raise TypeError("A trusted BP12 command handover writer is required.")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ValueError("A handover idempotency key is required.")
        self._access._require(
            credential, "bp12.incident.record.command_handover",
            f"incident:{incident_id}",
        )
        reconciliation = self.build_authorised_command_handover(
            credential, incident_id,
            assignment_snapshot_reader=assignment_snapshot_reader,
            operational_timeline_reader=operational_timeline_reader,
        )
        from runtime.bp12_incident_operational_events import build_incident_command_handover_record
        document = build_incident_command_handover_record(
            reconciliation=reconciliation, **handover_fields
        )
        if document.get("incident_id") != incident_id:
            raise ValueError("Handover projection incident identity does not match the authorised incident.")
        if document.get("handover_ready") is not True:
            raise ValueError("Incident command handover is not ready for persistence.")
        record_id = handover_writer.record(
            document, idempotency_key=idempotency_key
        )
        if type(record_id) is not int or record_id < 1:
            raise RuntimeError("BP12 command handover writer returned an invalid record ID.")
        return {
            **document,
            "record_status": "PERSISTED",
            "read_only": True,
            "persisted": True,
            "command_handover_id": record_id,
        }

    def read_authorised_command_handover_history(
        self, credential: str, incident_id: int, *, history_reader,
    ) -> list[dict]:
        """Read BP12's append-only command handover history under its own grant."""
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        if not callable(getattr(history_reader, "read", None)):
            raise TypeError("A trusted BP12 command handover history reader is required.")
        self._access._require(
            credential, "bp12.incident.inspect.command_handover.history",
            f"incident:{incident_id}",
        )
        rows = history_reader.read(incident_id)
        if not isinstance(rows, list):
            raise RuntimeError("BP12 command handover history reader returned an invalid result.")
        for row in rows:
            if not isinstance(row, dict) or row.get("incident_id") != incident_id:
                raise ValueError("Command handover history contains a conflicting incident identity.")
            if not row.get("source_ref") or not row.get("source_event_id"):
                raise ValueError("Command handover history is missing mandatory provenance.")
            document = row.get("handover_document")
            if not isinstance(document, dict) or document.get("record_status") != "PERSISTED":
                raise ValueError("Command handover history contains an invalid persisted document.")
        return rows

    def read_investigation_location_history(
        self, credential: str, incident_id: int, *, case_ref: str,
        case_incident_verifier, location_history_reader,
    ) -> list[dict]:
        """BP16 handoff: prove case linkage before BP12 history access."""
        if not isinstance(case_ref, str) or not case_ref.strip():
            raise ValueError("A stable case reference is required.")
        if not callable(case_incident_verifier):
            raise TypeError("A trusted case-to-incident verifier is required")
        self._access._require(
            credential, "bp16.investigation.inspect.case", f"case:{case_ref}"
        )
        if case_incident_verifier(case_ref, incident_id) is not True:
            raise PermissionError("Access denied.")
        self._access._require(
            credential,
            "bp16.investigation.incident.location.history",
            f"incident:{incident_id}",
        )
        return self.read_location_history(
            credential, incident_id,
            location_history_reader=location_history_reader,
        )


def create_postgres_bp04_police_lookup_access(
    connect,
    lookup: Any,
    principal_id: UUID,
) -> BP04PoliceLookupAccess:
    """Compose officer access with live PostgreSQL grants and durable audit.

    This factory creates no grants and performs no migration. Every attempted
    read verifies the opaque session, reloads current grants and appends an
    authorization decision through PostgresAuditSink. The caller must provide
    the trusted database connection factory and the already-built shared
    process-local BP04Lookup instance.
    """
    from runtime.postgres_security import (
        PostgresAuditSink,
        PostgresGrantProvider,
        PostgresSessionVerifier,
    )

    authorization = AuthorizationService(
        PostgresSessionVerifier(connect),
        PostgresAuditSink(connect),
        PostgresGrantProvider(connect),
    )
    return BP04PoliceLookupAccess(lookup, authorization, principal_id)
