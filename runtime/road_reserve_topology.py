"""Dissolve fictional road corridors and reconcile them to city/neighbourhood boundaries."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon, mapping, shape
from shapely.ops import unary_union


def _geojson_polygon(value, label):
    geom = shape(value)
    if not geom.is_valid or geom.is_empty or geom.geom_type != "Polygon":
        raise ValueError(f"{label} must be a valid non-empty Polygon")
    return geom


def build_road_reserve_topology(source: dict, corridor_register: dict) -> dict:
    if corridor_register.get("road_reserve_width_source") != "SW-RDS-V1":
        raise ValueError("Road corridor register does not use SW-RDS-V1")
    segments = corridor_register["segments"]
    if len(segments) != len(source["network"]["segments"]):
        raise ValueError("Corridor register segment count does not match source network")

    segment_polygons = []
    for item in segments:
        coords = item.get("reserve_polygon")
        if not coords or len(coords) != 1:
            raise ValueError(f"Missing segment corridor polygon: {item['segment_id']}")
        polygon = Polygon(coords[0])
        if polygon.is_empty or not polygon.is_valid or polygon.area <= 0:
            raise ValueError(f"Invalid segment corridor polygon: {item['segment_id']}")
        segment_polygons.append((item, polygon))

    raw_union = unary_union([p for _, p in segment_polygons])
    if raw_union.is_empty or not raw_union.is_valid:
        raise ValueError("Dissolved road reserve is empty or invalid")

    city_features = [
        f for f in source["features"]
        if f.get("properties", {}).get("entity_type") == "city_state_boundary"
    ]
    if len(city_features) != 1:
        raise ValueError("Expected exactly one sovereign city boundary")
    city = _geojson_polygon(city_features[0]["geometry"], "city boundary")
    outside_city = raw_union.difference(city)
    clipped = raw_union.intersection(city)
    if clipped.is_empty or not clipped.is_valid:
        raise ValueError("City-clipped road reserve is empty or invalid")

    neighbourhoods = source["neighbourhoods"]
    hood_geometries = []
    for hood in neighbourhoods:
        geom = _geojson_polygon(hood["geometry"], f"neighbourhood {hood['id']}")
        if not city.covers(geom):
            raise ValueError(f"Neighbourhood lies outside city boundary: {hood['id']}")
        hood_geometries.append((hood, geom))

    hood_union = unary_union([g for _, g in hood_geometries])
    overlap_area = sum(g.area for _, g in hood_geometries) - hood_union.area
    gap_geometry = city.difference(hood_union)
    outside_geometry = hood_union.difference(city)
    if overlap_area > 0.001:
        raise ValueError(f"Neighbourhood polygons overlap by {overlap_area} m2")
    if gap_geometry.area > 0.001:
        raise ValueError(f"Neighbourhood coverage gap: {gap_geometry.area} m2")
    if outside_geometry.area > 0.001:
        raise ValueError(f"Neighbourhood polygons exceed city boundary by {outside_geometry.area} m2")

    by_neighbourhood = []
    allocated_geometries = []
    for hood, geom in sorted(hood_geometries, key=lambda pair: pair[0]["id"]):
        reserve = clipped.intersection(geom)
        allocated_geometries.append(reserve)
        by_neighbourhood.append({
            "neighbourhood_id": hood["id"],
            "neighbourhood_name": hood["name"],
            "neighbourhood_area_m2": round(geom.area, 3),
            "road_reserve_area_m2": round(reserve.area, 3),
            "road_reserve_geometry": mapping(reserve),
            "intersecting_segment_count": sum(1 for _, p in segment_polygons if p.intersects(geom)),
        })

    allocated_area = sum(g.area for g in allocated_geometries)
    if abs(allocated_area - clipped.area) > 0.001:
        raise ValueError("Neighbourhood road-reserve allocation does not reconcile to dissolved city road reserve")

    body = {
        "schema": "saltwater-bp04-03-road-reserve-topology/1.0",
        "audit_id": "BP04-03-STAGE-C-ROAD-RESERVE-TOPOLOGY-001",
        "source_dataset": source["dataset_id"],
        "road_reserve_design_standard": "SW-RDS-V1",
        "operational_approval": False,
        "summary": {
            "segment_corridor_count": len(segment_polygons),
            "dissolved_road_reserve_component_count": len(getattr(clipped, "geoms", [clipped])),
            "city_boundary_area_m2": round(city.area, 3),
            "neighbourhood_count": len(hood_geometries),
            "neighbourhood_union_area_m2": round(hood_union.area, 3),
            "neighbourhood_overlap_area_m2": round(overlap_area, 6),
            "neighbourhood_gap_area_m2": round(gap_geometry.area, 6),
            "neighbourhood_outside_city_area_m2": round(outside_geometry.area, 6),
            "sum_of_segment_corridor_areas_m2": round(sum(p.area for _, p in segment_polygons), 3),
            "junction_overlap_area_removed_by_dissolve_m2": round(sum(p.area for _, p in segment_polygons) - raw_union.area, 3),
            "raw_road_reserve_area_before_city_clip_m2": round(raw_union.area, 3),
            "road_reserve_outside_city_area_m2": round(outside_city.area, 3),
            "dissolved_city_road_reserve_area_m2": round(clipped.area, 3),
            "sum_neighbourhood_road_reserve_area_m2": round(allocated_area, 3),
            "road_reserve_allocation_delta_m2": round(allocated_area - clipped.area, 6),
            "boundary_topology_status": "PASS",
            "road_reserve_allocation_status": "PASS",
        },
        "city_road_reserve_geometry": mapping(clipped),
        "coverage_by_neighbourhood": by_neighbourhood,
        "method": {
            "segment_corridors": "SW-RDS-V1 class width applied to source centre-lines using mitered offsets",
            "dissolve": "Shapely unary_union of all segment corridor polygons",
            "city_edge": "Clip dissolved road reserve to sovereign city-state boundary",
            "neighbourhood_allocation": "Intersect dissolved city road reserve with each of 24 neighbourhood polygons",
            "junction_overlap": "Dissolved once before area accounting; no duplicate junction area",
        },
        "limitations": [
            "This is fictional game-world geography, not a real survey or cadastral plan.",
            "The city boundary and neighbourhood polygons are the current canonical SW-GEO-V1 rectangles.",
            "Road-reserve widths are fictional design dimensions from SW-RDS-V1.",
            "Parcel frontage and parcel boundaries are not created by this operation.",
            "No land ownership, occupancy, property or building count is inferred from road reserve area.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    from runtime.road_corridor_audit import build_road_corridor_audit
    corridors = build_road_corridor_audit(source)
    result = build_road_reserve_topology(source, corridors)
    Path("bp04-03-road-reserve-topology.json").write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"] | {"manifest_sha256": result["manifest_sha256"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
