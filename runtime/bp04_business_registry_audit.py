"""Deterministic acceptance audit for BP04's canonical business register."""
from __future__ import annotations

from collections import Counter

from runtime.naming import normalize_name


def audit_business_registry(registry: dict) -> dict:
    """Audit distinct business identities without counting branches or names as businesses.

    Establishments and occupancy links are separate child records. A business may
    have multiple establishments (including branches), each with its own address
    and unit link, while exactly one establishment remains its registered primary
    establishment. Brand and alias records, when supplied by another owning
    register, never contribute to the business identity count.
    """
    businesses = registry.get("businesses")
    establishments = registry.get("establishments")
    links = registry.get("business_unit_links")
    if not all(isinstance(rows, list) for rows in (businesses, establishments, links)):
        raise ValueError("businesses, establishments and business_unit_links must be lists")
    if registry.get("schema") != "saltwater-business-registry/1.0":
        raise ValueError("unsupported business registry schema")
    if registry.get("dataset_id") != "SW-BUSINESS-REGISTRY-V1":
        raise ValueError("unexpected business registry dataset identity")
    if registry.get("canon_status") != "CANONICAL_FICTIONAL_GAME_WORLD":
        raise ValueError("business registry is not marked as fictional game-world canon")
    if registry.get("city") != "Saltwater" or registry.get("generator") != "SW-BUSINESS-REGISTRY-GENERATOR-002":
        raise ValueError("business registry city or generator provenance mismatch")

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
    establishments_by_id: dict[str, dict] = {}
    for row in establishments:
        business_id = row.get("business_id")
        if business_id not in by_business:
            raise ValueError(f"orphan establishment: {row.get('establishment_id')}")
        establishments_by_business.setdefault(business_id, []).append(row)
        establishments_by_id[row["establishment_id"]] = row

    links_by_establishment: dict[str, list[dict]] = {}
    for row in links:
        business_id = row.get("business_id")
        if business_id not in by_business:
            raise ValueError(f"orphan business-unit link: {row.get('business_unit_link_id')}")
        establishment_id = row.get("establishment_id")
        establishment = establishments_by_id.get(establishment_id)
        if establishment is None:
            raise ValueError(f"orphan business-unit link establishment: {row.get('business_unit_link_id')}")
        if establishment.get("business_id") != business_id:
            raise ValueError(f"business-unit link owner mismatch: {row.get('business_unit_link_id')}")
        links_by_establishment.setdefault(establishment_id, []).append(row)

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
        if row.get("source_generator") != registry["generator"]:
            raise ValueError(f"business {business_id} has mismatched generator provenance")
        if not business_id.startswith("SWBIZ-") or not business_id[6:].isdigit():
            raise ValueError(f"business {business_id} does not use the stable text identity format")
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
        if not owned_establishments:
            raise ValueError(f"business {business_id} must have at least one establishment")
        primary_matches = [
            establishment for establishment in owned_establishments
            if establishment["establishment_id"] == row["primary_establishment_id"]
        ]
        if len(primary_matches) != 1:
            raise ValueError(f"business {business_id} must reference exactly one owned primary establishment")
        primary_establishment = primary_matches[0]
        if primary_establishment.get("address_id") != row["registered_address_id"]:
            raise ValueError(f"business {business_id} registered address differs from its primary establishment address")

        for establishment in owned_establishments:
            establishment_id = establishment["establishment_id"]
            for field in ("unit_id", "premises_id", "property_id", "building_id", "address_id", "district_id", "neighbourhood_id", "operating_status", "source_generator"):
                if not isinstance(establishment.get(field), str) or not establishment[field].strip():
                    raise ValueError(f"establishment {establishment_id} lacks {field}")
            if establishment["source_generator"] != registry["generator"]:
                raise ValueError(f"establishment {establishment_id} has mismatched generator provenance")
            if not establishment_id.startswith("SWEST-"):
                raise ValueError(f"establishment {establishment_id} does not use the stable text identity format")
            establishment_links = links_by_establishment.get(establishment_id, [])
            if not establishment_links:
                raise ValueError(f"establishment {establishment_id} lacks an occupancy link")
            current_links = [link for link in establishment_links if link.get("valid_to_tick") is None]
            if len(current_links) != 1:
                raise ValueError(f"establishment {establishment_id} must have exactly one current occupancy link")
            for link in establishment_links:
                if link.get("unit_id") != establishment["unit_id"] or link.get("premises_id") != establishment["premises_id"]:
                    raise ValueError(f"business {business_id} occupancy link does not match establishment {establishment_id}")
                if link.get("occupancy_relationship") != "business_operator":
                    raise ValueError(f"establishment {establishment_id} has an invalid occupancy relationship")
                if not isinstance(link.get("valid_from_tick"), int) or link["valid_from_tick"] < 0:
                    raise ValueError(f"business {business_id} occupancy link has an invalid start tick")
                if link.get("valid_to_tick") is not None and (
                    not isinstance(link["valid_to_tick"], int)
                    or link["valid_to_tick"] < link["valid_from_tick"]
                ):
                    raise ValueError(f"business {business_id} occupancy link has an invalid end tick")
                expected_occupancy_status = row["status"]
                if link.get("valid_to_tick") is None and link.get("occupancy_status") != expected_occupancy_status:
                    raise ValueError(f"business {business_id} current occupancy lifecycle status mismatch")

        if primary_establishment.get("operating_status") != row["status"]:
            raise ValueError(f"business {business_id} and primary establishment lifecycle status differ")

    current_unit_occupants: dict[str, str] = {}
    for link in links:
        if link.get("valid_to_tick") is not None:
            continue
        unit_id = link["unit_id"]
        prior_business = current_unit_occupants.get(unit_id)
        if prior_business is not None and prior_business != link["business_id"]:
            raise ValueError(f"unit {unit_id} has overlapping exclusive business occupancy")
        current_unit_occupants[unit_id] = link["business_id"]

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
        "brand_records_not_counted_as_businesses": len(registry.get("brands", [])),
        "alias_records_not_counted_as_businesses": len(registry.get("business_aliases", [])),
        "persistent_name_reservations_performed": False,
        "operational_property_access_approval": False,
    }
    summary["valid_10k_business_minimum"] = summary["business_count"] >= 10000 and summary["distinct_business_ids"] == summary["business_count"] and summary["local_saltwater_businesses"] == summary["business_count"]
    return summary
