"""Area reconciliation for geometry-derived BP04-03 parcel candidates."""
from __future__ import annotations
import json
from pathlib import Path
from runtime.parcel_candidate_generator import build_candidates


def build_coverage_audit(source: dict) -> dict:
    candidates = build_candidates(source)
    generation = candidates["generation"]
    body = {
        "schema": "saltwater-bp04-03-parcel-coverage-area-audit/2.0",
        "audit_id": "BP04-03-STAGE-C-PARCEL-COVERAGE-AREA-002",
        "source_dataset": source["dataset_id"],
        "operational_approval": False,
        "summary": {
            "neighbourhood_count": len(candidates["coverage_by_neighbourhood"]),
            "source_grid_cell_count": generation["source_grid_cell_count"],
            "candidate_parcel_count": generation["parcel_candidate_count"],
            "water_intersection_cell_count": generation["water_intersection_cell_count"],
            "source_area_m2": generation["source_area_m2"],
            "dissolved_road_reserve_area_m2": generation["road_reserve_area_m2"],
            "water_area_outside_road_reserve_m2": generation["water_area_outside_road_reserve_m2"],
            "candidate_land_area_m2": generation["candidate_land_area_m2"],
            "area_balance_delta_m2": generation["area_balance_delta_m2"],
            "area_balance_status": "PASS" if generation["area_balance_delta_m2"] == 0 else "FAIL",
            "provisional_15m_inset_used": False,
            "whole_water_hit_cells_excluded": False,
        },
        "coverage_by_neighbourhood": candidates["coverage_by_neighbourhood"],
        "limitations": [
            "This is fictional game-world candidate geometry, not a real cadastral plan.",
            "The dissolved road-reserve geometry uses SW-RDS-V1 design widths.",
            "Water is removed by its actual mapped polygon intersection, not by excluding an entire grid cell.",
            "500m grid cells provide lineage only; they do not define final cadastral boundaries.",
            "No ownership, occupancy, canonical address or built-asset count is inferred.",
        ],
        "candidate_manifest_sha256": candidates["manifest_sha256"],
    }
    import hashlib
    body["manifest_sha256"] = hashlib.sha256(
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
