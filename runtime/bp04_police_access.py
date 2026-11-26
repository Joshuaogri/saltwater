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
