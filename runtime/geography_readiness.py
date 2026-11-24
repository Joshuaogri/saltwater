"""Read-only SW-GEO-V1 readiness audit; never approves or imports operational geography."""
from __future__ import annotations
import json
from pathlib import Path\nfrom runtime.geography_identity_reconciliation import validate_identity_map

EXPECTED = {"districts": 8, "neighbourhoods": 24, "roads": 42, "nodes": 367, "segments": 685, "routes": 5}


def _unique(items, key):
    values = [item.get(key) for item in items]
    return all(values) and len(values) == len(set(values))


def _closed_ring(poly):
    try:
        ring = poly["coordinates"][0]
        return len(ring) >= 4 and ring[0] == ring[-1]
    except (KeyError, IndexError, TypeError):
        return False


def audit_geography(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    districts, hoods = data.get("districts", []), data.get("neighbourhoods", [])
    roads = data.get("roads", [])
    network = data.get("network", {})
    nodes, segments, routes = (network.get(k, []) for k in ("nodes", "segments", "routes"))
    register_path = Path(path).with_name("bp04-03-stage-a-source-spatial-reconciliation-v1.json")
    register = json.loads(register_path.read_text(encoding="utf-8")) if register_path.exists() else {}
    mapping_records = register.get("records", [])
    unresolved_count = sum(1 for row in mapping_records if row.get("mapping_status") == "UNRESOLVED" and row.get("spatial_id") is None)
    node_ids = {n.get("id") for n in nodes}
    segment_ids = {s.get("id") for s in segments}
    district_ids = {d.get("id") for d in districts}
    checks = {
        "canonical_dataset_id": data.get("dataset_id") == "SW-GEO-V1",
        "not_operationally_approved": data.get("status") == "DESIGN_BASELINE_NOT_YET_USER_APPROVED_FOR_OPERATIONAL_SEED",
        "district_count": len(districts) == EXPECTED["districts"],
        "neighbourhood_count": len(hoods) == EXPECTED["neighbourhoods"],
        "road_count": len(roads) == EXPECTED["roads"],
        "node_count": len(nodes) == EXPECTED["nodes"],
        "segment_count": len(segments) == EXPECTED["segments"],
        "route_count": len(routes) == EXPECTED["routes"],
        "district_ids_unique": _unique(districts, "id"),
        "district_names_unique": _unique(districts, "name"),
        "neighbourhood_ids_unique": _unique(hoods, "id"),
        "neighbourhood_names_unique": _unique(hoods, "name"),
        "road_ids_unique": _unique(roads, "id"),
        "road_names_unique": _unique(roads, "name"),
        "node_ids_unique": _unique(nodes, "id"),
        "segment_ids_unique": _unique(segments, "id"),
        "route_ids_unique": _unique(routes, "id"),
        "neighbourhood_parent_integrity": all(h.get("district_id") in district_ids for h in hoods),
        "neighbourhood_rings_closed": all(_closed_ring(h.get("geometry", {})) for h in hoods),
        "segment_endpoints_resolve": all(s.get("from_node_id") in node_ids and s.get("to_node_id") in node_ids for s in segments),
        "segment_roads_resolve": all(s.get("road_id") in {r.get("id") for r in roads} for s in segments),
        "road_segment_membership_resolves": all(set(r.get("segment_ids", [])).issubset(segment_ids) for r in roads),
        "route_nodes_resolve": all(set(r.get("node_ids", [])).issubset(node_ids) for r in routes),
        "route_segments_resolve": all(set(r.get("segment_ids", [])).issubset(segment_ids) for r in routes),
        "single_connected_component_claim": network.get("connected_components") == 1 or data.get("validation", {}).get("connected_components") == 1,
        "reconciliation_register_present": register.get("register_id") == "BP04-03-STAGE-A-RECON-001",
        "reconciliation_register_has_100_source_records": len(mapping_records) == 100,
        "all_100_source_identities_resolved": identity_result["resolved"] == 100 and unresolved_count == 0 and register.get("summary", {}).get("resolved") == 100,
    }
    blockers = [
        "Database spatial_id surrogates are generated per database and must be looked up by stable entity_code; they are not portable source identifiers.",
        "Parcel fabric and canonical numbered addresses do not exist in SW-GEO-V1.",
        "Building footprints and entrances do not exist in SW-GEO-V1.",
        "SW-GEO-V1 is planning-grade and has not been approved for operational seeding.",
        "Graph structural checks do not constitute full geometry QA or operational routing acceptance.",
    ]
    return {
        "audit": "BP04-03-STAGE-A-READINESS",
        "dataset_id": data.get("dataset_id"),
        "source_status": data.get("status"),
        "counts": {"districts": len(districts), "neighbourhoods": len(hoods), "roads": len(roads), "nodes": len(nodes), "segments": len(segments), "routes": len(routes)},
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "unresolved_source_to_spatial_id_mappings": unresolved_count,
        "resolved_source_to_entity_code_mappings": identity_result["resolved"],
        "database_spatial_id_policy": "Generated per database; resolve by entity_code at materialisation.",\n        "resolved_source_to_entity_code_mappings": identity_result["resolved"],\n        "database_spatial_id_policy": "Generated per database; resolve by entity_code at materialisation.",
        "blockers": blockers,
        "operational_seed_eligible": False,
        "geometry_import_performed": False,
        "database_write_performed": False,
        "approval_note": "This audit is read-only. A passing structural audit cannot approve BP-02 geography or authorise production seeding.",
    }


def main():
    root = Path(__file__).resolve().parents[1]
    source = root / "data/geography/saltwater-geography-v1.json"
    print(json.dumps(audit_geography(source), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
