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
