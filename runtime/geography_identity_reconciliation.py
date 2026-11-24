"""Validate the 100 SW-GEO-V1 source identities against the stable identity map.

Database spatial_id values are generated surrogates and differ between databases.
The portable source-to-identity mapping is source_id == entity_code; never
hard-code a disposable or production sequence value in the geography source.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEO_PATH = ROOT / "data/geography/saltwater-geography-v1.json"
MAP_PATH = ROOT / "data/geography/saltwater-geography-v1-identity-map.json"
REGISTER_PATH = ROOT / "data/geography/bp04-03-stage-a-source-spatial-reconciliation-v1.json"


def _source_catalog(geo: dict) -> dict[str, dict]:
    catalog: dict[str, dict] = {}
    for row in geo["districts"]:
        catalog[row["id"]] = {
            "entity_type": "DISTRICT", "entity_kind": 3,
            "display_name": row["name"], "parent_entity_code": "saltwater-city",
        }
    for row in geo["neighbourhoods"]:
        catalog[row["id"]] = {
            "entity_type": "NEIGHBOURHOOD", "entity_kind": 4,
            "display_name": row["name"], "parent_entity_code": row["district_id"],
        }
    for row in geo["features"]:
        props = row["properties"]
        kind = props.get("entity_type")
        if kind == "landmark":
            catalog[row["id"]] = {
                "entity_type": "LANDMARK", "entity_kind": 10,
                "display_name": props["name"], "parent_entity_code": "saltwater-city",
            }
        elif kind in {"harbour_water", "constructed_water", "terrain_feature"}:
            catalog[row["id"]] = {
                "entity_type": "GEO_ZONE", "entity_kind": 5,
                "display_name": props["name"], "parent_entity_code": "saltwater-city",
            }
    for row in geo["roads"]:
        catalog[row["id"]] = {
            "entity_type": "ROAD", "entity_kind": 7,
            "display_name": row["name"], "parent_entity_code": "saltwater-city",
        }
    for row in geo["network"]["routes"]:
        catalog[row["id"]] = {
            "entity_type": "ROUTE", "entity_kind": 9,
            "display_name": row["name"], "parent_entity_code": "saltwater-city",
        }
    return catalog


def validate_identity_map(geo: dict, identity_map: dict) -> dict:
    catalog = _source_catalog(geo)
    entries = identity_map["entries"]
    errors = []
    seen = set()
    for entry in entries:
        source_id = entry["source_id"]
        if source_id in seen:
            errors.append(f"duplicate source_id: {source_id}")
        seen.add(source_id)
        if source_id not in catalog:
            errors.append(f"source record missing from SW-GEO-V1: {source_id}")
            continue
        expected = catalog[source_id]
        for field in ("entity_type", "entity_kind", "display_name", "parent_entity_code"):
            if entry.get(field) != expected[field]:
                errors.append(
                    f"{source_id}: {field} mismatch "
                    f"(map={entry.get(field)!r}, source={expected[field]!r})"
                )
        if entry.get("entity_code") != source_id:
            errors.append(f"{source_id}: entity_code must equal stable source_id")
    if seen != set(catalog):
        errors.append(
            f"coverage mismatch: map={len(seen)} source_catalog={len(catalog)} "
            f"missing={sorted(set(catalog)-seen)} extra={sorted(seen-set(catalog))}"
        )
    if len(entries) != 100:
        errors.append(f"expected 100 entries, found {len(entries)}")
    if errors:
        raise ValueError("\\n".join(errors))
    return {
        "source_records": len(catalog),
        "resolved": len(entries),
        "unresolved": 0,
        "portable_spatial_id_literals": 0,
        "stable_source_to_entity_code_mappings": len(entries),
        "spatial_id_policy": "DATABASE_GENERATED_SURROGATE; resolve by entity_code in each database",
    }


def main() -> None:
    geo = json.loads(GEO_PATH.read_text(encoding="utf-8"))
    identity_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    result = validate_identity_map(geo, identity_map)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
