"""Build a deterministic, non-operative BP03 resident-to-dwelling candidate map.

The output joins fictional resident name candidates to unique active BP04 dwelling
units and derives the portable BP02 parcel/address source IDs. It creates no
canonical people, residence links, households, occupancy records or DB writes.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESIDENT_PATH = ROOT / "data/people/saltwater-opening-civilian-resident-seed-v1.json.gz"
PROPERTY_PATH = ROOT / "data/property/saltwater-property-world-v1.json.gz"
OUTPUT_PATH = ROOT / "data/people/saltwater-opening-resident-dwelling-allocation-v1.json.gz"
SUMMARY_PATH = ROOT / "data/people/saltwater-opening-resident-dwelling-allocation-v1-summary.json"
TARGET_COUNT = 9000
POPULATION_CAP = 10000
TOTAL_OPENING_COUNT = 9500


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _stable_id(prefix: str, source_id: str) -> str:
    return f"{prefix}-{_sha256(source_id.encode('utf-8'))[:16].upper()}"


def _columnar_rows(document: dict, table_name: str) -> list[dict]:
    table = document.get("tables", {}).get(table_name)
    if not isinstance(table, dict):
        raise ValueError(f"property world is missing {table_name!r}")
    columns, values = table.get("columns"), table.get("rows")
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"property world table {table_name!r} is malformed")
    rows = []
    for index, row in enumerate(values):
        if len(row) != len(columns):
            raise ValueError(f"{table_name}[{index}] has an invalid column count")
        rows.append(dict(zip(columns, row)))
    return rows


def _load_sources() -> tuple[dict, bytes, dict, bytes]:
    resident_raw = RESIDENT_PATH.read_bytes()
    resident = json.loads(gzip.decompress(resident_raw))
    digest = resident.pop("manifest_sha256", None)
    if not digest or digest != _sha256(_canonical_json(resident)):
        raise ValueError("civilian candidate manifest checksum is invalid")
    resident["manifest_sha256"] = digest
    if resident.get("dataset_id") != "SW-OPENING-CIVILIAN-RESIDENT-SEED-V1":
        raise ValueError("unexpected civilian candidate dataset")
    if resident.get("candidate_count") != TARGET_COUNT or len(resident.get("records", [])) != TARGET_COUNT:
        raise ValueError("exactly 9,000 civilian candidates are required")
    if resident.get("production_import_authorized") is not False:
        raise ValueError("civilian candidate dataset must remain non-production-authorised")

    property_raw = PROPERTY_PATH.read_bytes()
    property_document = json.loads(gzip.decompress(property_raw))
    if property_document.get("storage_format") != "textual_json_columnar_v1":
        raise ValueError("unsupported BP04 property-world storage format")
    if property_document.get("metadata", {}).get("dataset_id") != "SW-PROPERTY-WORLD-V1":
        raise ValueError("unexpected BP04 property-world dataset")
    return resident, resident_raw, property_document, property_raw


def _allocation_quotas(units_by_neighbourhood: dict[str, list[dict]], total: int) -> dict[str, int]:
    eligible_total = sum(len(rows) for rows in units_by_neighbourhood.values())
    if eligible_total < total:
        raise ValueError(f"only {eligible_total} eligible dwellings exist for {total} candidates")
    quotas = {}
    remainders = []
    assigned = 0
    for neighbourhood_id, rows in units_by_neighbourhood.items():
        numerator = total * len(rows)
        quota, remainder = divmod(numerator, eligible_total)
        quotas[neighbourhood_id] = quota
        assigned += quota
        remainders.append((remainder, neighbourhood_id))
    for _, neighbourhood_id in sorted(remainders, key=lambda item: (-item[0], item[1]))[:total - assigned]:
        quotas[neighbourhood_id] += 1
    if sum(quotas.values()) != total:
        raise AssertionError("neighbourhood dwelling quotas do not reconcile")
    return quotas


def build_opening_resident_dwelling_allocation() -> dict[str, Any]:
    resident, resident_raw, property_document, property_raw = _load_sources()
    properties = {row["property_id"]: row for row in _columnar_rows(property_document, "properties")}
    addresses = {row["address_id"]: row for row in _columnar_rows(property_document, "addresses")}
    buildings = {row["building_id"]: row for row in _columnar_rows(property_document, "buildings")}
    premises = {row["premises_id"]: row for row in _columnar_rows(property_document, "premises")}
    units = _columnar_rows(property_document, "units")

    units_by_neighbourhood: dict[str, list[dict]] = defaultdict(list)
    for unit in units:
        if unit.get("unit_class") != "dwelling" or unit.get("canonical_status") != "active":
            continue
        prop = properties.get(unit.get("property_id"))
        building = buildings.get(unit.get("building_id"))
        premise = premises.get(unit.get("premises_id"))
        if not prop or prop.get("primary_use") not in {"dwelling", "mixed_use"}:
            continue
        if prop.get("canonical_status") != "active":
            continue
        if not building or building.get("canonical_status") != "active":
            continue
        if not premise or premise.get("canonical_status") != "active":
            continue
        address = addresses.get(prop.get("address_id"))
        if not address or address.get("property_id") != prop.get("property_id"):
            raise ValueError(f"{unit['unit_id']}: active dwelling has no matching BP04 site address")
        candidate_parcel_id = prop.get("source_candidate_parcel_id")
        expected_address_ref = f"SW-GEO-V1:{candidate_parcel_id}"
        if not candidate_parcel_id or address.get("source_ref") != expected_address_ref:
            raise ValueError(f"{unit['unit_id']}: BP04 address parcel provenance does not match its property")
        neighbourhood_id = prop.get("neighbourhood_id")
        district_id = prop.get("district_id")
        if not neighbourhood_id or not district_id:
            raise ValueError(f"{unit['unit_id']}: property lacks administrative geography")
        units_by_neighbourhood[str(neighbourhood_id)].append({
            "unit": unit, "property": prop, "address": address,
            "building": building, "premises": premise,
            "candidate_parcel_id": candidate_parcel_id,
            "district_id": str(district_id),
            "neighbourhood_id": str(neighbourhood_id),
        })

    if not units_by_neighbourhood:
        raise ValueError("no active household-eligible dwelling units were found")
    for neighbourhood_id, rows in units_by_neighbourhood.items():
        districts = {row["district_id"] for row in rows}
        if len(districts) != 1:
            raise ValueError(f"{neighbourhood_id}: dwelling inventory crosses district boundaries")
        rows.sort(key=lambda row: (
            str(row["property"]["property_id"]),
            str(row["building"]["building_id"]),
            int(row["unit"].get("floor_order") or 0),
            str(row["unit"]["unit_id"]),
        ))

    eligible_total = sum(len(rows) for rows in units_by_neighbourhood.values())
    expected_inventory = property_document.get("metadata", {}).get("summary", {}).get(
        "household_eligible_dwelling_unit_count"
    )
    if expected_inventory is not None and expected_inventory != eligible_total:
        raise ValueError(
            f"eligible dwelling count {eligible_total} does not match property manifest {expected_inventory}"
        )
    quotas = _allocation_quotas(units_by_neighbourhood, TARGET_COUNT)
    candidate_records = resident["records"]
    allocations = []
    candidate_index = 0
    neighbourhood_summary = []
    for neighbourhood_id in sorted(units_by_neighbourhood):
        rows = units_by_neighbourhood[neighbourhood_id]
        quota = quotas[neighbourhood_id]
        district_id = rows[0]["district_id"]
        neighbourhood_summary.append({
            "district_id": district_id,
            "neighbourhood_id": neighbourhood_id,
            "eligible_dwelling_count": len(rows),
            "candidate_allocation_count": quota,
            "unallocated_eligible_dwelling_count": len(rows) - quota,
        })
        for selected in rows[:quota]:
            candidate = candidate_records[candidate_index]
            candidate_index += 1
            unit = selected["unit"]
            prop = selected["property"]
            address = selected["address"]
            bp04_address_id = str(address["address_id"])
            candidate_parcel_id = selected["candidate_parcel_id"]
            allocations.append({
                "allocation_ref": f"SW-DWELLING-ALLOC-{candidate_index:06d}",
                "candidate_ref": candidate["candidate_ref"],
                "person_source_ref": candidate["source_ref"],
                "display_name": candidate["display_name"],
                "district_id": district_id,
                "neighbourhood_id": neighbourhood_id,
                "property_id": str(prop["property_id"]),
                "building_id": str(unit["building_id"]),
                "premises_id": str(unit["premises_id"]),
                "unit_id": str(unit["unit_id"]),
                "bp04_address_id": bp04_address_id,
                "bp04_address_source_ref": str(address["source_ref"]),
                "source_candidate_parcel_id": str(candidate_parcel_id),
                "bp02_parcel_source_id": _stable_id("SWP", str(candidate_parcel_id)),
                "bp02_address_source_id": _stable_id("SWA", bp04_address_id),
                "allocation_status": "CANDIDATE_DWELLING_MATCH_ONLY",
                "person_id": None,
                "residence_record_created": False,
                "household_record_created": False,
            })
    if candidate_index != TARGET_COUNT:
        raise AssertionError(f"allocated {candidate_index} candidates; expected {TARGET_COUNT}")
    if len({row["unit_id"] for row in allocations}) != TARGET_COUNT:
        raise ValueError("candidate allocation reuses a dwelling unit")
    if len({row["candidate_ref"] for row in allocations}) != TARGET_COUNT:
        raise ValueError("candidate allocation reuses a person candidate")
    if len({row["bp04_address_id"] for row in allocations}) != TARGET_COUNT:
        raise ValueError("candidate allocation assigns multiple people to one site address; one candidate per site is required for this initial plan")

    payload = {
        "schema": "saltwater-opening-resident-dwelling-allocation/1.0",
        "dataset_id": "SW-OPENING-RESIDENT-DWELLING-ALLOCATION-V1",
        "allocation_version": 1,
        "allocation_method": "largest-remainder proportional allocation by active eligible dwelling inventory per neighbourhood; stable lexical tie-break; stable unit ordering",
        "allocation_policy": "one candidate per distinct active dwelling unit and one candidate per BP04 site address in this planning pass; no household composition, occupancy capacity, demographics or actual residence is inferred",
        "candidate_count": TARGET_COUNT,
        "eligible_dwelling_count": eligible_total,
        "allocated_candidate_count": len(allocations),
        "unallocated_eligible_dwelling_count": eligible_total - len(allocations),
        "neighbourhood_count": len(neighbourhood_summary),
        "neighbourhood_allocation": neighbourhood_summary,
        "source_datasets": {
            "resident_candidates": {
                "dataset_id": resident["dataset_id"],
                "manifest_sha256": resident["manifest_sha256"],
                "compressed_sha256": _sha256(resident_raw),
            },
            "property_world": {
                "dataset_id": "SW-PROPERTY-WORLD-V1",
                "compressed_sha256": _sha256(property_raw),
            },
            "bp02_identity_rule": "SWP- + first 16 uppercase SHA-256 hex characters of source_candidate_parcel_id; SWA- + first 16 uppercase SHA-256 hex characters of BP04 address_id",
        },
        "population_reconciliation": {
            "civilian_usual_residents_target": TARGET_COUNT,
            "active_police_service_people_target": 500,
            "distinct_opening_people_target": TOTAL_OPENING_COUNT,
            "hard_population_cap": POPULATION_CAP,
            "unused_opening_headroom": POPULATION_CAP - TOTAL_OPENING_COUNT,
        },
        "materialisation_status": "CANDIDATE_DWELLING_MATCHES_ONLY_NO_CANONICAL_PERSON_RESIDENCE_OR_HOUSEHOLD_ROWS",
        "occupancy_capacity_status": "NOT_ASSESSED",
        "production_seed_authorized": False,
        "person_records_created": 0,
        "residence_records_created": 0,
        "household_records_created": 0,
        "records": allocations,
    }
    payload["manifest_sha256"] = _sha256(_canonical_json(payload))
    return payload


def write_opening_resident_dwelling_allocation() -> dict[str, Any]:
    payload = build_opening_resident_dwelling_allocation()
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("wb") as destination:
        with gzip.GzipFile(fileobj=destination, mode="wb", filename="", mtime=0, compresslevel=9) as stream:
            stream.write(raw)
    summary = {
        "dataset_id": payload["dataset_id"],
        "manifest_sha256": payload["manifest_sha256"],
        "candidate_count": payload["candidate_count"],
        "eligible_dwelling_count": payload["eligible_dwelling_count"],
        "allocated_candidate_count": payload["allocated_candidate_count"],
        "unallocated_eligible_dwelling_count": payload["unallocated_eligible_dwelling_count"],
        "neighbourhood_count": payload["neighbourhood_count"],
        "materialisation_status": payload["materialisation_status"],
        "occupancy_capacity_status": payload["occupancy_capacity_status"],
        "production_seed_authorized": payload["production_seed_authorized"],
        "compressed_bytes": OUTPUT_PATH.stat().st_size,
        "source_datasets": payload["source_datasets"],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    write_opening_resident_dwelling_allocation()
