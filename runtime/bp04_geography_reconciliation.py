"""Read-only BP04-to-BP02 source reconciliation; never promotes candidates to canon.

BP-02 currently has stable IDs for the 100 source geography entities, but its
operational parcel/address identities are not yet approved or materialised.
This audit reconciles property source links to the generated parcel candidates
and checks district/neighbourhood/road context against BP-02 entity_code values.
It explicitly leaves every BP04 address non-canonical until BP-02 supplies
approved parcel and address identities.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterable

from runtime.geography_identity_reconciliation import validate_identity_map
from runtime.parcel_candidate_generator import build_candidates
from runtime.bp02_parcel_address_identity import build_identity_register
from runtime.bp02_address_access_reconciliation import reconcile_building_access_roads
from runtime.bp02_address_review_register import build_address_review_register
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory

ROOT = Path(__file__).resolve().parents[1]
GEO_PATH = ROOT / "data/geography/saltwater-geography-v1.json"
IDENTITY_MAP_PATH = ROOT / "data/geography/saltwater-geography-v1-identity-map.json"
PROPERTY_WORLD_PATH = ROOT / "data/property/saltwater-property-world-v1.json.gz"


def _read_columnar_gzip(path: Path) -> dict:
    document = json.loads(gzip.decompress(path.read_bytes()))
    if document.get("storage_format") != "textual_json_columnar_v1":
        raise ValueError(f"Unsupported BP04 source format: {path}")
    if not isinstance(document.get("tables"), dict):
        raise ValueError(f"Malformed BP04 source document: {path}")
    return document


def _rows(document: dict, collection: str) -> list[dict]:
    table = document.get("tables", {}).get(collection)
    if not isinstance(table, dict):
        raise ValueError(f"Missing BP04 collection: {collection}")
    columns, values = table.get("columns"), table.get("rows")
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"Malformed BP04 collection: {collection}")
    result = []
    for index, row in enumerate(values):
        if not isinstance(row, list) or len(row) != len(columns):
            raise ValueError(f"Malformed BP04 row {collection}[{index}]")
        result.append(dict(zip(columns, row)))
    return result


def reconcile_collections(
    properties: Iterable[dict],
    addresses: Iterable[dict],
    candidate_parcel_ids: set[str],
    geography_entity_codes: set[str],
    canonical_parcel_codes: set[str] | None = None,
    canonical_address_codes: set[str] | None = None,
    canonical_parcel_by_candidate: dict[str, str] | None = None,
    canonical_address_by_source: dict[str, str] | None = None,
) -> dict:
    properties, addresses = list(properties), list(addresses)
    canonical_parcel_codes = canonical_parcel_codes or set()
    canonical_address_codes = canonical_address_codes or set()
    canonical_parcel_by_candidate = canonical_parcel_by_candidate or {}
    canonical_address_by_source = canonical_address_by_source or {}

    property_by_id = {}
    for row in properties:
        identifier = row.get("property_id")
        if not identifier or identifier in property_by_id:
            raise ValueError(f"Missing or duplicate BP04 property ID: {identifier}")
        property_by_id[identifier] = row

    address_by_id = {}
    for row in addresses:
        identifier = row.get("address_id")
        if not identifier or identifier in address_by_id:
            raise ValueError(f"Missing or duplicate BP04 address ID: {identifier}")
        address_by_id[identifier] = row

    candidate_links = 0
    property_address_links = 0
    district_matches = 0
    neighbourhood_matches = 0
    road_matches = 0
    errors = []

    for prop in properties:
        parcel_id = prop.get("source_candidate_parcel_id")
        if parcel_id not in candidate_parcel_ids:
            errors.append(f"{prop['property_id']}: source parcel candidate is unresolved: {parcel_id}")
        else:
            candidate_links += 1

        address_id = prop.get("address_id")
        address = address_by_id.get(address_id)
        if address is None or address.get("property_id") != prop["property_id"]:
            errors.append(f"{prop['property_id']}: primary BP04 address link is missing or inconsistent")
            continue
        property_address_links += 1

        if prop.get("source_district_id") != address.get("district_id"):
            errors.append(f"{prop['property_id']}: district context differs between property and address")
        if prop.get("source_neighbourhood_id") != address.get("neighbourhood_id"):
            errors.append(f"{prop['property_id']}: neighbourhood context differs between property and address")

        if prop.get("source_district_id") in geography_entity_codes:
            district_matches += 1
        else:
            errors.append(f"{prop['property_id']}: district ID is not a BP-02 entity_code")
        if prop.get("source_neighbourhood_id") in geography_entity_codes:
            neighbourhood_matches += 1
        else:
            errors.append(f"{prop['property_id']}: neighbourhood ID is not a BP-02 entity_code")
        if address.get("road_id") in geography_entity_codes:
            road_matches += 1
        else:
            errors.append(f"{address_id}: road ID is not a BP-02 entity_code")

    orphan_addresses = sorted(
        identifier for identifier, row in address_by_id.items()
        if row.get("property_id") not in property_by_id
    )
    if orphan_addresses:
        errors.append(f"orphan BP04 addresses: {orphan_addresses[:10]}")

    if errors:
        raise ValueError("\\n".join(errors))

    canonical_parcel_matches = sum(
        1 for row in properties
        if row.get("source_candidate_parcel_id") in canonical_parcel_codes
    )
    canonical_address_matches = sum(
        1 for row in addresses if row.get("address_id") in canonical_address_codes
    )
    design_parcel_matches = sum(
        1 for row in properties
        if row.get("source_candidate_parcel_id") in canonical_parcel_by_candidate
    )
    design_address_matches = sum(
        1 for row in addresses if row.get("address_id") in canonical_address_by_source
    )
    return {
        "property_records": len(properties),
        "address_records": len(addresses),
        "generated_candidate_parcel_links_resolved": candidate_links,
        "primary_property_address_links_resolved": property_address_links,
        "district_entity_code_matches": district_matches,
        "neighbourhood_entity_code_matches": neighbourhood_matches,
        "road_entity_code_matches": road_matches,
        "canonical_parcel_identity_matches": canonical_parcel_matches,
        "canonical_address_identity_matches": canonical_address_matches,
        "properties_still_awaiting_bp02_parcel_binding": len(properties) - canonical_parcel_matches,
        "bp02_design_parcel_identity_matches": design_parcel_matches,
        "addresses_still_awaiting_bp02_address_binding": len(addresses) - canonical_address_matches,
        "bp02_design_address_identity_matches": design_address_matches,
        "canonical_binding_status": (
            "DESIGN_IDENTITIES_BOUND_OPERATIONAL_RELEASE_BLOCKED" if design_parcel_matches == len(properties)
            and design_address_matches == len(addresses)
            else "BLOCKED_BP02_CANONICAL_PARCEL_AND_ADDRESS_IDENTITIES_ABSENT"
        ),
        "address_promotion_performed": False,
        "operational_approval": False,
        "database_write_performed": False,
    }


def build_reconciliation(geo: dict, identity_map: dict, property_document: dict) -> dict:
    identity_result = validate_identity_map(geo, identity_map)
    candidate_manifest = build_candidates(geo)
    parcel_dossiers = build_parcel_dossiers(geo, candidate_manifest)
    physical_assets = build_asset_inventory(geo, candidate_manifest, parcel_dossiers)
    candidate_ids = {
        row["candidate_parcel_id"] for row in candidate_manifest["parcels"]
    }
    codes = {row["entity_code"] for row in identity_map.get("entries", [])}
    types = {
        row["entity_type"]: set()
        for row in identity_map.get("entries", [])
    }
    for row in identity_map.get("entries", []):
        types.setdefault(row["entity_type"], set()).add(row["entity_code"])

    properties = _rows(property_document, "properties")
    addresses = _rows(property_document, "addresses")
    road_segment_to_road = {
        segment["id"]: segment["road_id"]
        for segment in geo.get("network", {}).get("segments", [])
    }
    identity_register = build_identity_register(
        candidate_manifest, properties, addresses, codes, road_segment_to_road
    )
    parcel_map = {
        row["source_candidate_parcel_id"]: row["parcel_id"]
        for row in identity_register["parcels"]
    }
    address_map = {
        row["source_address_id"]: row["address_id"]
        for row in identity_register["addresses"]
    }
    result = reconcile_collections(
        properties, addresses, candidate_ids, codes,
        types.get("PARCEL", set()), types.get("ADDRESS", set()),
        parcel_map, address_map,
    )
    building_access_reconciliation = reconcile_building_access_roads(
        properties, addresses, parcel_dossiers, physical_assets
    )
    address_review_register = build_address_review_register(
        identity_register, building_access_reconciliation
    )
    frontage_counts = {}
    for address in identity_register["addresses"]:
        status = address["road_frontage_match_status"]
        frontage_counts[status] = frontage_counts.get(status, 0) + 1
    road_candidate_counts = {}
    for address in identity_register["addresses"]:
        status = address["address_road_candidate_status"]
        road_candidate_counts[status] = road_candidate_counts.get(status, 0) + 1
    frontage_exceptions = [
        {
            "source_address_id": row["source_address_id"],
            "property_id": row["property_id"],
            "source_candidate_parcel_id": row["source_candidate_parcel_id"],
            "source_road_id": row["road_id"],
            "candidate_frontage_road_ids": row["candidate_frontage_road_ids"],
            "address_road_candidate_id": row["address_road_candidate_id"],
            "status": row["road_frontage_match_status"],
        }
        for row in identity_register["addresses"]
        if row["road_frontage_match_status"] not in (
            "ROAD_MATCHES_PARCEL_FRONTAGE_CANDIDATE", "NOT_EVALUATED"
        )
    ]
    building_access_by_address = {
        row["source_address_id"]: row
        for row in building_access_reconciliation["address_access_road_results"]
    }
    frontage_exception_crosscheck = []
    for row in frontage_exceptions:
        access_row = building_access_by_address.get(row["source_address_id"])
        frontage_exception_crosscheck.append({
            **row,
            "building_access_road_candidate_status": (
                access_row["status"] if access_row else "NOT_FOUND"
            ),
            "building_access_road_candidate_id": (
                access_row["address_access_road_candidate_id"] if access_row else None
            ),
            "building_access_road_candidate_ids": (
                access_row["candidate_access_road_ids"] if access_row else []
            ),
            "building_access_road_candidate_details": (
                access_row["candidate_access_road_details"] if access_row else {}
            ),
        })
    result.update({
        "bp02_address_placement_review_register": address_review_register,
        "building_access_road_candidate_status_counts": building_access_reconciliation["address_access_road_candidate_status_counts"],
        "building_access_road_candidate_references_resolved": building_access_reconciliation["address_access_road_candidate_references_resolved"],
        "building_access_candidate_unresolved_access_points": building_access_reconciliation["unresolved_building_access_point_count"],
        "building_access_road_exceptions": [
            row for row in building_access_reconciliation["address_access_road_results"]
            if row["status"] != "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET"
        ],
        "building_access_asset_counts": {
            "properties": len(physical_assets.get("properties", [])),
            "buildings": len(physical_assets.get("buildings", [])),
            "building_boundary_access_candidates": len(physical_assets.get("access_points", [])),
        },
        "address_road_frontage_candidate_status_counts": frontage_counts,
        "address_road_candidate_status_counts": road_candidate_counts,
        "address_road_candidate_references_resolved": sum(
            1 for row in identity_register["addresses"] if row["address_road_candidate_id"]
        ),
        "address_road_frontage_exceptions": frontage_exceptions,
        "address_frontage_exceptions_building_access_crosscheck": frontage_exception_crosscheck,
        "bp02_design_parcel_identity_count": identity_register["parcel_identity_count"],
        "bp02_design_address_identity_count": identity_register["address_identity_count"],
        "bp02_design_identity_register": identity_register["register_id"],
        "operational_identity_release_approved": identity_register["operational_approval"],
        "audit": "BP04-TO-BP02-ADDRESS-RECONCILIATION",
        "source_geography_dataset": geo.get("dataset_id"),
        "source_geography_status": geo.get("status"),
        "source_identity_map_records": identity_result["resolved"],
        "candidate_parcel_set_id": candidate_manifest["candidate_set_id"],
        "candidate_parcel_count": len(candidate_ids),
        "candidate_manifest_sha256": candidate_manifest["manifest_sha256"],
        "bp02_canonical_parcel_identity_count": len(types.get("PARCEL", set())),
        "bp02_canonical_address_identity_count": len(types.get("ADDRESS", set())),
        "limitations": [
            "Stable BP-02 parcel and address design identities now bind all source records; geometry and address facts remain unapproved for operational release.",
            "Source street labels and numbers remain unverified; no missing address attributes are invented.",
            "District, neighbourhood and road context resolves to stable BP-02 entity_code values only.",
            "No spatial_id surrogate is fabricated or copied from a disposable database.",
            "No canonical address is promoted and no production database is written.",
        ],
    })
    return result


def main() -> None:
    geo = json.loads(GEO_PATH.read_text(encoding="utf-8"))
    identity_map = json.loads(IDENTITY_MAP_PATH.read_text(encoding="utf-8"))
    property_document = _read_columnar_gzip(PROPERTY_WORLD_PATH)
    print(json.dumps(build_reconciliation(geo, identity_map, property_document), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
