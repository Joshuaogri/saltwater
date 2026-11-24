"""Area-balance audit for BP04-03 planning parcel candidates.

Separates candidate parcel interiors, provisional inset residuals, exact
water intersections and unresolved non-water area inside water-hit cells.
It does not classify any residual as road, public space or developable land.
"""
from __future__ import annotations

import json
from pathlib import Path

from runtime.parcel_candidate_generator import (
    GRID_M,
    ROAD_RESERVE_M,
    _bounds,
    _polygon_rect_intersection_area,
    _ring_area,
    build_candidates,
)


def _polygon_area(feature):
    geom = feature.get("geometry", {})
    if geom.get("type") != "Polygon" or len(geom.get("coordinates", [])) != 1:
        raise ValueError(f"Unsupported area geometry: {feature.get('id')}")
    return _ring_area(geom["coordinates"][0][:-1])


def _axis_aligned_rectangle(feature):
    ring = feature["geometry"]["coordinates"][0]
    if len(ring) != 5 or ring[0] != ring[-1]:
        raise ValueError(f"Water geometry is not a closed rectangle: {feature['id']}")
    xs = {p[0] for p in ring[:-1]}
    ys = {p[1] for p in ring[:-1]}
    if len(xs) != 2 or len(ys) != 2:
        raise ValueError(f"Water geometry is not an axis-aligned rectangle: {feature['id']}")
    expected = {
        (min(xs), min(ys)), (max(xs), min(ys)),
        (max(xs), max(ys)), (min(xs), max(ys)),
    }
    if {tuple(p) for p in ring[:-1]} != expected:
        raise ValueError(f"Water rectangle has invalid corners: {feature['id']}")
    return min(xs), min(ys), max(xs), max(ys)


