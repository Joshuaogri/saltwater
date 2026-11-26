"""Deterministic acceptance audit for BP04's canonical business register."""
from __future__ import annotations

from collections import Counter

from runtime.naming import normalize_name


def audit_business_registry(registry: dict) -> dict:
    """Audit business identity, local scope, lifecycle and establishment lineage.

    This is a read-only source audit. It does not persist reservations, create
    people, or promote property/access records into operational status.
    """
    businesses = registry.get("businesses")
    establishments = registry.get("establishments")
    links = registry.get("business_unit_links")
    if not all(isinstance(rows, list) for rows in (businesses, establishments, links)):
        raise ValueError("businesses, establishments and business_unit_links must be lists")

    business_ids = [row.get("business_id") for row in businesses]
    establishment_ids = [row.get("establishment_id") for row in establishments]
    link_ids = [row.get("business_unit_link_id") for row in links]
    if any(not isinstance(value, str) or not value.strip() for values in (business_ids, establishment_ids, link_ids) for value in values):
        raise ValueError("all business, establishment and link identities must be non-empty text")
    if len(set(business_ids)) != len(business_ids):
        raise ValueError("duplicate business identity")
    if len(set(establishment_ids)) != len(establishment_ids):
        raise ValueError("duplicate establishment identity")
    if len(set(link_ids)) != len(link_ids):
        raise ValueError("duplicate business-unit link identity")

    by_business = {row["business_id"]: row for row in businesses}
    establishments_by_business: dict[str, list[dict]] = {}
    for row in establishments:
        business_id = row.get("business_id")
        if business_id not in by_business:
            raise ValueError(f"orphan establishment: {row.get('establishment_id')}")
        establishments_by_business.setdefault(business_id, []).append(row)

    links_by_business: dict[str, list[dict]] = {}
    for row in links:
        business_id = row.get("business_id")
        if business_id not in by_business:
            raise ValueError(f"orphan business-unit link: {row.get('business_unit_link_id')}")
        links_by_business.setdefault(business_id, []).append(row)

    public_names: dict[str, tuple[str, str]] = {}
    sector_counts = Counter()
    lifecycle_counts = Counter()
    for row in businesses:
        business_id = row["business_id"]
        for field in ("registered_name", "trading_name", "sector", "primary_activity", "legal_form", "business_size", "status", "registered_address_id", "primary_establishment_id", "source_generator"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"business {business_id} has missing {field}")
        if row.get("registered_city") != "Saltwater" or row.get("fictional_entity") is not True:
            raise ValueError(f"business {business_id} is not explicitly local Saltwater canon")
        if row.get("person_records_created") != 0:
            raise ValueError(f"business {business_id} improperly creates person records")
        if any(char.isdigit() for char in row["registered_name"] + row["trading_name"]):
            raise ValueError(f"business {business_id} contains a numeric placeholder name")
        for field in ("registered_name", "trading_name"):
            key = normalize_name(row[field])
            prior = public_names.get(key)
            if prior:
                raise ValueError(f"global public-name collision between {prior[0]} and {business_id}")
            public_names[key] = (business_id, field)
        sector_counts[row["sector"]] += 1
        lifecycle_counts[row["status"]] += 1

        owned_establishments = establishments_by_business.get(business_id, [])
        owned_links = links_by_business.get(business_id, [])
        if len(owned_establishments) != 1 or len(owned_links) != 1:
            raise ValueError(f"business {business_id} must have one primary establishment and one source occupancy link")
        establishment = owned_establishments[0]
        link = owned_links[0]
        if establishment["establishment_id"] != row["primary_establishment_id"]:
            raise ValueError(f"business {business_id} primary establishment reference mismatch")
        if establishment.get("address_id") != row["registered_address_id"]:
            raise ValueError(f"business {business_id} registered address differs from establishment address")
        for field in ("unit_id", "premises_id", "property_id", "building_id", "address_id"):
            if not isinstance(establishment.get(field), str) or not establishment[field].strip():
                raise ValueError(f"establishment {establishment['establishment_id']} lacks {field}")
        if link.get("establishment_id") != establishment["establishment_id"] or link.get("unit_id") != establishment["unit_id"] or link.get("premises_id") != establishment["premises_id"]:
            raise ValueError(f"business {business_id} occupancy link does not match its establishment")
        if link.get("occupancy_relationship") != "business_operator":
            raise ValueError(f"business {business_id} has an invalid occupancy relationship")
        if establishment.get("operating_status") != row["status"]:
            raise ValueError(f"business {business_id} and establishment lifecycle status differ")

    summary = {
        "business_count": len(businesses),
        "distinct_business_ids": len(set(business_ids)),
        "establishment_count": len(establishments),
        "distinct_establishment_ids": len(set(establishment_ids)),
        "business_unit_link_count": len(links),
        "distinct_business_unit_link_ids": len(set(link_ids)),
        "public_name_count": len(public_names),
        "businesses_by_sector": dict(sorted(sector_counts.items())),
        "businesses_by_lifecycle_status": dict(sorted(lifecycle_counts.items())),
        "multi_establishment_businesses": sum(1 for rows in establishments_by_business.values() if len(rows) > 1),
        "local_saltwater_businesses": sum(1 for row in businesses if row.get("registered_city") == "Saltwater"),
        "person_records_created": sum(row.get("person_records_created", 0) for row in businesses),
        "persistent_name_reservations_performed": False,
        "operational_property_access_approval": False,
    }
    summary["valid_10k_business_minimum"] = summary["business_count"] >= 10000 and summary["distinct_business_ids"] == summary["business_count"] and summary["local_saltwater_businesses"] == summary["business_count"]
    return summary
