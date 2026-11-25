"""Geometry-only route-corridor candidates for BP04-03 access connectors.

No width, surface, gradient, barrier, construction, legal-access or route
suitability is inferred. A LineString is a centreline candidate, not a route.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from shapely.geometry import LineString, Polygon, shape

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.road_corridor_audit import build_road_corridor_audit

TOLERANCE_M = 0.01
GENERATOR = "BP04-03-ROUTE-CORRIDOR-CANDIDATE-AUDIT-V1"


def _polygon(rings):
    return Polygon(rings[0], rings[1:])


def build_route_corridor_candidates(source: dict, candidates: dict | None = None,
                                    dossiers: dict | None = None,
                                    inventory: dict | None = None) -> dict:
    candidates = candidates or build_candidates(source)
    dossiers = dossiers or build_parcel_dossiers(source, candidates)
    inventory = inventory or build_asset_inventory(source, candidates, dossiers)
    if any(item.get("operational_approval") is not False
           for item in (candidates, dossiers, inventory)):
        raise ValueError("Only non-operational source manifests are accepted")
    if candidates.get("source_dataset") != source.get("dataset_id"):
        raise ValueError("Candidate source dataset mismatch")
    if dossiers.get("candidate_manifest_sha256") != candidates.get("manifest_sha256"):
        raise ValueError("Parcel dossier/candidate manifest lineage mismatch")
    if inventory.get("candidate_manifest_sha256") != candidates.get("manifest_sha256"):
        raise ValueError("Asset/candidate manifest lineage mismatch")
    if inventory.get("parcel_dossier_manifest_sha256") != dossiers.get("manifest_sha256"):
        raise ValueError("Asset/dossier manifest lineage mismatch")

    corridor_register = build_road_corridor_audit(source)
    reserve_by_segment = {
        row["segment_id"]: shape({
            "type": "Polygon", "coordinates": row["reserve_polygon"]
        })
        for row in corridor_register["segments"]
    }
    properties = {r["source_candidate_parcel_id"]: r for r in inventory["properties"]}
    buildings = {r["candidate_building_id"]: r for r in inventory["buildings"]}
    access_points = {r["candidate_access_point_id"]: r for r in inventory["access_points"]}
    dossier_by_parcel = {
        r["dossier"]["candidate_parcel_id"]: r for r in dossiers["parcels"]
    }
    building_geometries = {
        key: _polygon(row["geometry"]) for key, row in buildings.items()
    }
    water = [
        (f["id"], shape(f["geometry"]))
        for f in source.get("features", [])
        if f.get("properties", {}).get("entity_type") in ("harbour_water", "constructed_water")
    ]
    terrain = [
        (f["id"], shape(f["geometry"]), f.get("properties", {}).get("terrain", "unknown"))
        for f in source.get("features", [])
        if f.get("properties", {}).get("entity_type") == "terrain_feature"
    ]

    rows = []
    exceptions = {
        "missing_parent_lineage": [],
        "missing_source_connector": [],
        "invalid_geometry": [],
        "connector_not_contained_by_parent_property": [],
        "origin_building_interior_crossing": [],
        "other_building_intersections": [],
        "mapped_water_intersections": [],
        "road_reserve_overlap": [],
    }
    terrain_intersections = 0
    clearance_values = []

    for connector in sorted(inventory.get("access_connectors", []),
                            key=lambda r: r["candidate_connector_id"]):
        cid = connector["candidate_connector_id"]
        access = access_points.get(connector.get("access_point_candidate_id"))
        building = buildings.get(access.get("building_id")) if access else None
        parcel_id = building.get("source_candidate_parcel_id") if building else None
        prop = properties.get(parcel_id) if parcel_id else None
        dossier_row = dossier_by_parcel.get(parcel_id) if parcel_id else None
        if not access or not building or not prop or not dossier_row:
            exceptions["missing_parent_lineage"].append(cid)
            continue

        road_candidate = next(
            (r for r in dossier_row["access_candidates"]
             if r["access_candidate_id"] == connector.get("road_access_candidate_id")),
            None,
        )
        if road_candidate is None:
            exceptions["missing_source_connector"].append(cid)
            continue

        try:
            coords = connector["geometry_coordinates"]
            if connector.get("geometry_type") != "LineString" or len(coords) != 2:
                raise ValueError("expected two-point LineString")
            line = LineString(coords)
            if line.is_empty or not line.is_valid or line.length <= 0:
                raise ValueError("empty, invalid or zero-length centreline")
        except (KeyError, TypeError, ValueError):
            exceptions["invalid_geometry"].append(cid)
            continue

        property_geometry = _polygon(prop["geometry"])
        own_building = building_geometries[building["candidate_building_id"]]
        if not property_geometry.covers(line):
            exceptions["connector_not_contained_by_parent_property"].append(cid)

        origin_crossing = line.intersection(own_building).length
        if origin_crossing > TOLERANCE_M:
            exceptions["origin_building_interior_crossing"].append(cid)

        other_building_hits = []
        other_clearances = []
        for other_id, other_geometry in building_geometries.items():
            if other_id == building["candidate_building_id"]:
                continue
            if line.intersects(other_geometry):
                other_building_hits.append(other_id)
            other_clearances.append(line.distance(other_geometry))
        if other_building_hits:
            exceptions["other_building_intersections"].append({
                "connector_id": cid, "building_ids": sorted(other_building_hits)
            })
        min_building_clearance = min(other_clearances) if other_clearances else None
        if min_building_clearance is not None:
            clearance_values.append(min_building_clearance)

        water_hits = []
        water_clearances = []
        for feature_id, geometry in water:
            if line.intersects(geometry):
                water_hits.append(feature_id)
            water_clearances.append(line.distance(geometry))
        if water_hits:
            exceptions["mapped_water_intersections"].append({
                "connector_id": cid, "feature_ids": sorted(water_hits)
            })
        min_water_clearance = min(water_clearances) if water_clearances else None

        terrain_hits = []
        for feature_id, geometry, terrain_code in terrain:
            if line.intersects(geometry):
                terrain_hits.append({
                    "feature_id": feature_id,
                    "terrain_code": terrain_code,
                    "intersection_length_m": round(line.intersection(geometry).length, 3),
                })
        if terrain_hits:
            terrain_intersections += 1

        reserve_intersections = []
        for segment_id in connector.get("road_segment_ids", []):
            reserve_poly = reserve_by_segment.get(segment_id)
            if reserve_poly is not None:
                overlap = line.intersection(reserve_poly).length
                if overlap > TOLERANCE_M:
                    reserve_intersections.append({
                        "segment_id": segment_id,
                        "overlap_length_m": round(overlap, 3),
                    })
        if reserve_intersections:
            exceptions["road_reserve_overlap"].append({
                "connector_id": cid, "segments": reserve_intersections
            })

        obstacle_state = (
            "MAPPED_BUILDING_OR_WATER_INTERSECTION"
            if other_building_hits or water_hits or origin_crossing > TOLERANCE_M
            else "NO_INTERSECTION_WITH_MAPPED_BUILDINGS_OR_WATER"
        )
        rows.append({
            "candidate_route_corridor_id": f"SWRC-{cid}",
            "source_connector_candidate_id": cid,
            "candidate_access_point_id": connector["access_point_candidate_id"],
            "candidate_building_id": building["candidate_building_id"],
            "candidate_property_id": prop["candidate_property_id"],
            "source_candidate_parcel_id": parcel_id,
            "road_access_candidate_id": connector["road_access_candidate_id"],
            "frontage_candidate_id": connector.get("frontage_candidate_id"),
            "road_connection_candidate_id": connector.get("road_connection_candidate_id"),
            "road_id": connector["road_id"],
            "road_segment_ids": connector["road_segment_ids"],
            "connector_type": connector["connector_type"],
            "contact_type": connector["contact_type"],
            "centreline_geometry": {"type": "LineString", "coordinates": coords},
            "centreline_length_m": round(line.length, 3),
            "centreline_status": "UNREVIEWED_GEOMETRIC_CANDIDATE",
            "mapped_obstacle_intersection_state": obstacle_state,
            "origin_building_interior_intersection_length_m": round(origin_crossing, 3),
            "other_building_intersection_ids": sorted(other_building_hits),
            "minimum_other_building_clearance_m": round(min_building_clearance, 3) if min_building_clearance is not None else None,
            "mapped_water_intersection_ids": sorted(water_hits),
            "minimum_mapped_water_clearance_m": round(min_water_clearance, 3) if min_water_clearance is not None else None,
            "terrain_feature_intersections": terrain_hits,
            "terrain_intersection_state": "INTERSECTS_MAPPED_TERRAIN_FEATURE" if terrain_hits else "NO_MAPPED_TERRAIN_FEATURE_INTERSECTION",
            "available_width_m": None,
            "corridor_width_m": None,
            "width_assessment_state": "NOT_ASSESSED_NO_WIDTH_OR_CLEARANCE_SOURCE",
            "surface_state": "unknown",
            "gradient_state": "not_assessed_no_elevation_source",
            "barrier_state": "not_assessed",
            "pedestrian_suitability": "not_assessed",
            "vehicle_suitability": "not_assessed",
            "accessibility_state": "not_assessed",
            "legal_access_state": "not_assessed",
            "public_access_state": "not_assessed",
            "emergency_egress_state": "not_assessed",
            "route_suitability": "unknown",
            "source_ref": connector["source_ref"],
            "source_manifest_sha256": inventory["manifest_sha256"],
            "actor_ref": GENERATOR,
            "confidence_code": "estimated",
            "effective_from_tick": 0,
            "recorded_status": "generated_route_corridor_centreline_candidate",
        })

    total = len(inventory.get("access_connectors", []))
    checks = {
        "all_connector_candidates_have_parent_and_source_lineage": not exceptions["missing_parent_lineage"] and not exceptions["missing_source_connector"],
        "all_centrelines_are_valid_two_endpoint_lines": len(rows) + len(exceptions["invalid_geometry"]) == total,
        "all_centrelines_remain_within_parent_property": not exceptions["connector_not_contained_by_parent_property"],
        "no_centreline_crosses_its_origin_building_interior": not exceptions["origin_building_interior_crossing"],
        "no_centreline_intersects_another_generated_building": not exceptions["other_building_intersections"],
        "no_centreline_intersects_mapped_water": not exceptions["mapped_water_intersections"],
        "no_centreline_runs_along_or_inside_its_linked_road_reserve": not exceptions["road_reserve_overlap"],
    }
    body = {
        "schema": "saltwater-bp04-03-route-corridor-candidates/1.0",
        "candidate_register_id": "BP04-03-ROUTE-CORRIDOR-CANDIDATES-001",
        "source_dataset": source["dataset_id"],
        "source_connector_manifest_sha256": inventory["manifest_sha256"],
        "candidate_manifest_sha256": candidates["manifest_sha256"],
        "parcel_dossier_manifest_sha256": dossiers["manifest_sha256"],
        "coordinate_reference": inventory["coordinate_reference"],
        "generator": GENERATOR,
        "operational_approval": False,
        "summary": {
            "connector_candidate_count": total,
            "route_corridor_centreline_candidate_count": len(rows),
            "frontage_centreline_candidate_count": sum(r["connector_type"] == "BUILDING_TO_FRONTAGE_CANDIDATE" for r in rows),
            "point_contact_or_proximity_centreline_candidate_count": sum(r["connector_type"] == "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE" for r in rows),
            "mapped_building_intersection_count": len(exceptions["other_building_intersections"]),
            "mapped_water_intersection_count": len(exceptions["mapped_water_intersections"]),
            "origin_building_interior_crossing_count": len(exceptions["origin_building_interior_crossing"]),
            "road_reserve_overlap_count": len(exceptions["road_reserve_overlap"]),
            "terrain_feature_intersection_count": terrain_intersections,
            "width_assessed_count": 0,
            "gradient_assessed_count": 0,
            "surface_assessed_count": 0,
            "route_suitability_confirmed_count": 0,
            "available_width_min_m": None,
            "available_width_max_m": None,
            "minimum_other_building_clearance_m": round(min(clearance_values), 3) if clearance_values else None,
            "maximum_other_building_clearance_m": round(max(clearance_values), 3) if clearance_values else None,
            "unresolved_connector_count": total - len(rows),
            "operational_access_points_created": 0,
            "canonical_addresses_created": 0,
            "operational_seed_eligible": False,
            "database_write_performed": False,
        },
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "exceptions": exceptions,
        "route_corridors": rows,
        "limitations": [
            "Each corridor is a two-dimensional centreline candidate copied from a connector geometry; no traversable route is asserted.",
            "No corridor polygon or width is generated because no supported route-width or clear-width source exists.",
            "No elevation model exists; gradient and vertical clearance remain not assessed.",
            "No path surface, construction, barrier, accessibility, pedestrian/vehicle suitability, legal/public access or emergency-egress facts are inferred.",
            "Mapped terrain intersections are recorded as context only and are not classified as impassable obstacles.",
            "The four point-contact-only road-reserve relationships remain distinct from frontage candidates.",
            "No operational access points, canonical addresses, operational spatial IDs, ownership, tenancy, occupancy or business assignments are created.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    result = build_route_corridor_candidates(source)
    Path("bp04-03-route-corridor-candidates.json").write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["summary"] | {
        "passed_checks": result["passed_checks"],
        "failed_checks": result["failed_checks"],
        "manifest_sha256": result["manifest_sha256"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
