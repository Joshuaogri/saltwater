"""Build the exact 9,000-person opening civilian resident candidate cohort.

Names are candidate components only. This creates no canonical BP03 person rows,
no demographic facts, no residence assignments, and no production database writes.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from typing import Any
import math

from runtime.naming import (GeneratorConfig, generate_candidates, normalize_name, pg_trgm_similarity)

ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "data/naming/saltwater-person-naming-v1.json"
POLICE_SEED_PATH = ROOT / "data/people/saltwater-opening-police-person-seed-v1.json"
OUTPUT_PATH = ROOT / "data/people/saltwater-opening-civilian-resident-seed-v1.json"
COMPRESSED_PATH = OUTPUT_PATH.with_suffix(OUTPUT_PATH.suffix + ".gz")
SEED = 20261127
TARGET_COUNT = 9000
POLICE_COUNT = 500
TOTAL_OPENING_COUNT = 9500
POPULATION_CAP = 10000
GENERATOR_VERSION = 1
NORMALIZER_VERSION = 1
CONFIG_VERSION = "saltwater-opening-civilian-resident-seed-v1"
SOURCE_REF = "SW-OPENING-CIVILIAN-RESIDENT-SEED-V1"


def _load_config() -> GeneratorConfig:
    payload = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != "saltwater-person-naming-vocabulary/1.0":
        raise ValueError("unsupported person naming vocabulary schema")
    sections = {}
    for key in ("given_names", "middle_names", "family_names"):
        values = tuple(str(x).strip() for x in payload.get(key, []) if str(x).strip())
        if len(values) < 60 or len({normalize_name(x) for x in values}) != len(values):
            raise ValueError(f"{key} must contain at least 60 unique curated components")
        sections[key] = values
    return GeneratorConfig(
        given_names=sections["given_names"],
        middle_names=sections["middle_names"],
        family_names=sections["family_names"],
        place_roots=(),
        business_roots=(),
        config_version=str(payload.get("config_version", "")),
    )


def _police_name_keys() -> set[str]:
    payload = json.loads(POLICE_SEED_PATH.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    if payload.get("candidate_count") != POLICE_COUNT or len(records) != POLICE_COUNT:
        raise ValueError("the approved opening police candidate cohort must contain exactly 500 names")
    keys = {normalize_name(row["display_name"]) for row in records}
    if len(keys) != POLICE_COUNT:
        raise ValueError("opening police cohort contains duplicate normalized names")
    return keys


def _trigram_signature(value: str) -> frozenset[str]:
    """Match the PostgreSQL pg_trgm word-trigram set used by SW-UNS."""
    normalized = normalize_name(value)
    result: set[str] = set()
    for word in normalized.split():
        padded = f"  {word} "
        result.update(padded[index:index + 3] for index in range(len(padded) - 2))
    return frozenset(result)


def _add_to_similarity_index(
    value: str,
    signatures: list[frozenset[str]],
    postings: dict[str, list[int]],
) -> None:
    signature = _trigram_signature(value)
    index = len(signatures)
    signatures.append(signature)
    for trigram in signature:
        postings.setdefault(trigram, []).append(index)


def _has_near_duplicate(
    value: str,
    signatures: list[frozenset[str]],
    postings: dict[str, list[int]],
    indexed_names: list[str],
) -> bool:
    signature = _trigram_signature(value)
    overlap_counts: dict[int, int] = {}
    for trigram in signature:
        for index in postings.get(trigram, ()):
            overlap_counts[index] = overlap_counts.get(index, 0) + 1
    for index, common in overlap_counts.items():
        prior = signatures[index]
        # Jaccard similarity >= 0.90 requires this many shared trigrams.
        required = math.ceil(0.90 * (len(signature) + len(prior)) / 1.90)
        if common >= required and pg_trgm_similarity(value, indexed_names[index]) >= 0.90:
            return True
    return False


def build_opening_resident_person_seed() -> dict[str, Any]:
    config = _load_config()
    police_keys = _police_name_keys()
    # Use a deterministic oversupply and the exact pg_trgm threshold enforced by
    # SW-UNS. This screens the 500 police names and all earlier civilian candidates.
    candidates = generate_candidates(
        "person", TARGET_COUNT * 4, seed=SEED, config=config
    )
    accepted: list[dict[str, Any]] = []
    seen = set(police_keys)
    indexed_names: list[str] = []
    signatures: list[frozenset[str]] = []
    postings: dict[str, list[int]] = {}
    for police_name in sorted(police_keys):
        indexed_names.append(police_name)
        _add_to_similarity_index(police_name, signatures, postings)

    for full_name in candidates:
        parts = full_name.split()
        if len(parts) != 3:
            continue
        key = normalize_name(full_name)
        if key in seen or _has_near_duplicate(
            full_name, signatures, postings, indexed_names
        ):
            continue
        given, middle, family = parts
        candidate_ref = f"SWCIV-{len(accepted) + 1:06d}"
        accepted.append({
            "candidate_ref": candidate_ref,
            "source_ref": f"{SOURCE_REF}:{candidate_ref}",
            "given_name": given,
            "middle_name": middle,
            "family_name": family,
            "display_name": full_name,
            "cohort": "OPENING_CIVILIAN_USUAL_RESIDENT",
            "identity_status": "UNMATERIALISED_CANDIDATE",
            "name_reservation_status": "PENDING_AUTHORITATIVE_REGISTRY_CHECK",
            "residence_assignment_status": "NOT_ASSIGNED",
            "person_id": None,
        })
        seen.add(key)
        indexed_names.append(full_name)
        _add_to_similarity_index(full_name, signatures, postings)
        if len(accepted) == TARGET_COUNT:
            break

    if len(accepted) != TARGET_COUNT:
        raise ValueError(
            f"person vocabulary yielded only {len(accepted)} distinct civilian names "
            "after excluding the 500 police cohort"
        )

    payload = {
        "schema": "saltwater-opening-civilian-resident-seed/1.0",
        "dataset_id": "SW-OPENING-CIVILIAN-RESIDENT-SEED-V1",
        "generator_version": GENERATOR_VERSION,
        "normalizer_version": NORMALIZER_VERSION,
        "config_version": CONFIG_VERSION,
        "seed": SEED,
        "target_count": TARGET_COUNT,
        "candidate_count": len(accepted),
        "intended_cohort": "opening_civilian_usual_residents",
        "cohort_basis": "SW-CANON-001 exact opening target of 9,000 civilian usual residents, exclusive of 500 opening police-service people",
        "population_reconciliation": {
            "civilian_usual_residents": TARGET_COUNT,
            "active_police_service_people": POLICE_COUNT,
            "distinct_opening_people_target": TOTAL_OPENING_COUNT,
            "hard_population_cap": POPULATION_CAP,
            "unused_opening_headroom": POPULATION_CAP - TOTAL_OPENING_COUNT,
        },
        "police_seed_exclusion": {
            "dataset_id": "SW-OPENING-POLICE-PERSON-SEED-V1",
            "excluded_exact_names": POLICE_COUNT,
            "overlap_after_exclusion": 0,
        },
        "identity_materialisation_status": "CANDIDATES_ONLY_NO_BP03_PERSON_ROWS_CREATED",
        "name_reservation_status": "PENDING_SW_UNS_001_AUTHORITATIVE_DATABASE_RESERVATION",
        "residence_assignment_status": "NOT_ASSIGNED_TO_BP02_ADDRESS_OR_PARCEL",
        "demographic_policy": "No age, date of birth, sex, gender, ethnicity, nationality, citizenship, occupation, household, or personal history is inferred by this seed.",
        "production_import_authorized": False,
        "records": accepted,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def write_opening_resident_person_seed() -> dict[str, Any]:
    payload = build_opening_resident_person_seed()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    readable = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT_PATH.write_text(readable, encoding="utf-8")
    with COMPRESSED_PATH.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, compresslevel=9) as stream:
            stream.write(readable.encode("utf-8"))
    return {
        "dataset_id": payload["dataset_id"],
        "candidate_count": payload["candidate_count"],
        "manifest_sha256": payload["manifest_sha256"],
        "json_bytes": OUTPUT_PATH.stat().st_size,
        "gzip_bytes": COMPRESSED_PATH.stat().st_size,
        "identity_materialisation_status": payload["identity_materialisation_status"],
        "production_import_authorized": payload["production_import_authorized"],
    }


if __name__ == "__main__":
    print(json.dumps(write_opening_resident_person_seed(), indent=2))
