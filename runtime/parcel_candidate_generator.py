"""Deterministic, non-operational parcel-block candidate generator for BP04-03 Stage B.

The output is a planning candidate only. It never allocates sw_geo IDs or canonical addresses.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROAD_RESERVE_M = 15.0
GRID_M = 500.0

LAND_USE = {
    "Westgate Gardens": "residential",
    "Foundry Quarter": "mixed_use",
    "Garden Ward": "residential",
    "Northbank West": "residential",
    "Northbank East": "mixed_use",
    "University Quarter": "education",
    "Assembly Quarter": "civic",
    "Civic Terrace": "civic",
    "Museum Gardens": "open_space",
    "Port Quarter": "port_maritime",
    "Customs Ward": "port_maritime",
    "Marina Point": "waterfront",
    "Parkside": "open_space",
    "Reservoir Ward": "utility",
    "South Gardens": "residential",
    "Industrial Park": "industrial",
    "Rail Yards": "freight_logistics",
    "Canal End": "freight_logistics",
    "Grand Market": "commercial",
    "Exchange Ward": "commercial",
    "Theatre Quarter": "mixed_use",
    "Old Harbour": "waterfront",
    "Ropewalk": "mixed_use",
    "Dockside": "port_maritime",
}


def _bounds(poly):
    ring = poly["coordinates"][0]
    xs, ys = [p[0] for p in ring[:-1]], [p[1] for p in ring[:-1]]
    return min(xs), min(ys), max(xs), max(ys)


def _polygon_bbox(feature):
    geom = feature.get("geometry", {})
    if geom.get("type") != "Polygon":
        return None
    ring = geom.get("coordinates", [[]])[0]
    if len(ring) < 4:
        return None
    xs, ys = [p[0] for p in ring[:-1]], [p[1] for p in ring[:-1]]
    return min(xs), min(ys), max(xs), max(ys)


def _clip_ring_to_rect(ring, rect):
    """Sutherland-Hodgman clipping of a polygon ring to an axis-aligned rectangle."""
    x0, y0, x1, y1 = rect
    points = [tuple(p) for p in ring[:-1]]

    def clip(poly, inside, intersect):
        if not poly:
            return []
        out = []
        previous = poly[-1]
        previous_inside = inside(previous)
        for current in poly:
            current_inside = inside(current)
            if current_inside:
                if not previous_inside:
                    out.append(intersect(previous, current))
                out.append(current)
            elif previous_inside:
                out.append(intersect(previous, current))
            previous, previous_inside = current, current_inside
        return out

    def vertical(boundary, a, b):
        if b[0] == a[0]:
            return (boundary, a[1])
        t = (boundary - a[0]) / (b[0] - a[0])
        return (boundary, a[1] + t * (b[1] - a[1]))

    def horizontal(boundary, a, b):
        if b[1] == a[1]:
            return (a[0], boundary)
        t = (boundary - a[1]) / (b[1] - a[1])
        return (a[0] + t * (b[0] - a[0]), boundary)

    points = clip(points, lambda p: p[0] >= x0, lambda a, b: vertical(x0, a, b))
    points = clip(points, lambda p: p[0] <= x1, lambda a, b: vertical(x1, a, b))
    points = clip(points, lambda p: p[1] >= y0, lambda a, b: horizontal(y0, a, b))
    points = clip(points, lambda p: p[1] <= y1, lambda a, b: horizontal(y1, a, b))
    return points


def _ring_area(points):
    if len(points) < 3:
        return 0.0
    return abs(sum(
        points[i][0] * points[(i + 1) % len(points)][1]
        - points[(i + 1) % len(points)][0] * points[i][1]
        for i in range(len(points))
    )) / 2.0


def _polygon_rect_intersection_area(feature, rect):
    """Exact area for a single simple Polygon outer ring clipped to a rectangle.

    Current SW-GEO-V1 water polygons are single-ring rectangles. Interior holes
    and MultiPolygon geometry are deliberately rejected rather than guessed.
    """
    geom = feature.get("geometry", {})
    if geom.get("type") != "Polygon":
        raise ValueError("Only Polygon water geometry is supported by Stage B v2")
    rings = geom.get("coordinates", [])
    if len(rings) != 1:
        raise ValueError("Water polygon holes require an explicit geometry implementation")
    clipped = _clip_ring_to_rect(rings[0], rect)
    return _ring_area(clipped)


def _overlaps(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def _edge_frontages(box, segments):
    x0, y0, x1, y1 = box
    found = set()
    for seg in segments:
        geom = seg.get("geometry", [])
        if len(geom) < 2:
            continue
        (ax, ay), (bx, by) = geom[0], geom[-1]
        if ay == by:
            lo, hi = sorted((ax, bx))
            if ay in (y0, y1) and lo <= x0 and hi >= x1:
                found.add("south" if ay == y0 else "north")
        elif ax == bx:
            lo, hi = sorted((ay, by))
            if ax in (x0, x1) and lo <= y0 and hi >= y1:
                found.add("west" if ax == x0 else "east")
    return sorted(found)


def build_candidates(source: dict) -> dict:
    hoods = source["neighbourhoods"]
    segments = source["network"]["segments"]
    water = [
        f for f in source.get("features", [])
        if f.get("properties", {}).get("entity_type") in ("harbour_water", "constructed_water")
    ]
    for feature in water:
        if _polygon_bbox(feature) is None:
            raise ValueError(f"Invalid water polygon feature: {feature.get('id')}")
    parcels, conflicts, coverage = [], [], []
    for hood in sorted(hoods, key=lambda x: x["id"]):
        x0, y0, x1, y1 = _bounds(hood["geometry"])
        if any(v % GRID_M for v in (x0, y0, x1, y1)):
            raise ValueError(f"Neighbourhood grid bounds are not divisible by {GRID_M}: {hood['id']}")
        local_count = 0
        ix = 0
        y = y0
        while y < y1:
            x = x0
            while x < x1:
                ix += 1
                cell = (x, y, x + GRID_M, y + GRID_M)
                water_intersections = [
                    (i, _polygon_rect_intersection_area(feature, cell))
                    for i, feature in enumerate(water)
                ]
                water_hits = [(i, area) for i, area in water_intersections if area > 0]
                if water_hits:
                    conflicts.append({
                        "candidate_cell_id": f"WATER-{hood['id']}-{ix:03d}",
                        "source_neighbourhood_id": hood["id"],
                        "cell_bbox_m": list(cell),
                        "conflict": "exact_water_polygon_intersection",
                        "water_feature_ids": [water[i].get("id") for i, _ in water_hits],
                        "intersection_area_m2": round(sum(area for _, area in water_hits), 3),
                        "status": "EXCLUDED_UNRESOLVED",
                    })
                else:
                    inner = (x + ROAD_RESERVE_M, y + ROAD_RESERVE_M,
                             x + GRID_M - ROAD_RESERVE_M, y + GRID_M - ROAD_RESERVE_M)
                    frontage = _edge_frontages(cell, segments)
                    local_count += 1
                    parcels.append({
                        "candidate_parcel_id": f"BPC-{hood['id'].replace('-', '')}-{ix:03d}",
                        "source_dataset": source["dataset_id"],
                        "source_neighbourhood_id": hood["id"],
                        "source_district_id": hood["district_id"],
                        "land_use_code": LAND_USE[hood["name"]],
                        "development_state": "unknown",
                        "geometry_format": "local_grid_polygon_v2",
                        "geometry": [[
                            [inner[0], inner[1]], [inner[2], inner[1]],
                            [inner[2], inner[3]], [inner[0], inner[3]],
                            [inner[0], inner[1]]
                        ]],
                        "area_m2": (inner[2] - inner[0]) * (inner[3] - inner[1]),
                        "area_basis": "derived_geometry",
                        "road_frontage_edges": frontage,
                        "frontage_status": "SUPPORTED_CANDIDATE" if frontage else "UNRESOLVED",
                        "geometry_quality": "candidate_unreviewed",
                        "epistemic_status": "generated_design_value",
                        "candidate_spatial_id": None,
                        "canonical_address_id": None,
                        "source_ref": f"{source['dataset_id']}:{hood['id']}:500m-cell:{ix:03d}",
                        "actor_ref": "BP04-03-STAGE-B-GENERATOR-V2",
                        "confidence_code": "estimated",
                        "reason": "Deterministic 500m planning-grid cell inset by a 15m candidate road-reserve allowance; not surveyed or operationally approved.",
                    })
                x += GRID_M
            y += GRID_M
        coverage.append({
            "source_neighbourhood_id": hood["id"],
            "candidate_parcel_count": local_count,
            "excluded_water_conflict_cells": sum(1 for c in conflicts if c["source_neighbourhood_id"] == hood["id"]),
            "coverage_status": "CANDIDATE_ONLY",
        })
    # Deterministic topology checks: candidate interiors must remain inside
    # their source neighbourhood and may not overlap another candidate interior.
    parcel_boxes = []
    for parcel in parcels:
        ring = parcel["geometry"][0]
        xs = [p[0] for p in ring[:-1]]
        ys = [p[1] for p in ring[:-1]]
        parcel_boxes.append((
            parcel["candidate_parcel_id"],
            parcel["source_neighbourhood_id"],
            (min(xs), min(ys), max(xs), max(ys)),
        ))
    neighbourhood_bounds = {
        hood["id"]: _bounds(hood["geometry"]) for hood in hoods
    }
    topology_violations = []
    for parcel_id, hood_id, box in parcel_boxes:
        hb = neighbourhood_bounds[hood_id]
        if box[0] < hb[0] or box[1] < hb[1] or box[2] > hb[2] or box[3] > hb[3]:
            topology_violations.append({
                "type": "candidate_outside_neighbourhood",
                "candidate_parcel_id": parcel_id,
                "source_neighbourhood_id": hood_id,
            })
    for i, (left_id, left_hood, left_box) in enumerate(parcel_boxes):
        for right_id, right_hood, right_box in parcel_boxes[i + 1:]:
            if left_hood == right_hood and _overlaps(left_box, right_box):
                topology_violations.append({
                    "type": "candidate_interior_overlap",
                    "candidate_parcel_ids": [left_id, right_id],
                    "source_neighbourhood_id": left_hood,
                })
    if topology_violations:
        raise ValueError(f"Candidate topology validation failed: {topology_violations[:5]}")

    source_grid_cells = sum(
        int((_bounds(h["geometry"])[2] - _bounds(h["geometry"])[0]) / GRID_M)
        * int((_bounds(h["geometry"])[3] - _bounds(h["geometry"])[1]) / GRID_M)
        for h in hoods
    )
    body = {
        "schema": "saltwater-bp04-03-parcel-candidates/1.0",
        "candidate_set_id": "BP04-03-STAGE-B-PARCEL-CANDIDATES-001",
        "source_dataset": source["dataset_id"],
        "source_status": source["status"],
        "operational_approval": False,
        "generation": {
            "generator": "BP04-03-STAGE-B-GENERATOR-V2",
            "grid_cell_m": GRID_M,
            "road_reserve_inset_m": ROAD_RESERVE_M,
            "geometry_crs": source["coordinate_reference"]["id"],
            "geometry_units": "metres",
            "parcel_candidate_count": len(parcels),
            "excluded_water_conflict_count": len(conflicts),
            "source_grid_cell_count": source_grid_cells,
            "topology": {
                "candidate_interiors_within_neighbourhoods": True,
                "candidate_interior_overlap_count": 0,
                "candidate_outside_neighbourhood_count": 0,
                "validation": "PASS",
                "unallocated_area_note": "The difference between neighbourhood envelopes and candidate parcel interiors includes provisional 15m grid insets and entire cells excluded where water intersects; it is not classified as road, public space or developable land.",
            },
            "unresolved_source_spatial_mappings": 100,
            "spatial_ids_assigned": 0,
            "canonical_addresses_created": 0,
        },
        "coverage_by_neighbourhood": coverage,
        "parcels": parcels,
        "excluded_cells": conflicts,
        "address_generation": {
            "status": "BLOCKED_PENDING_BP02_SOURCE_MAPPING_AND_FRONTAGE_REVIEW",
            "records_created": 0,
            "reason": "No candidate is assigned a canonical road or address ID. No street number or operational locator is inferred.",
        },
        "limitations": [
            "Planning-grade grid-derived candidates only; not final cadastral parcels.",
            "Cells with positive-area intersection against exact water polygon rings are excluded and explicitly listed for resolution.",
            "A 15m inset is a generated road-reserve allowance, not an approved right-of-way width.",
            "Candidate frontage is a geometric edge match only; access, legal frontage and route connectivity remain unverified. The 15m inset is still a provisional grid assumption, not a surveyed road-reserve polygon.",
            "No parcel is approved, canonical or eligible for production import.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    output = build_candidates(source)
    target = Path("bp04-03-stage-b-parcel-candidates.json")
    target.write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_parcels": output["generation"]["parcel_candidate_count"],
        "water_conflict_cells": output["generation"]["excluded_water_conflict_count"],
        "neighbourhoods_covered": len(output["coverage_by_neighbourhood"]),
        "frontage_supported": sum(1 for p in output["parcels"] if p["frontage_status"] == "SUPPORTED_CANDIDATE"),
        "frontage_unresolved": sum(1 for p in output["parcels"] if p["frontage_status"] == "UNRESOLVED"),
        "manifest_sha256": output["manifest_sha256"],
        "operational_approval": output["operational_approval"],
        "spatial_ids_assigned": output["generation"]["spatial_ids_assigned"],
        "canonical_addresses_created": output["generation"]["canonical_addresses_created"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
