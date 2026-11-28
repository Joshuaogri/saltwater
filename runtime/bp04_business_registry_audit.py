"""Deterministic acceptance audit for BP04's canonical business register."""
from __future__ import annotations

from collections import Counter

from runtime.naming import normalize_name


def audit_business_registry(registry: dict, *, property_world_document: dict | None = None, geography: dict | None = None) -> dict:
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
    allowed_lifecycle_statuses = {"active", "seasonal", "temporarily_inactive"}
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
        if row["status"] not in allowed_lifecycle_statuses:
            raise ValueError(f"business {business_id} has an unknown lifecycle status")
        if type(row.get("year_established")) is not int or not 1985 <= row["year_established"] <= 2026:
            raise ValueError(f"business {business_id} has an implausible establishment year")
        expected_employee_bands = {"micro": "1-4", "small": "5-19", "medium": "20-99", "large": "100-499"}
        if row.get("employee_band") != expected_employee_bands.get(row.get("business_size")):
            raise ValueError(f"business {business_id} has an employee band inconsistent with its size")
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
                if type(link.get("valid_from_tick")) is not int or link["valid_from_tick"] < 0:
                    raise ValueError(f"business {business_id} occupancy link has an invalid start tick")
                if link.get("valid_to_tick") is not None and (
                    type(link["valid_to_tick"]) is not int
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

    lifecycle_total = sum(lifecycle_counts.values())
    if lifecycle_total != len(businesses):
        raise ValueError("business lifecycle classes do not reconcile to the total registry")
    embedded_summary = registry.get("summary")
    if not isinstance(embedded_summary, dict):
        raise ValueError("business registry summary is missing")
    expected_lifecycle_counts = {
        "active": embedded_summary.get("active_businesses"),
        "seasonal": embedded_summary.get("seasonal_businesses"),
        "temporarily_inactive": embedded_summary.get("temporarily_inactive_businesses"),
    }
    if any(type(value) is not int or value < 0 for value in expected_lifecycle_counts.values()):
        raise ValueError("business registry lifecycle summary counts are incomplete")
    if {status: lifecycle_counts[status] for status in allowed_lifecycle_statuses} != expected_lifecycle_counts:
        raise ValueError("business lifecycle class counts do not match the registry summary")
    if embedded_summary.get("distinct_business_count") != len(businesses):
        raise ValueError("business registry summary total does not match business identities")

    summary = {
        "business_count": len(businesses),
        "active_businesses": lifecycle_counts["active"],
        "seasonal_businesses": lifecycle_counts["seasonal"],
        "temporarily_inactive_businesses": lifecycle_counts["temporarily_inactive"],
        "lifecycle_count_total": lifecycle_total,
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
    if (property_world_document is None) != (geography is None):
        raise ValueError("property-world and geography references must be supplied together")
    if property_world_document is not None and geography is not None:
        summary["spatial_lineage"] = audit_business_registry_spatial_lineage(
            registry, property_world_document, geography
        )
    return summary


def audit_business_registry_spatial_lineage(
    registry: dict, property_world_document: dict, geography: dict
) -> dict:
    """Resolve every business address and establishment through canonical BP04/BP02 IDs."""
    if property_world_document.get("schema") != "saltwater-canonical-property-world-columnar/1.0":
        raise ValueError("unsupported canonical property-world archive schema")
    metadata = property_world_document.get("metadata")
    tables = property_world_document.get("tables")
    if not isinstance(metadata, dict) or not isinstance(tables, dict):
        raise ValueError("canonical property-world metadata or tables are missing")
    if (
        metadata.get("dataset_id") != "SW-PROPERTY-WORLD-V1"
        or metadata.get("canon_status") != "CANONICAL_FICTIONAL_GAME_WORLD"
        or metadata.get("generator") != "SW-PROPERTY-WORLD-GENERATOR-001"
    ):
        raise ValueError("canonical property-world identity, canon status or generator mismatch")
    lineage = metadata.get("lineage")
    if not isinstance(lineage, dict) or lineage.get("fictional_world_facts") is not True:
        raise ValueError("canonical property-world provenance is not fictional game canon")
    if lineage.get("source_geography_dataset") != geography.get("dataset_id"):
        raise ValueError("property-world and geography source dataset identities do not match")

    def index(table_name: str, key_field: str, fields: tuple[str, ...]) -> dict:
        table = tables.get(table_name)
        if not isinstance(table, dict) or not isinstance(table.get("columns"), list) or not isinstance(table.get("rows"), list):
            raise ValueError(f"canonical property-world {table_name} table is missing")
        columns = table["columns"]
        try:
            key_index = columns.index(key_field)
            field_indexes = tuple(columns.index(field) for field in fields)
        except ValueError as exc:
            raise ValueError(f"canonical property-world {table_name} table lacks a required field") from exc
        result = {}
        for row in table["rows"]:
            if len(row) != len(columns):
                raise ValueError(f"canonical property-world {table_name} row width mismatch")
            key = row[key_index]
            if not isinstance(key, str) or not key.strip() or key in result:
                raise ValueError(f"canonical property-world {table_name} has an invalid or duplicate identity")
            result[key] = tuple(row[i] for i in field_indexes)
        return result

    properties = index("properties", "property_id", ("address_id",))
    addresses = index("addresses", "address_id", ("property_id", "district_id", "neighbourhood_id"))
    buildings = index("buildings", "building_id", ("property_id", "address_id"))
    premises = index("premises", "premises_id", ("property_id", "building_id", "address_id"))
    units = index("units", "unit_id", ("property_id", "building_id", "premises_id", "address_id"))

    districts = geography.get("districts")
    neighbourhoods = geography.get("neighbourhoods")
    if not isinstance(districts, list) or not isinstance(neighbourhoods, list):
        raise ValueError("BP02 district and neighbourhood inventories are missing")
    district_ids = {row.get("id") for row in districts}
    neighbourhood_ids = {row.get("id") for row in neighbourhoods}
    if None in district_ids or None in neighbourhood_ids:
        raise ValueError("BP02 geography contains a missing district or neighbourhood identity")

    establishments = {row["establishment_id"]: row for row in registry["establishments"]}
    for business in registry["businesses"]:
        primary = establishments[business["primary_establishment_id"]]
        address = addresses.get(business["registered_address_id"])
        if address is None:
            raise ValueError(f"business {business['business_id']} references an unknown canonical address")
        if address[0] != primary["property_id"]:
            raise ValueError(f"business {business['business_id']} registered address belongs to another property")

    for establishment in registry["establishments"]:
        establishment_id = establishment["establishment_id"]
        property_id = establishment["property_id"]
        building_id = establishment["building_id"]
        premises_id = establishment["premises_id"]
        unit_id = establishment["unit_id"]
        address_id = establishment["address_id"]
        district_id = establishment["district_id"]
        neighbourhood_id = establishment["neighbourhood_id"]

        prop = properties.get(property_id)
        building = buildings.get(building_id)
        premise = premises.get(premises_id)
        unit = units.get(unit_id)
        address = addresses.get(address_id)
        if prop is None or building is None or premise is None or unit is None or address is None:
            raise ValueError(f"establishment {establishment_id} has an off-map or unknown property/building/premises/unit/address reference")
        if prop[0] != address_id:
            raise ValueError(f"establishment {establishment_id} address does not match its canonical property")
        if building != (property_id, address_id):
            raise ValueError(f"establishment {establishment_id} building does not belong to its property/address")
        if premise != (property_id, building_id, address_id):
            raise ValueError(f"establishment {establishment_id} premises does not belong to its building/property/address")
        if unit != (property_id, building_id, premises_id, address_id):
            raise ValueError(f"establishment {establishment_id} unit does not belong to its premises/building/property/address")
        if address != (property_id, district_id, neighbourhood_id):
            raise ValueError(f"establishment {establishment_id} address district/neighbourhood lineage mismatch")
        if district_id not in district_ids or neighbourhood_id not in neighbourhood_ids:
            raise ValueError(f"establishment {establishment_id} references an unknown BP02 district/neighbourhood")

    return {
        "businesses_checked": len(registry["businesses"]),
        "establishments_checked": len(registry["establishments"]),
        "canonical_properties_checked": len({row["property_id"] for row in registry["establishments"]}),
        "canonical_buildings_checked": len({row["building_id"] for row in registry["establishments"]}),
        "canonical_premises_checked": len({row["premises_id"] for row in registry["establishments"]}),
        "canonical_units_checked": len({row["unit_id"] for row in registry["establishments"]}),
        "canonical_addresses_checked": len({row["address_id"] for row in registry["establishments"]}),
        "districts_referenced": len({row["district_id"] for row in registry["establishments"]}),
        "neighbourhoods_referenced": len({row["neighbourhood_id"] for row in registry["establishments"]}),
        "exception_count": 0,
        "validation_status": "PASS",
    }
