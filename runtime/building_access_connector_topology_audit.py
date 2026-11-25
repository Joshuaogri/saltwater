"""Independent topology audit for persisted, non-operational access connector candidates."""
from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon

from runtime.road_corridor_audit import build_road_corridor_audit
from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory


TOLERANCE_M = 0.01


def audit_connector_topology(source: dict, candidates: dict, dossiers: dict,
                             inventory: dict) -> dict:
    if any(item.get("operational_approval") is not False
           for item in (candidates, dossiers, inventory)):
        raise ValueError("Only non-operational geography and asset candidates are accepted")
    if dossiers.get("candidate_manifest_sha256") != candidates.get("manifest_sha256"):
        raise ValueError("Parcel dossier/candidate manifest lineage mismatch")
    if inventory.get("parcel_dossier_manifest_sha256") != dossiers.get("manifest_sha256"):
        raise ValueError("Asset/dossier manifest lineage mismatch")

    corridors = build_road_corridor_audit(source)
    segment_by_id = {row["segment_id"]: row for row in corridors["segments"]}
    properties = {row["source_candidate_parcel_id"]: row for row in inventory["properties"]}
    buildings = {row["candidate_building_id"]: row for row in inventory["buildings"]}
    access_points = {row["candidate_access_point_id"]: row for row in inventory["access_points"]}
    dossiers_by_parcel = {
        row["dossier"]["candidate_parcel_id"]: row for row in dossiers["parcels"]
    }
    connectors = inventory.get("access_connectors", [])

    exceptions = {
        "missing_parent_or_parcel": [],
        "missing_road_candidate": [],
        "road_or_segment_mismatch": [],
        "access_point_endpoint_mismatch": [],
        "road_candidate_endpoint_mismatch": [],
        "connector_length_mismatch": [],
        "connector_outside_property": [],
        "frontage_topology_mismatch": [],
        "proximity_topology_mismatch": [],
        "classification_mismatch": [],
    }
    frontage_count = 0
    proximity_count = 0

    for row in connectors:
        cid = row["candidate_connector_id"]
        access = access_points.get(row.get("access_point_candidate_id"))
        building = buildings.get(access.get("building_id")) if access else None
        prop = properties.get(building.get("source_candidate_parcel_id")) if building else None
        parcel_id = building.get("source_candidate_parcel_id") if building else None
        dossier = dossiers_by_parcel.get(parcel_id) if parcel_id else None
        if not access or not building or not prop or not dossier:
            exceptions["missing_parent_or_parcel"].append(cid)
            continue

        access_candidate = next(
            (candidate for candidate in dossier["access_candidates"]
             if candidate["access_candidate_id"] == row.get("road_access_candidate_id")),
            None,
        )
        if access_candidate is None:
            exceptions["missing_road_candidate"].append(cid)
            continue

        segment_ids = row.get("road_segment_ids", [])
        segments = [segment_by_id.get(segment_id) for segment_id in segment_ids]
        if (not segment_ids or any(segment is None for segment in segments)
                or any(segment["road_id"] != row.get("road_id") for segment in segments)
                or row.get("road_id") != access_candidate.get("road_id")
                or segment_ids != access_candidate.get("road_segment_ids", [])):
            exceptions["road_or_segment_mismatch"].append(cid)

        coords = row.get("geometry_coordinates", [])
        if len(coords) < 2:
            exceptions["road_candidate_endpoint_mismatch"].append(cid)
            continue
        line = LineString(coords)
        start, end = Point(coords[0]), Point(coords[-1])
        access_point = Point(access["point_m"])
        candidate_point = Point(
            access_candidate["candidate_x_m"], access_candidate["candidate_y_m"]
        )
        if start.distance(access_point) > TOLERANCE_M:
            exceptions["access_point_endpoint_mismatch"].append(cid)
        if end.distance(candidate_point) > TOLERANCE_M:
            exceptions["road_candidate_endpoint_mismatch"].append(cid)
        if abs(line.length - float(row["length_m"])) > 0.005:
            exceptions["connector_length_mismatch"].append(cid)

        property_geometry = Polygon(prop["geometry"][0], prop["geometry"][1:])
        if not property_geometry.covers(line):
            exceptions["connector_outside_property"].append(cid)

        if access_candidate["candidate_type"] == "unclassified_access_location":
            frontage_count += 1
            frontage = next(
                (item for item in dossier["frontages"]
                 if item["frontage_candidate_id"] == row.get("frontage_candidate_id")),
                None,
            )
            if (row.get("connector_type") != "BUILDING_TO_FRONTAGE_CANDIDATE"
                    or row.get("contact_type") != "FRONTAGE_CANDIDATE"
                    or row.get("road_connection_candidate_id") is not None
                    or frontage is None
                    or row.get("road_id") != frontage.get("road_id")
                    or any(sid not in frontage["road_segment_ids"] for sid in segment_ids)):
                exceptions["classification_mismatch"].append(cid)
                exceptions["frontage_topology_mismatch"].append(cid)
                continue
            if candidate_point.distance(property_geometry.boundary) > TOLERANCE_M:
                exceptions["frontage_topology_mismatch"].append(cid)
            reserve_edges = [
                Polygon(segment["reserve_polygon"][0]).boundary for segment in segments
                if segment is not None
            ]
            if not reserve_edges or min(candidate_point.distance(edge) for edge in reserve_edges) > TOLERANCE_M:
                exceptions["frontage_topology_mismatch"].append(cid)

        elif access_candidate["candidate_type"] == "road_reserve_proximity_connection":
            proximity_count += 1
            parcel_contact = Point(
                access_candidate["parcel_boundary_x_m"],
                access_candidate["parcel_boundary_y_m"],
            )
            road_contact = candidate_point
            if (row.get("connector_type") != "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE"
                    or row.get("frontage_candidate_id") is not None
                    or row.get("road_connection_candidate_id")
                       != access_candidate.get("road_connection_candidate_id")
                    or row.get("contact_type") != access_candidate.get("contact_type")
                    or len(segment_ids) != 1):
                exceptions["classification_mismatch"].append(cid)
                exceptions["proximity_topology_mismatch"].append(cid)
                continue
            segment = segments[0] if segments else None
            if segment is None:
                exceptions["proximity_topology_mismatch"].append(cid)
                continue
            reserve_edge = Polygon(segment["reserve_polygon"][0]).boundary
            measured_gap = parcel_contact.distance(road_contact)
            if (parcel_contact.distance(property_geometry.boundary) > TOLERANCE_M
                    or road_contact.distance(reserve_edge) > TOLERANCE_M
                    or abs(measured_gap - access_candidate["distance_to_road_reserve_m"]) > TOLERANCE_M):
                exceptions["proximity_topology_mismatch"].append(cid)
        else:
            exceptions["classification_mismatch"].append(cid)

    checks = {
        "all_connectors_have_valid_building_property_and_parcel_lineage": not exceptions["missing_parent_or_parcel"],
        "all_road_and_segment_references_resolve_to_the_same_road": not exceptions["missing_road_candidate"] and not exceptions["road_or_segment_mismatch"],
        "connector_start_matches_its_building_boundary_candidate": not exceptions["access_point_endpoint_mismatch"],
        "connector_end_matches_its_road_access_candidate": not exceptions["road_candidate_endpoint_mismatch"],
        "connector_lengths_match_their_line_geometry": not exceptions["connector_length_mismatch"],
        "all_connector_lines_remain_inside_their_parent_property": not exceptions["connector_outside_property"],
        "frontage_connectors_match_parcel_and_road_reserve_topology": not exceptions["frontage_topology_mismatch"],
        "point_contact_connectors_preserve_non_frontage_topology": not exceptions["proximity_topology_mismatch"],
        "frontage_and_proximity_types_are_never_interchanged": not exceptions["classification_mismatch"],
    }
    return {
        "audit": "BP04-03-INDEPENDENT-ACCESS-CONNECTOR-ROAD-TOPOLOGY",
        "counts": {
            "connector_candidates": len(connectors),
            "frontage_connector_candidates": frontage_count,
            "road_reserve_proximity_connector_candidates": proximity_count,
            "unlinked_connector_candidates": sum(
                1 for row in connectors if not row.get("road_access_candidate_id")
            ),
        },
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "exceptions": exceptions,
        "interpretation": (
            "This audit checks generated connector endpoint, parent-property, road-segment, "
            "frontage and road-reserve geometry lineage. It does not establish constructed "
            "paths, legal/public access, doors/gates, route surface, gradient, accessibility, "
            "vehicle suitability or emergency egress."
        ),
        "operational_access_points_created": 0,
        "canonical_addresses_created": 0,
        "operational_seed_eligible": False,
        "database_write_performed": False,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    candidates = build_candidates(source)
    dossiers = build_parcel_dossiers(source, candidates)
    inventory = build_asset_inventory(source, candidates, dossiers)
    report = audit_connector_topology(source, candidates, dossiers, inventory)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
