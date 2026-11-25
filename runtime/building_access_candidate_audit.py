"""Read-only reconciliation of generated building-boundary access candidates to parcel frontage candidates."""
from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import Point, Polygon


def _polygon(record):
    return Polygon(record["geometry"][0], record["geometry"][1:])


def audit_building_access_candidates(candidates: dict, dossiers: dict, assets: dict) -> dict:
    if assets.get("operational_approval") is not False:
        raise ValueError("Operational asset manifests are not accepted")
    if dossiers.get("operational_approval") is not False:
        raise ValueError("Operational parcel dossiers are not accepted")
    if assets.get("parcel_dossier_manifest_sha256") != dossiers.get("manifest_sha256"):
        raise ValueError("Asset/dossier manifest lineage mismatch")

    parcel_by_id = {row["candidate_parcel_id"]: row for row in candidates["parcels"]}
    dossier_by_parcel = {row["dossier"]["candidate_parcel_id"]: row for row in dossiers["parcels"]}
    property_by_id = {row["candidate_property_id"]: row for row in assets["properties"]}
    building_by_id = {row["candidate_building_id"]: row for row in assets["buildings"]}
    access_rows = assets["access_points"]

    property_source_ids = [row["source_candidate_parcel_id"] for row in assets["properties"]]
    access_ids = [row["candidate_access_point_id"] for row in access_rows]
    identity_ok = (
        len(property_by_id) == len(assets["properties"]) == 420
        and len(building_by_id) == len(assets["buildings"]) == 384
        and len(access_ids) == len(set(access_ids)) == 768
        and len(set(property_source_ids)) == 420
        and set(property_source_ids) == set(parcel_by_id)
    )

    hierarchy_errors, footprint_errors, point_errors = [], [], []
    link_errors, nearest_mismatches, status_errors = [], [], []
    distances_by_position = {"A01": [], "A02": [], "OTHER": []}
    access_with_no_frontage = 0

    for building in assets["buildings"]:
        building_id = building["candidate_building_id"]
        prop = property_by_id.get(building["property_id"])
        parcel_id = building.get("source_candidate_parcel_id")
        parcel = parcel_by_id.get(parcel_id)
        if prop is None or parcel is None or prop.get("source_candidate_parcel_id") != parcel_id:
            hierarchy_errors.append(building_id)
            continue
        property_geom = _polygon(prop)
        parcel_geom = _polygon(parcel)
        if property_geom.symmetric_difference(parcel_geom).area > 0.001:
            hierarchy_errors.append(building_id)
        footprint = _polygon(building)
        if not footprint.is_valid or footprint.is_empty or not property_geom.covers(footprint):
            footprint_errors.append(building_id)

    for access in access_rows:
        access_id = access["candidate_access_point_id"]
        building = building_by_id.get(access["building_id"])
        if building is None:
            hierarchy_errors.append(access_id)
            continue
        prop = property_by_id.get(building["property_id"])
        parcel_id = building["source_candidate_parcel_id"]
        parcel = parcel_by_id.get(parcel_id)
        dossier_row = dossier_by_parcel.get(parcel_id)
        if prop is None or parcel is None or dossier_row is None:
            hierarchy_errors.append(access_id)
            continue

        footprint = _polygon(building)
        property_geom = _polygon(prop)
        point = Point(access["point_m"])
        if footprint.boundary.distance(point) > 0.00001:
            point_errors.append(access_id)
        if not property_geom.covers(point):
            point_errors.append(access_id)

        connection_candidates = dossier_row.get("access_candidates", [])
        connection_points = {
            row["access_candidate_id"]: Point(row["candidate_x_m"], row["candidate_y_m"])
            for row in connection_candidates
        }
        if not connection_points:
            access_with_no_frontage += 1
            if access.get("road_link_candidate_id") is not None:
                link_errors.append(access_id)
            continue

        distances = sorted(
            ((point.distance(connection_point), candidate_id)
             for candidate_id, connection_point in connection_points.items()),
            key=lambda item: (round(item[0], 9), item[1]),
        )
        nearest_distance, nearest_id = distances[0]
        linked_id = access.get("road_link_candidate_id")
        if linked_id not in connection_points:
            link_errors.append(access_id)
        else:
            linked_distance = point.distance(connection_points[linked_id])
            if (abs(linked_distance - nearest_distance) > 0.00001 or linked_id != nearest_id
                    or access.get("road_link_candidate_distance_m") is None
                    or abs(access["road_link_candidate_distance_m"] - linked_distance) > 0.001):
                nearest_mismatches.append({
                    "access_candidate_id": access_id,
                    "assigned_frontage_candidate_id": linked_id,
                    "nearest_frontage_candidate_id": nearest_id,
                    "assigned_distance_m": round(linked_distance, 3),
                    "recorded_distance_m": access.get("road_link_candidate_distance_m"),
                    "nearest_distance_m": round(nearest_distance, 3),
                })
            position = access_id.rsplit("-", 1)[-1]
            distances_by_position.get(position, distances_by_position["OTHER"]).append(nearest_distance)

        if access.get("point_status") != "UNREVIEWED_BUILDING_BOUNDARY_CANDIDATE":
            status_errors.append(access_id)
        if access.get("access_type") != "unknown" or access.get("access_modes") != []:
            status_errors.append(access_id)
        if access.get("availability_state") != "not_assessed" or access.get("accessibility_state") != "not_assessed":
            status_errors.append(access_id)
        if access.get("emergency_egress_state") != "not_assessed" or access.get("loading_capability_state") != "not_assessed":
            status_errors.append(access_id)
        if linked_id is None:
            if (access.get("road_link_basis") != "NO_FRONTAGE_CANDIDATE"
                    or access.get("road_link_status") != "UNRESOLVED_NO_FRONTAGE"
                    or access.get("road_link_candidate_distance_m") is not None):
                status_errors.append(access_id)
        else:
            linked_candidate = next(
                row for row in connection_candidates
                if row["access_candidate_id"] == linked_id
            )
            expected_basis = (
                "NEAREST_ROAD_RESERVE_PROXIMITY_CANDIDATE"
                if linked_candidate.get("candidate_type") == "road_reserve_proximity_connection"
                else "NEAREST_STRAIGHT_LINE_FRONTAGE_CANDIDATE"
            )
            if (access.get("road_link_basis") != expected_basis
                    or access.get("road_link_status") != "UNREVIEWED_PROXIMITY_ONLY_NOT_A_CONFIRMED_ROUTE"):
                status_errors.append(access_id)

    distances = [value for values in distances_by_position.values() for value in values]
    distances.sort()
    median = distances[len(distances) // 2] if distances else 0.0
    max_distance = max(distances) if distances else 0.0
    generation = assets.get("generation", {})
    checks = {
        "property_building_and_access_identity_counts_reconcile": identity_ok,
        "building_footprints_remain_inside_their_parcel_property": not footprint_errors,
        "building_access_points_are_on_building_boundaries_and_inside_property": not point_errors,
        "asset_to_parcel_and_parent_hierarchy_is_consistent": not hierarchy_errors,
        "road_link_candidates_resolve_to_the_same_parcel_frontage": not link_errors,
        "each_building_access_candidate_links_to_its_nearest_geometric_frontage": not nearest_mismatches,
        "access_facts_remain_unknown_or_not_assessed": not status_errors,
        "no_operational_address_or_access_point_is_created": (
            generation.get("canonical_addresses_created") == 0
            and generation.get("operational_access_points_created") == 0
            and assets.get("operational_approval") is False
        ),
    }
    return {
        "audit": "BP04-03-BUILDING-ACCESS-CANDIDATE-RECONCILIATION",
        "counts": {
            "property_site_candidates": len(assets["properties"]),
            "building_candidates": len(assets["buildings"]),
            "building_boundary_access_candidates": len(access_rows),
            "access_candidates_without_parcel_frontage": access_with_no_frontage,
            "point_contact_road_reserve_candidates": sum(
                1 for row in assets["access_points"]
                if row.get("road_link_contact_type") == "POINT_CONTACT_ONLY"
            ),
            "assigned_frontage_link_mismatches": len(nearest_mismatches),
        },
        "measurements": {
            "nearest_frontage_straight_line_gap_median": round(median, 3),
            "nearest_frontage_straight_line_gap_max": round(max_distance, 3),
            "a01_gap_count": len(distances_by_position["A01"]),
            "a02_gap_count": len(distances_by_position["A02"]),
        },
        "exceptions": {
            "hierarchy_errors": sorted(set(hierarchy_errors)),
            "building_footprint_errors": sorted(set(footprint_errors)),
            "access_point_geometry_errors": sorted(set(point_errors)),
            "unresolved_frontage_links": sorted(set(link_errors)),
            "assigned_link_not_nearest": nearest_mismatches,
            "unsupported_access_facts": sorted(set(status_errors)),
        },
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "operational_access_points_created": 0,
        "canonical_addresses_created": 0,
        "operational_seed_eligible": False,
        "database_write_performed": False,
        "interpretation": "Straight-line distances are geometric proximity measurements only. They do not establish a driveway, entrance, traversable path, legal frontage or usable emergency access.",
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
    report = audit_building_access_candidates(candidates, dossiers, assets)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