def build_coverage_audit(source: dict) -> dict:
    candidates = build_candidates(source)
    hoods = source["neighbourhoods"]
    water = [
        feature for feature in source.get("features", [])
        if feature.get("properties", {}).get("entity_type") in ("harbour_water", "constructed_water")
    ]
    water_boxes = [(feature, _axis_aligned_rectangle(feature)) for feature in water]
    overlaps = []
    for i, (left, a) in enumerate(water_boxes):
        for right, b in water_boxes[i + 1:]:
            if a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]:
                overlaps.append([left["id"], right["id"]])
    if overlaps:
        raise ValueError(f"Overlapping water polygons would double-count area: {overlaps}")

    source_area = sum(_polygon_area(hood["geometry"]) for hood in hoods)
    source_grid_cells = candidates["generation"]["source_grid_cell_count"]
    candidate_cells = candidates["generation"]["parcel_candidate_count"]
    water_cells = candidates["generation"]["excluded_water_conflict_count"]
    grid_cell_area = GRID_M * GRID_M
    candidate_cell_envelope_area = candidate_cells * grid_cell_area
    water_hit_cell_envelope_area = water_cells * grid_cell_area
    candidate_parcel_area = sum(parcel["area_m2"] for parcel in candidates["parcels"])
    exact_water_intersection_area = sum(
        cell["intersection_area_m2"] for cell in candidates["excluded_cells"]
    )
    provisional_inset_residual = candidate_cell_envelope_area - candidate_parcel_area
    nonwater_area_in_water_hit_cells = water_hit_cell_envelope_area - exact_water_intersection_area
    unallocated_area = source_area - candidate_parcel_area - exact_water_intersection_area

    if source_area != source_grid_cells * grid_cell_area:
        raise ValueError("Neighbourhood area does not reconcile to the source grid envelope")
    if abs(unallocated_area - provisional_inset_residual - nonwater_area_in_water_hit_cells) > 0.001:
        raise ValueError("Area balance does not reconcile")
    if min(provisional_inset_residual, nonwater_area_in_water_hit_cells, unallocated_area) < -0.001:
        raise ValueError("Area balance contains a negative residual")

    by_hood = []
    for hood in sorted(hoods, key=lambda h: h["id"]):
        parcels = [p for p in candidates["parcels"] if p["source_neighbourhood_id"] == hood["id"]]
        excluded = [c for c in candidates["excluded_cells"] if c["source_neighbourhood_id"] == hood["id"]]
        hood_area = _polygon_area(hood["geometry"])
        parcel_area = sum(p["area_m2"] for p in parcels)
        water_area = sum(c["intersection_area_m2"] for c in excluded)
        excluded_envelope = len(excluded) * grid_cell_area
        candidate_envelope = len(parcels) * grid_cell_area
        inset_residual = candidate_envelope - parcel_area
        excluded_nonwater = excluded_envelope - water_area
        by_hood.append({
            "neighbourhood_id": hood["id"],
            "neighbourhood_name": hood["name"],
            "source_area_m2": hood_area,
            "candidate_parcel_count": len(parcels),
            "water_hit_cell_count": len(excluded),
            "candidate_parcel_area_m2": round(parcel_area, 3),
            "exact_water_intersection_area_m2": round(water_area, 3),
            "provisional_inset_residual_m2": round(inset_residual, 3),
            "unresolved_nonwater_area_in_water_hit_cells_m2": round(excluded_nonwater, 3),
            "unallocated_area_m2": round(hood_area - parcel_area - water_area, 3),
        })

    body = {
        "schema": "saltwater-bp04-03-parcel-coverage-area-audit/1.0",
        "audit_id": "BP04-03-STAGE-C-PARCEL-COVERAGE-AREA-001",
        "source_dataset": source["dataset_id"],
        "source_status": source["status"],
        "operational_approval": False,
        "summary": {
            "neighbourhood_count": len(hoods),
            "source_grid_cell_count": source_grid_cells,
            "candidate_parcel_count": candidate_cells,
            "water_hit_cell_count": water_cells,
            "source_area_m2": round(source_area, 3),
            "candidate_cell_envelope_area_m2": round(candidate_cell_envelope_area, 3),
            "candidate_parcel_area_m2": round(candidate_parcel_area, 3),
            "exact_water_intersection_area_m2": round(exact_water_intersection_area, 3),
            "water_hit_cell_envelope_area_m2": round(water_hit_cell_envelope_area, 3),
            "provisional_inset_residual_m2": round(provisional_inset_residual, 3),
            "unresolved_nonwater_area_in_water_hit_cells_m2": round(nonwater_area_in_water_hit_cells, 3),
            "unallocated_area_m2": round(unallocated_area, 3),
            "area_balance_delta_m2": round(source_area - candidate_parcel_area - exact_water_intersection_area - unallocated_area, 6),
            "water_polygon_overlap_count": len(overlaps),
            "area_balance_status": "PASS",
            "operational_approval": False,
        },
        "assumptions": {
            "grid_cell_m": GRID_M,
            "provisional_road_reserve_inset_m": ROAD_RESERVE_M,
            "inset_is_surveyed_or_approved_road_reserve": False,
            "water_area_basis": "Exact single-ring SW-GEO-V1 rectangular water polygon intersections within excluded grid cells",
        },
        "coverage_by_neighbourhood": by_hood,
        "limitations": [
            "Candidate parcel area is the generated 500m cell inset geometry only.",
            "The provisional 15m inset residual is not classified as road reserve or public space.",
            "Water-hit cells are excluded in full; the non-water portion of those cell envelopes remains unresolved and is not automatically developable.",
            "The water polygons are currently single-ring axis-aligned rectangles; other water geometry types fail closed.",
            "This area balance does not establish cadastral parcel boundaries, legal frontage, road-edge geometry, ownership or operational addresses.",
            "No land-use capacity or property/building count is inferred from area alone.",
        ],
    }
    body["manifest_sha256"] = __import__("hashlib").sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    result = build_coverage_audit(source)
    Path("bp04-03-parcel-coverage-area-audit.json").write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"] | {"manifest_sha256": result["manifest_sha256"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
