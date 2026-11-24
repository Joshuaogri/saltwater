"""Geometry-derived BP04-03 parcel candidates from fictional roads and water."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon, box, mapping, shape
from shapely.ops import unary_union

GRID_M = 500.0

LAND_USE = {
    "Westgate Gardens": "residential", "Foundry Quarter": "mixed_use",
    "Garden Ward": "residential", "Northbank West": "residential",
    "Northbank East": "mixed_use", "University Quarter": "education",
    "Assembly Quarter": "civic", "Civic Terrace": "civic",
    "Museum Gardens": "open_space", "Port Quarter": "port_maritime",
    "Customs Ward": "port_maritime", "Marina Point": "waterfront",
    "Parkside": "open_space", "Reservoir Ward": "utility",
    "South Gardens": "residential", "Industrial Park": "industrial",
    "Rail Yards": "freight_logistics", "Canal End": "freight_logistics",
    "Grand Market": "commercial", "Exchange Ward": "commercial",
    "Theatre Quarter": "mixed_use", "Old Harbour": "waterfront",
    "Ropewalk": "mixed_use", "Dockside": "port_maritime",
}


def _polygon(value, label):
    geom = shape(value)
    if geom.geom_type != "Polygon" or geom.is_empty or not geom.is_valid or geom.area <= 0:
        raise ValueError(f"{label} must be a valid non-empty Polygon")
    return geom


def _polygon_parts(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom] if geom.area > 0.000001 else []
    if geom.geom_type == "MultiPolygon":
        return sorted(
            [p for p in geom.geoms if p.area > 0.000001],
            key=lambda p: (round(p.centroid.x, 6), round(p.centroid.y, 6), round(p.area, 6), p.wkb_hex),
        )
    if geom.geom_type == "GeometryCollection":
        parts = []
        for part in geom.geoms:
            parts.extend(_polygon_parts(part))
        return sorted(parts, key=lambda p: (round(p.centroid.x, 6), round(p.centroid.y, 6), round(p.area, 6), p.wkb_hex))
    return []


def _candidate_name(candidate_id: str, occupied: set[str]) -> str:
    """Generate a deterministic, pronounceable fictional parcel name."""
    import hashlib
    onsets = ("", "b", "br", "d", "dr", "f", "g", "gr", "h", "k", "l", "m", "n", "p", "r", "s", "sh", "t", "th", "v", "w", "z")
    vowels = ("a", "e", "i", "o", "u", "ae", "ai", "ea", "ei", "ia", "io", "oa", "ou")
    codas = ("n", "r", "l", "m", "s", "th", "nd", "st", "rn", "v", "k", "")
    for attempt in range(1000):
        digest = hashlib.sha256(
            f"saltwater:SW-UNS-plot-name-v1:{candidate_id}:{attempt}".encode()
        ).digest()
        parts = []
        offset = 0
        for _ in range(3):
            onset = onsets[digest[offset] % len(onsets)]
            vowel = vowels[digest[offset + 1] % len(vowels)]
            coda = codas[digest[offset + 2] % len(codas)]
            parts.append(onset + vowel + coda)
            offset += 3
        name = "".join(parts).capitalize()
        if name.casefold() not in occupied:
            occupied.add(name.casefold())
            return name
    raise ValueError(f"Could not generate a unique candidate name for {candidate_id}")


def _rings(poly):
    return [
        [[round(float(x), 9), round(float(y), 9)] for x, y in list(poly.exterior.coords)],
        *[
            [[round(float(x), 6), round(float(y), 6)] for x, y in list(ring.coords)]
            for ring in poly.interiors
        ],
    ]


def _feature_water(source):
    water = []
    for feature in source.get("features", []):
        if feature.get("properties", {}).get("entity_type") in ("harbour_water", "constructed_water"):
            geom = _polygon(feature["geometry"], f"water feature {feature.get('id')}")
            water.append((feature.get("id"), geom))
    for i, (left_id, left) in enumerate(water):
        for right_id, right in water[i + 1:]:
            if left.intersection(right).area > 0.001:
                raise ValueError(f"Overlapping water polygons would double-count area: {left_id}, {right_id}")
    return water


def build_candidates(source: dict) -> dict:
    from runtime.road_corridor_audit import build_road_corridor_audit
    from runtime.road_reserve_topology import build_road_reserve_topology

    corridors = build_road_corridor_audit(source)
    topology = build_road_reserve_topology(source, corridors)
    road_reserve = shape(topology["city_road_reserve_geometry"])
    if not road_reserve.is_valid or road_reserve.is_empty:
        raise ValueError("Dissolved fictional road reserve is invalid")
    road_edge_boundary = road_reserve.boundary
    water_features = _feature_water(source)
    water_union = unary_union([g for _, g in water_features]) if water_features else Polygon()
    if not water_union.is_valid:
        raise ValueError("Water union is invalid")
    water_ids = [(fid, geom) for fid, geom in water_features]

    parcels, cell_audit, coverage = [], [], []
    occupied_names: set[str] = set()
    total_source_area = total_road_area = total_water_area = total_candidate_area = 0.0
    source_cell_count = 0

    for hood in sorted(source["neighbourhoods"], key=lambda h: h["id"]):
        hood_geom = _polygon(hood["geometry"], f"neighbourhood {hood['id']}")
        minx, miny, maxx, maxy = hood_geom.bounds
        if any(abs(v / GRID_M - round(v / GRID_M)) > 1e-9 for v in (minx, miny, maxx, maxy)):
            raise ValueError(f"Neighbourhood grid bounds are not aligned to {GRID_M}m: {hood['id']}")
        hood_road = road_reserve.intersection(hood_geom)
        hood_water = water_union.intersection(hood_geom).difference(hood_road)
        developable = hood_geom.difference(unary_union([hood_road, water_union]))
        if not developable.is_valid:
            raise ValueError(f"Invalid developable geometry in {hood['id']}")

        hood_parcels = []
        cell_index = 0
        y = miny
        while y < maxy - 1e-8:
            x = minx
            while x < maxx - 1e-8:
                cell_index += 1
                source_cell_count += 1
                cell = box(x, y, min(x + GRID_M, maxx), min(y + GRID_M, maxy))
                cell_land = cell.intersection(hood_geom).difference(unary_union([road_reserve, water_union]))
                parts = _polygon_parts(cell_land)
                water_area = cell.intersection(hood_geom).intersection(water_union).area
                road_area = cell.intersection(hood_geom).intersection(road_reserve).area
                cell_audit.append({
                    "source_neighbourhood_id": hood["id"],
                    "source_cell_index": cell_index,
                    "source_cell_bounds_m": [x, y, min(x + GRID_M, maxx), min(y + GRID_M, maxy)],
                    "road_reserve_area_m2": round(road_area, 6),
                    "water_intersection_area_m2": round(water_area, 6),
                    "candidate_component_count": len(parts),
                    "candidate_land_area_m2": round(sum(p.area for p in parts), 6),
                })
                for component_no, poly in enumerate(parts, start=1):
                    parcel_id = f"BPC-{hood['id'].replace('-', '')}-{cell_index:03d}-{component_no:02d}"
                    frontage = []
                    boundary = poly.boundary
                    actual_road_edge_contact = boundary.intersection(road_edge_boundary)
                    if actual_road_edge_contact.length > 0.01:
                        for segment in corridors["segments"]:
                            seg_poly = Polygon(segment["reserve_polygon"][0])
                            shared = boundary.intersection(seg_poly.boundary).intersection(road_edge_boundary)
                            if shared.length > 0.01:
                                frontage.append(segment["segment_id"])
                    parcel = {
                        "candidate_parcel_id": parcel_id,
                        "display_name": _candidate_name(parcel_id, occupied_names),
                        "source_dataset": source["dataset_id"],
                        "source_neighbourhood_id": hood["id"],
                        "source_district_id": hood["district_id"],
                        "land_use_code": LAND_USE[hood["name"]],
                        "development_state": "unknown",
                        "geometry_format": "polygon_with_optional_interior_rings",
                        "geometry": _rings(poly),
                        "area_m2": round(poly.area, 3),
                        "area_basis": "derived_geometry",
                        "road_frontage_segment_ids": sorted(set(frontage)),
                        "frontage_status": "ROAD_RESERVE_EDGE_CONTACT_CANDIDATE" if frontage else "NO_ROAD_EDGE_CONTACT_IDENTIFIED",
                        "geometry_quality": "candidate_unreviewed",
                        "epistemic_status": "generated_design_value",
                        "candidate_spatial_id": None,
                        "canonical_address_id": None,
                        "source_ref": f"{source['dataset_id']}:{hood['id']}:500m-cell:{cell_index:03d}:component:{component_no:02d}",
                        "actor_ref": "BP04-03-STAGE-B-GENERATOR-V3",
                        "confidence_code": "estimated",
                        "reason": "Deterministic polygon component generated by intersecting the source neighbourhood and 500m lineage cell, then subtracting SW-RDS-V1 dissolved road reserve and mapped water; planning candidate only.",
                    }
                    parcels.append(parcel)
                    hood_parcels.append(parcel)

                x += GRID_M
            y += GRID_M

        parcel_union = unary_union([Polygon(p["geometry"][0], p["geometry"][1:]) for p in hood_parcels]) if hood_parcels else Polygon()
        overlap = sum(Polygon(p["geometry"][0], p["geometry"][1:]).area for p in hood_parcels) - parcel_union.area
        delta = hood_geom.area - hood_road.area - hood_water.area - parcel_union.area
        if abs(overlap) > 0.001 or abs(delta) > 0.01:
            raise ValueError(f"Parcel coverage does not reconcile in {hood['id']}: overlap={overlap}, delta={delta}")
        coverage.append({
            "neighbourhood_id": hood["id"],
            "neighbourhood_name": hood["name"],
            "source_area_m2": round(hood_geom.area, 3),
            "road_reserve_area_m2": round(hood_road.area, 3),
            "water_area_outside_road_reserve_m2": round(hood_water.area, 3),
            "candidate_land_area_m2": round(parcel_union.area, 3),
            "candidate_parcel_count": len(hood_parcels),
            "area_balance_delta_m2": round(delta, 6),
            "topology_status": "PASS",
        })
        total_source_area += hood_geom.area
        total_road_area += hood_road.area
        total_water_area += hood_water.area
        total_candidate_area += parcel_union.area

    ids = [p["candidate_parcel_id"] for p in parcels]
    if len(ids) != len(set(ids)):
        raise ValueError("Deterministic parcel candidate IDs are not unique")
    body = {
        "schema": "saltwater-bp04-03-parcel-candidates/2.0",
        "candidate_set_id": "BP04-03-STAGE-B-PARCEL-CANDIDATES-002",
        "source_dataset": source["dataset_id"],
        "source_status": source["status"],
        "operational_approval": False,
        "generation": {
            "generator": "BP04-03-STAGE-B-GENERATOR-V3",
            "grid_cell_m": GRID_M,
            "road_reserve_design_standard": "SW-RDS-V1",
            "road_reserve_geometry_source": "DISSOLVED_685_SEGMENT_CORRIDORS",
            "parcel_candidate_count": len(parcels),
            "source_grid_cell_count": source_cell_count,
            "water_feature_count": len(water_features),
            "water_intersection_cell_count": sum(1 for c in cell_audit if c["water_intersection_area_m2"] > 0),
            "candidate_component_count": len(parcels),
            "source_area_m2": round(total_source_area, 3),
            "road_reserve_area_m2": round(total_road_area, 3),
            "water_area_outside_road_reserve_m2": round(total_water_area, 3),
            "candidate_land_area_m2": round(total_candidate_area, 3),
            "area_balance_delta_m2": round(total_source_area-total_road_area-total_water_area-total_candidate_area, 6),
            "topology_validation": "PASS",
            "unresolved_source_spatial_mappings": 100,
            "spatial_ids_assigned": 0,
            "canonical_addresses_created": 0,
        },
        "coverage_by_neighbourhood": coverage,
        "source_cell_audit": cell_audit,
        "parcels": parcels,
        "excluded_cells": [],
        "address_generation": {
            "status": "BLOCKED_PENDING_BP02_SOURCE_MAPPING_AND_ADDRESS_DESIGN",
            "records_created": 0,
            "reason": "This candidate generation does not allocate operational spatial IDs, street numbers or canonical addresses.",
        },
        "limitations": [
            "Fictional game-world design geometry only; not a real survey or cadastral register.",
            "Parcel candidate polygons are cell-lineage components after subtracting road-reserve and water geometry.",
            "Road frontage is a geometric boundary-contact candidate, not legal frontage or proof of a usable entrance.",
            "The 500m source cells preserve deterministic lineage but do not assert final cadastral boundaries.",
            "No ownership, tenancy, occupancy, business operator, property/building count or canonical address is inferred.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    result = build_candidates(source)
    Path("bp04-03-stage-b-parcel-candidates.json").write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "candidate_parcels": result["generation"]["parcel_candidate_count"],
        "source_cells": result["generation"]["source_grid_cell_count"],
        "water_intersection_cells": result["generation"]["water_intersection_cell_count"],
        "road_reserve_area_m2": result["generation"]["road_reserve_area_m2"],
        "candidate_land_area_m2": result["generation"]["candidate_land_area_m2"],
        "area_balance_delta_m2": result["generation"]["area_balance_delta_m2"],
        "frontage_candidates": sum(1 for p in result["parcels"] if p["road_frontage_segment_ids"]),
        "manifest_sha256": result["manifest_sha256"],
        "operational_approval": result["operational_approval"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
