"""Independent geometry QA for BP04-03 parcel dossiers; candidate-only and read-only."""
from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import Point, Polygon, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.road_corridor_audit import build_road_corridor_audit
from runtime.road_reserve_topology import build_road_reserve_topology

TOL = 0.02


def _parcel_polygon(record):
    rings = record["geometry"]
    return Polygon(rings[0], rings[1:])


def _candidate_id(row):
    return row["dossier"]["candidate_parcel_id"]


def audit_parcel_dossiers(source: dict, candidates: dict | None = None,
                          dossiers: dict | None = None) -> dict:
    candidates = candidates or build_candidates(source)
    dossiers = dossiers or build_parcel_dossiers(source, candidates)
    if dossiers.get("operational_approval") is not False:
        raise ValueError("Operational parcel dossier manifests are not accepted")
    if dossiers.get("source_dataset") != source.get("dataset_id"):
        raise ValueError("Dossier source dataset mismatch")
    if dossiers.get("candidate_manifest_sha256") != candidates.get("manifest_sha256"):
        raise ValueError("Dossier/candidate manifest lineage mismatch")

    corridors = build_road_corridor_audit(source)
    topology = build_road_reserve_topology(source, corridors)
    road_reserve = shape(topology["city_road_reserve_geometry"])
    road_edge = road_reserve.boundary
    segment_by_id = {row["segment_id"]: row for row in corridors["segments"]}
    segment_polygons = {sid: Polygon(row["reserve_polygon"][0])
                        for sid, row in segment_by_id.items()}
    roads = {row["id"]: row for row in source["roads"]}
    water = {row["id"]: shape(row["geometry"]) for row in source["features"]
             if row.get("properties", {}).get("entity_type") in
             ("harbour_water", "constructed_water")}
    water_union = unary_union(list(water.values())) if water else Polygon()
    neighbourhoods = {row["id"]: shape(row["geometry"]) for row in source["neighbourhoods"]}
    city = next(shape(row["geometry"]) for row in source["features"]
                if row.get("properties", {}).get("entity_type") == "city_state_boundary")

    candidate_rows = {row["candidate_parcel_id"]: row for row in candidates["parcels"]}
    dossier_rows = {_candidate_id(row): row for row in dossiers["parcels"]}
    identity_ok = (len(candidate_rows) == len(candidates["parcels"]) == 420
                   and len(dossier_rows) == len(dossiers["parcels"]) == 420
                   and set(candidate_rows) == set(dossier_rows))
    geometry_errors, outside_parent, reserve_or_water_intrusions = [], [], []
    geometries = []
    for parcel_id, candidate in candidate_rows.items():
        geom = _parcel_polygon(candidate)
        geometries.append(geom)
        if geom.is_empty or not geom.is_valid or geom.area <= 0:
            geometry_errors.append(parcel_id)
            continue
        parent = neighbourhoods.get(candidate["source_neighbourhood_id"])
        if parent is None or not parent.covers(geom):
            outside_parent.append(parcel_id)
        if not city.covers(geom):
            outside_parent.append(parcel_id)
        intrusion = geom.intersection(unary_union([road_reserve, water_union])).area
        if intrusion > TOL:
            reserve_or_water_intrusions.append(parcel_id)

    overlap_area = sum(g.area for g in geometries) - unary_union(geometries).area
    overlap_ok = abs(overlap_area) <= TOL

    frontage_errors, access_errors = [], []
    expected_frontages = 0
    for parcel_id, row in dossier_rows.items():
        candidate = candidate_rows.get(parcel_id)
        if candidate is None:
            frontage_errors.append(parcel_id)
            continue
        parcel = _parcel_polygon(candidate)
        parcel_boundary = parcel.boundary
        expected_by_road = {}
        for segment_id, segment in segment_by_id.items():
            contact = parcel_boundary.intersection(segment_polygons[segment_id].boundary).intersection(road_edge)
            if contact.length > 0.01:
                expected_by_road.setdefault(segment["road_id"], []).append((segment_id, contact))
        actual_by_road = {}
        for frontage in row.get("frontages", []):
            road_id = frontage.get("road_id")
            actual_by_road.setdefault(road_id, []).append(frontage)
        if set(actual_by_road) != set(expected_by_road):
            frontage_errors.append(parcel_id)
        frontage_ids = set()
        for frontage in row.get("frontages", []):
            frontage_id = frontage.get("frontage_candidate_id")
            frontage_ids.add(frontage_id)
            road_id = frontage.get("road_id")
            road = roads.get(road_id)
            segment_ids = frontage.get("road_segment_ids", [])
            expected_entries = expected_by_road.get(road_id, [])
            expected_segment_ids = {entry[0] for entry in expected_entries}
            if (not road or frontage.get("road_name") != road.get("name")
                    or set(segment_ids) != expected_segment_ids or not segment_ids):
                frontage_errors.append(frontage_id or parcel_id)
                continue
            contact_union = unary_union([entry[1] for entry in expected_entries])
            measured = contact_union.length
            if measured <= 0.01 or abs(measured - frontage.get("contact_length_m", -1)) > TOL:
                frontage_errors.append(frontage_id)
            point = Point(frontage["candidate_point_x_m"], frontage["candidate_point_y_m"])
            if contact_union.distance(point) > TOL:
                frontage_errors.append(frontage_id)
            if frontage.get("contact_component_count", 0) < 1:
                frontage_errors.append(frontage_id)
        expected_frontages += len(expected_by_road)
        for access in row.get("access_candidates", []):
            frontage = next((f for f in row.get("frontages", [])
                             if f.get("frontage_candidate_id") == access.get("frontage_candidate_id")), None)
            if frontage is None:
                access_errors.append(access.get("access_candidate_id", parcel_id))
                continue
            point = Point(access["candidate_x_m"], access["candidate_y_m"])
            frontage_point = Point(frontage["candidate_point_x_m"], frontage["candidate_point_y_m"])
            if point.distance(frontage_point) > TOL or parcel_boundary.distance(point) > TOL:
                access_errors.append(access.get("access_candidate_id"))
            if access.get("review_status") != "UNREVIEWED_GEOMETRIC_CANDIDATE":
                access_errors.append(access.get("access_candidate_id"))
            if access.get("candidate_type") != "unclassified_access_location":
                access_errors.append(access.get("access_candidate_id"))
        if len(row.get("access_candidates", [])) != len(row.get("frontages", [])):
            access_errors.append(parcel_id)

    water_errors = []
    for parcel_id, row in dossier_rows.items():
        parcel = _parcel_polygon(candidate_rows[parcel_id])
        expected = {}
        for water_id, water_geom in water.items():
            contact = parcel.boundary.intersection(water_geom.boundary).length
            if contact > 0.01:
                expected[water_id] = round(contact, 3)
        actual = {item["water_feature_id"]: item["contact_length_m"]
                  for item in row.get("water_adjacencies", [])}
        if set(actual) != set(expected) or any(abs(actual[k] - expected[k]) > TOL for k in expected):
            water_errors.append(parcel_id)

    expected_adjacency = {}
    tree = STRtree(geometries)
    ids = list(candidate_rows)
    for i, geom in enumerate(geometries):
        for j in sorted(int(v) for v in tree.query(geom, predicate="touches") if int(v) > i):
            contact = geom.boundary.intersection(geometries[j].boundary)
            if contact.is_empty:
                continue
            expected_adjacency[(ids[i], ids[j])] = (
                "SHARED_BOUNDARY_CANDIDATE" if contact.length > 0.01 else "CORNER_TOUCH_CANDIDATE",
                round(contact.length, 3),
            )
    actual_adjacency = {}
    duplicate_adjacency = False
    for row in dossiers.get("adjacency", []):
        pair = (row.get("left_candidate_parcel_id"), row.get("right_candidate_parcel_id"))
        if pair in actual_adjacency or pair[0] >= pair[1]:
            duplicate_adjacency = True
            continue
        actual_adjacency[pair] = (row.get("relationship_code"), row.get("shared_boundary_length_m"))
    adjacency_ok = (not duplicate_adjacency and set(actual_adjacency) == set(expected_adjacency)
                    and all(actual_adjacency[k][0] == expected_adjacency[k][0]
                            and abs(actual_adjacency[k][1] - expected_adjacency[k][1]) <= TOL
                            for k in expected_adjacency))

    summary = dossiers.get("summary", {})
    actual_frontage_count = sum(len(r.get("frontages", [])) for r in dossier_rows.values())
    actual_access_count = sum(len(r.get("access_candidates", [])) for r in dossier_rows.values())
    checks = {
        "candidate_and_dossier_identity_sets_match": identity_ok,
        "all_candidate_parcels_are_valid_polygons": not geometry_errors,
        "parcels_are_contained_by_neighbourhood_and_city": not outside_parent,
        "parcels_exclude_road_reserve_and_mapped_water": not reserve_or_water_intrusions,
        "candidate_parcel_interiors_do_not_overlap": overlap_ok,
        "frontage_candidates_match_complete_road_edge_geometry": (
            not frontage_errors and actual_frontage_count == expected_frontages
        ),
        "access_candidates_match_frontage_points_and_remain_unreviewed": (
            not access_errors and actual_access_count == actual_frontage_count
        ),
        "water_adjacencies_match_source_water_geometry": not water_errors,
        "parcel_adjacency_register_is_complete_and_measured": adjacency_ok,
        "candidate_manifest_summary_and_non_operational_state_are_consistent": (
            summary.get("parcel_dossier_count") == 420
            and summary.get("frontage_candidate_count") == actual_frontage_count
            and summary.get("access_location_candidate_count") == actual_access_count
            and summary.get("adjacency_relationship_count") == len(actual_adjacency)
            and summary.get("canonical_addresses_created") == 0
            and summary.get("operational_access_points_created") == 0
            and dossiers.get("operational_approval") is False
        ),
    }
    return {
        "audit": "BP04-03-PARCEL-DOSSIER-GEOMETRY-QA",
        "source_dataset": source.get("dataset_id"),
        "counts": {
            "candidate_parcels": len(candidate_rows),
            "parcel_dossiers": len(dossier_rows),
            "frontage_candidates": actual_frontage_count,
            "access_location_candidates": actual_access_count,
            "water_adjacency_records": sum(len(r.get("water_adjacencies", [])) for r in dossier_rows.values()),
            "parcel_adjacency_records": len(dossiers.get("adjacency", [])),
        },
        "measurements": {
            "candidate_parcel_total_area_m2": round(sum(g.area for g in geometries), 3),
            "parcel_interior_overlap_area_m2": round(overlap_area, 6),
            "expected_adjacency_relationships": len(expected_adjacency),
        },
        "exceptions": {
            "invalid_parcel_ids": sorted(geometry_errors),
            "outside_parent_or_city_ids": sorted(set(outside_parent)),
            "road_reserve_or_water_intrusion_ids": sorted(reserve_or_water_intrusions),
            "frontage_geometry_errors": sorted(set(frontage_errors)),
            "access_geometry_errors": sorted(set(access_errors)),
            "water_adjacency_errors": sorted(water_errors),
            "adjacency_missing_or_incorrect": not adjacency_ok,
        },
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "operational_seed_eligible": False,
        "canonical_addresses_created": 0,
        "operational_access_points_created": 0,
        "database_write_performed": False,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    report = audit_parcel_dossiers(source)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
