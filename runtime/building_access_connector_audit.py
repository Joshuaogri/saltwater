"""Read-only feasibility audit for direct building-to-parcel-frontage connector candidates.

A geometrically feasible straight connector is not a driveway, entrance, legal access,
or traversable route. The audit never creates operational access facts or writes a DB.
"""
from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, shape


def _polygon(record):
    return Polygon(record["geometry"][0], record["geometry"][1:])


def audit_direct_access_connectors(source: dict, candidates: dict,
                                   dossiers: dict, assets: dict) -> dict:
    if assets.get("operational_approval") is not False:
        raise ValueError("Operational asset manifests are not accepted")
    if dossiers.get("operational_approval") is not False:
        raise ValueError("Operational parcel dossiers are not accepted")
    if assets.get("parcel_dossier_manifest_sha256") != dossiers.get("manifest_sha256"):
        raise ValueError("Asset/dossier manifest lineage mismatch")

    property_by_id = {row["candidate_property_id"]: row for row in assets["properties"]}
    building_by_id = {row["candidate_building_id"]: row for row in assets["buildings"]}
    parcel_by_id = {row["candidate_parcel_id"]: row for row in candidates["parcels"]}
    dossier_by_parcel = {
        row["dossier"]["candidate_parcel_id"]: row for row in dossiers["parcels"]
    }
    water = [
        shape(feature["geometry"])
        for feature in source.get("features", [])
        if feature.get("properties", {}).get("entity_type")
        in ("harbour_water", "constructed_water")
    ]
    access_rows = assets["access_points"]
    connectors = []
    errors = {"missing_parent": [], "missing_frontage": [], "outside_parent_property": [],
              "crosses_origin_building": [], "crosses_other_building": [],
              "crosses_water": [], "invalid_geometry": []}
    lengths = []
    status_counts = {
        "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED": 0,
        "DIRECT_GEOMETRY_BLOCKED_UNREVIEWED": 0,
        "NO_FRONTAGE_CANDIDATE": 0,
    }

    buildings_by_property = {}
    for building in assets["buildings"]:
        buildings_by_property.setdefault(building["property_id"], []).append(building)

    for access in access_rows:
        aid = access["candidate_access_point_id"]
        building = building_by_id.get(access.get("building_id"))
        if building is None:
            errors["missing_parent"].append(aid)
            continue
        prop = property_by_id.get(building.get("property_id"))
        parcel_id = building.get("source_candidate_parcel_id")
        parcel = parcel_by_id.get(parcel_id)
        dossier = dossier_by_parcel.get(parcel_id)
        if prop is None or parcel is None or dossier is None:
            errors["missing_parent"].append(aid)
            continue
        frontage_id = access.get("road_link_candidate_id")
        frontage = {
            row["access_candidate_id"]: row
            for row in dossier.get("access_candidates", [])
        }.get(frontage_id)
        if frontage is None:
            if frontage_id is None:
                status_counts["NO_FRONTAGE_CANDIDATE"] += 1
                continue
            errors["missing_frontage"].append(aid)
            continue

        start = Point(access["point_m"])
        end = Point(frontage["candidate_x_m"], frontage["candidate_y_m"])
        line = LineString([(start.x, start.y), (end.x, end.y)])
        if line.is_empty or not line.is_valid or line.length <= 0:
            errors["invalid_geometry"].append(aid)
            continue
        property_geom = _polygon(prop)
        origin_footprint = _polygon(building)
        outside = not property_geom.covers(line)
        origin_cross = line.intersection(origin_footprint).length > 0.01
        other_cross = False
        for other in buildings_by_property.get(prop["candidate_property_id"], []):
            if other["candidate_building_id"] == building["candidate_building_id"]:
                continue
            if line.intersection(_polygon(other)).length > 0.01:
                other_cross = True
                break
        water_cross = any(line.intersection(water_geom).length > 0.01 for water_geom in water)
        if outside:
            errors["outside_parent_property"].append(aid)
        if origin_cross:
            errors["crosses_origin_building"].append(aid)
        if other_cross:
            errors["crosses_other_building"].append(aid)
        if water_cross:
            errors["crosses_water"].append(aid)
        feasible = not (outside or origin_cross or other_cross or water_cross)
        status = ("DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED" if feasible
                  else "DIRECT_GEOMETRY_BLOCKED_UNREVIEWED")
        status_counts[status] += 1
        lengths.append(line.length)
        connectors.append({
            "candidate_access_point_id": aid,
            "candidate_road_connection_id": frontage_id,
            "road_connection_type": frontage.get("candidate_type"),
            "road_connection_contact_type": frontage.get("contact_type"),
            "property_id": prop["candidate_property_id"],
            "building_id": building["candidate_building_id"],
            "straight_connector_length_m": round(line.length, 3),
            "geometry_status": status,
            "property_contains_connector": not outside,
            "crosses_origin_building": origin_cross,
            "crosses_other_building": other_cross,
            "crosses_water": water_cross,
            "review_status": "UNREVIEWED_GEOMETRIC_LINE_ONLY",
        })

    lengths.sort()
    median = lengths[len(lengths) // 2] if lengths else 0.0
    checks = {
        "all_linked_candidates_have_valid_parent_and_frontage": (
            not errors["missing_parent"] and not errors["missing_frontage"]
        ),
        "every_connector_is_inside_its_parent_property": not errors["outside_parent_property"],
        "no_feasible_connector_crosses_its_origin_building_interior": not any(
            row["geometry_status"] == "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED"
            and row["crosses_origin_building"] for row in connectors
        ),
        "no_feasible_connector_crosses_another_building_interior": not any(
            row["geometry_status"] == "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED"
            and row["crosses_other_building"] for row in connectors
        ),
        "no_feasible_connector_crosses_mapped_water": not any(
            row["geometry_status"] == "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED"
            and row["crosses_water"] for row in connectors
        ),
        "all_connectors_remain_unreviewed_candidates": all(
            row["review_status"] == "UNREVIEWED_GEOMETRIC_LINE_ONLY" for row in connectors
        ),
        "no_operational_access_or_address_created": (
            assets.get("generation", {}).get("operational_access_points_created") == 0
            and assets.get("generation", {}).get("canonical_addresses_created") == 0
            and assets.get("operational_approval") is False
        ),
    }
    return {
        "audit": "BP04-03-DIRECT-BUILDING-TO-FRONTAGE-CONNECTOR-FEASIBILITY",
        "counts": {
            "building_boundary_access_candidates": len(access_rows),
            "direct_connector_candidates_tested": len(connectors),
            "direct_geometry_feasible_unreviewed": status_counts["DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED"],
            "direct_geometry_blocked_unreviewed": status_counts["DIRECT_GEOMETRY_BLOCKED_UNREVIEWED"],
            "no_frontage_candidate": status_counts["NO_FRONTAGE_CANDIDATE"],
            "point_contact_road_reserve_candidates": sum(
                1 for row in connectors if row["road_connection_contact_type"] == "POINT_CONTACT_ONLY"
            ),
        },
        "measurements": {
            "connector_length_median": round(median, 3),
            "connector_length_max": round(max(lengths), 3) if lengths else 0.0,
        },
        "exceptions": errors,
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "connector_candidates": connectors,
        "interpretation": (
            "A feasible result means only that the straight geometric line is contained "
            "by the parent property and does not cross mapped building interiors or mapped "
            "water. It does not establish a constructed driveway, door, gate, legal access, "
            "surface condition, gradient, barrier-free route, vehicle suitability or emergency "
            "egress. Blocked candidates are not silently rerouted."
        ),
        "operational_access_points_created": 0,
        "canonical_addresses_created": 0,
        "operational_seed_eligible": False,
        "database_write_performed": False,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    from runtime.parcel_candidate_generator import build_candidates
    from runtime.parcel_dossier_generator import build_parcel_dossiers
    from runtime.physical_asset_inventory_generator import build_asset_inventory

    candidates = build_candidates(source)
    dossiers = build_parcel_dossiers(source, candidates)
    assets = build_asset_inventory(source, candidates, dossiers)
    report = audit_direct_access_connectors(source, candidates, dossiers, assets)
    summary = {key: value for key, value in report.items() if key != "connector_candidates"}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
