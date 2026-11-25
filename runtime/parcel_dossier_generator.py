"""Detailed, non-operational parcel dossiers and spatial relationship candidates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon, Point
from shapely.ops import linemerge, unary_union
from shapely.strtree import STRtree

from runtime.parcel_candidate_generator import build_candidates
from runtime.road_corridor_audit import build_road_corridor_audit
from runtime.road_reserve_topology import build_road_reserve_topology


def _polygon(parcel):
    return Polygon(parcel["geometry"][0], parcel["geometry"][1:])


def _line_parts(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        return [geometry] if geometry.length > 0 else []
    if hasattr(geometry, "geoms"):
        parts = []
        for item in geometry.geoms:
            parts.extend(_line_parts(item))
        return parts
    return []


def build_parcel_dossiers(source: dict, candidate_manifest: dict | None = None) -> dict:
    candidates = candidate_manifest or build_candidates(source)
    if candidates.get("operational_approval") is not False:
        raise ValueError("Only non-operational parcel candidate manifests are accepted")
    if candidates.get("source_dataset") != source.get("dataset_id"):
        raise ValueError("Parcel candidate manifest source dataset mismatch")

    corridors = build_road_corridor_audit(source)
    reserve = build_road_reserve_topology(source, corridors)
    road_reserve = __import__("shapely.geometry", fromlist=["shape"]).shape(
        reserve["city_road_reserve_geometry"]
    )
    water_features = [
        f for f in source.get("features", [])
        if f.get("properties", {}).get("entity_type") in ("harbour_water", "constructed_water")
    ]
    water_geometries = [(f["id"], __import__("shapely.geometry", fromlist=["shape"]).shape(f["geometry"])) for f in water_features]
    water_union = unary_union([g for _, g in water_geometries]) if water_geometries else None

    roads = {r["id"]: r for r in source["roads"]}
    segment_by_id = {s["segment_id"]: s for s in corridors["segments"]}
    segment_polygons = {
        sid: Polygon(segment["reserve_polygon"][0])
        for sid, segment in segment_by_id.items()
    }
    road_edge_boundary = road_reserve.boundary

    parcel_rows = []
    parcel_geometries = []
    for parcel in candidates["parcels"]:
        geom = _polygon(parcel)
        if geom.is_empty or not geom.is_valid or geom.area <= 0:
            raise ValueError(f"Invalid parcel geometry: {parcel['candidate_parcel_id']}")
        boundary = geom.boundary
        frontage_rows = []
        access_rows = []
        contacts_by_road = {}
        for segment_id in parcel.get("road_frontage_segment_ids", []):
            segment = segment_by_id[segment_id]
            contact = boundary.intersection(segment_polygons[segment_id].boundary)
            lines = _line_parts(contact)
            if sum(line.length for line in lines) > 0.01:
                contacts_by_road.setdefault(segment["road_id"], []).append((segment, lines))

        # A continuous parcel edge along one named road is one frontage
        # candidate, even when the road centre-line is split into many source
        # network segments. Access-location candidates are therefore not
        # multiplied by every small road-network segment.
        for road_id in sorted(contacts_by_road):
            entries = contacts_by_road[road_id]
            all_lines = [line for _, lines in entries for line in lines]
            merged = unary_union(all_lines)
            if merged.geom_type in ("MultiLineString", "GeometryCollection"):
                merged = linemerge(merged)
            components = sorted(
                _line_parts(merged),
                key=lambda line: (round(line.bounds[0], 6), round(line.bounds[1], 6),
                                  round(line.bounds[2], 6), round(line.bounds[3], 6), line.wkb_hex),
            )
            road = roads[road_id]
            classes = {segment["road_class"] for segment, _ in entries}
            if len(classes) != 1:
                raise ValueError(f"Road {road_id} has inconsistent segment classes")
            if not components:
                continue
            contributing_segments = sorted({
                segment["segment_id"]
                for segment, source_lines in entries
                if sum(
                    component.intersection(source_line).length
                    for component in components for source_line in source_lines
                ) > 0.01
            })
            if not contributing_segments:
                raise ValueError(f"Frontage component has no source segment: {parcel['candidate_parcel_id']}")
            longest = sorted(components, key=lambda line: (-line.length, line.wkb_hex))[0]
            point = longest.interpolate(0.5, normalized=True)
            frontage_id = f"PFC-{parcel['candidate_parcel_id']}-{road_id}"
            total_contact_length = sum(line.length for line in components)
            frontage_rows.append({
                "frontage_candidate_id": frontage_id,
                "road_segment_ids": contributing_segments,
                "road_id": road_id,
                "road_name": road["name"],
                "road_class": next(iter(classes)),
                "contact_length_m": round(total_contact_length, 3),
                "contact_component_count": len(components),
                "candidate_point_x_m": round(point.x, 6),
                "candidate_point_y_m": round(point.y, 6),
                "source_ref": f"{source['dataset_id']}:{road_id}:{','.join(contributing_segments)}",
                "confidence_code": "estimated",
            })
            access_rows.append({
                "access_candidate_id": f"PAC-{parcel['candidate_parcel_id']}-{road_id}",
                "frontage_candidate_id": frontage_id,
                "road_id": road_id,
                "candidate_x_m": round(point.x, 6),
                "candidate_y_m": round(point.y, 6),
                "candidate_type": "unclassified_access_location",
                "review_status": "UNREVIEWED_GEOMETRIC_CANDIDATE",
                "source_ref": f"{source['dataset_id']}:{road_id}",
                "confidence_code": "estimated",
            })


        unique_frontage_length = boundary.intersection(road_reserve.boundary).length
        water_contact = boundary.intersection(water_union.boundary).length if water_union else 0.0
        water_adjacencies = []
        for feature_id, water in water_geometries:
            contact_length = boundary.intersection(water.boundary).length
            if contact_length > 0.01:
                water_adjacencies.append({
                    "water_feature_id": feature_id,
                    "contact_length_m": round(contact_length, 3),
                    "source_ref": f"{source['dataset_id']}:{feature_id}",
                    "confidence_code": "estimated",
                })
        adjacent_water_ids = sorted(row["water_feature_id"] for row in water_adjacencies)
        centroid = geom.centroid
        label_point = geom.representative_point()
        area = geom.area
        perimeter = geom.length
        compactness = (4.0 * 3.141592653589793 * area / (perimeter * perimeter)) if perimeter else 0.0
        minx, miny, maxx, maxy = geom.bounds
        dossier = {
            "candidate_parcel_id": parcel["candidate_parcel_id"],
            "source_neighbourhood_id": parcel["source_neighbourhood_id"],
            "source_district_id": parcel["source_district_id"],
            "display_name": parcel["display_name"],
            "area_m2": round(area, 3),
            "perimeter_m": round(perimeter, 3),
            "compactness_index": round(compactness, 8),
            "centroid_x_m": round(centroid.x, 6),
            "centroid_y_m": round(centroid.y, 6),
            "label_point_x_m": round(label_point.x, 6),
            "label_point_y_m": round(label_point.y, 6),
            "bounds_m": [round(minx, 6), round(miny, 6), round(maxx, 6), round(maxy, 6)],
            "exterior_vertex_count": len(geom.exterior.coords) - 1,
            "interior_ring_count": len(geom.interiors),
            "road_frontage_length_m": round(unique_frontage_length, 3),
            "frontage_segment_count": sum(len(row["road_segment_ids"]) for row in frontage_rows),
            "frontage_candidate_count": len(frontage_rows),
            "water_boundary_contact_length_m": round(water_contact, 3),
            "adjacent_water_feature_ids": adjacent_water_ids,
            "frontage_review_status": "REVIEW_REQUIRED" if frontage_rows else "NO_ROAD_EDGE_CONTACT_REVIEW_REQUIRED",
            "geometry_review_status": "VALID_GENERATED_CANDIDATE",
            "measurement_basis": "DERIVED_FROM_GENERATED_POLYGON_GEOMETRY",
            "source_ref": parcel["source_ref"],
            "actor_ref": "BP04-03-PARCEL-DOSSIER-GENERATOR-V1",
            "confidence_code": "estimated",
            "reason": "Measured from the generated fictional parcel polygon and SW-RDS-V1/water overlays; not a surveyed or operational parcel.",
        }
        parcel_rows.append({
            "dossier": dossier,
            "frontages": sorted(frontage_rows, key=lambda x: (x["road_id"], x["frontage_candidate_id"])),
            "access_candidates": sorted(access_rows, key=lambda x: x["access_candidate_id"]),
            "water_adjacencies": sorted(water_adjacencies, key=lambda x: x["water_feature_id"]),
        })
        parcel_geometries.append(geom)

    # Spatial index produces deterministic unique adjacency pairs, including
    # shared-edge and corner-touch relationships across neighbourhood edges.
    tree = STRtree(parcel_geometries)
    adjacency_rows = []
    for i, left_geom in enumerate(parcel_geometries):
        hits = tree.query(left_geom, predicate="touches")
        for j in sorted(int(value) for value in hits if int(value) > i):
            right_geom = parcel_geometries[j]
            contact = left_geom.boundary.intersection(right_geom.boundary)
            shared_length = contact.length
            if shared_length > 0.01:
                relation = "SHARED_BOUNDARY_CANDIDATE"
            elif not contact.is_empty:
                relation = "CORNER_TOUCH_CANDIDATE"
            else:
                continue
            left = parcel_rows[i]["dossier"]
            right = parcel_rows[j]["dossier"]
            adjacency_rows.append({
                "left_candidate_parcel_id": left["candidate_parcel_id"],
                "left_neighbourhood_id": left["source_neighbourhood_id"],
                "right_candidate_parcel_id": right["candidate_parcel_id"],
                "right_neighbourhood_id": right["source_neighbourhood_id"],
                "relationship_code": relation,
                "shared_boundary_length_m": round(shared_length, 3),
                "source_ref": f"{source['dataset_id']}:{left['candidate_parcel_id']}:{right['candidate_parcel_id']}",
                "actor_ref": "BP04-03-PARCEL-DOSSIER-GENERATOR-V1",
                "confidence_code": "estimated",
                "reason": "Candidate parcel boundary topology derived from intersecting generated polygon boundaries.",
            })

    adjacency_rows.sort(key=lambda row: (row["left_candidate_parcel_id"], row["right_candidate_parcel_id"]))
    if len({(r["left_candidate_parcel_id"], r["right_candidate_parcel_id"]) for r in adjacency_rows}) != len(adjacency_rows):
        raise ValueError("Duplicate parcel adjacency pair")
    if any(r["left_candidate_parcel_id"] >= r["right_candidate_parcel_id"] for r in adjacency_rows):
        raise ValueError("Parcel adjacency pair ordering is not canonical")

    total_area = sum(row["dossier"]["area_m2"] for row in parcel_rows)
    frontage_count = sum(bool(row["frontages"]) for row in parcel_rows)
    access_count = sum(len(row["access_candidates"]) for row in parcel_rows)
    body = {
        "schema": "saltwater-bp04-03-parcel-dossiers/1.0",
        "dossier_set_id": "BP04-03-STAGE-D-PARCEL-DOSSIERS-001",
        "source_dataset": source["dataset_id"],
        "candidate_manifest_sha256": candidates["manifest_sha256"],
        "operational_approval": False,
        "summary": {
            "parcel_dossier_count": len(parcel_rows),
            "valid_geometry_count": len(parcel_rows),
            "frontage_review_required_count": frontage_count,
            "no_road_edge_contact_count": len(parcel_rows) - frontage_count,
            "frontage_candidate_count": sum(len(row["frontages"]) for row in parcel_rows),
            "frontage_segment_contact_count": sum(
                len(frontage["road_segment_ids"]) for row in parcel_rows for frontage in row["frontages"]
            ),
            "frontage_contact_component_count": sum(
                frontage["contact_component_count"] for row in parcel_rows for frontage in row["frontages"]
            ),
            "access_location_candidate_count": access_count,
            "adjacency_relationship_count": len(adjacency_rows),
            "shared_boundary_relationship_count": sum(1 for r in adjacency_rows if r["relationship_code"] == "SHARED_BOUNDARY_CANDIDATE"),
            "corner_touch_relationship_count": sum(1 for r in adjacency_rows if r["relationship_code"] == "CORNER_TOUCH_CANDIDATE"),
            "water_adjacent_parcel_count": sum(bool(row["dossier"]["adjacent_water_feature_ids"]) for row in parcel_rows),
            "water_adjacency_relationship_count": sum(len(row["water_adjacencies"]) for row in parcel_rows),
            "total_candidate_parcel_area_m2": round(total_area, 3),
            "canonical_addresses_created": 0,
            "operational_access_points_created": 0,
            "operational_approval": False,
        },
        "parcels": parcel_rows,
        "adjacency": adjacency_rows,
        "limitations": [
            "Fictional game-world parcel dossier candidates, not real-world cadastral or survey records.",
            "Perimeter, area, centroid, compactness and bounding box are derived from generated polygon geometry.",
            "Road contact is geometric only and does not prove legal frontage or usable access.",
            "Access locations are unreviewed candidates, not operational access-point identities or entrances.",
            "Adjacency is a geometric relationship candidate and does not imply ownership, shared title or a legal boundary agreement.",
            "No property, building, premises, unit, ownership, tenancy, occupancy or canonical address records are created.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    result = build_parcel_dossiers(source)
    Path("bp04-03-parcel-dossiers.json").write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"] | {"manifest_sha256": result["manifest_sha256"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
