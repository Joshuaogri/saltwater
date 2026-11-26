"""Build the unreserved 500-person opening police identity candidate seed.

Names are proposals until the SW-UNS PostgreSQL registry accepts them. This
module creates no BP03 person rows and makes no personnel-category decisions.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.naming import (
    GeneratorConfig,
    generate_candidates,
    normalize_name,
    pg_trgm_similarity,
)

ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "data/naming/saltwater-person-naming-v1.json"
OUTPUT_PATH = ROOT / "data/people/saltwater-opening-police-person-seed-v1.json"
COMPRESSED_PATH = OUTPUT_PATH.with_suffix(OUTPUT_PATH.suffix + ".gz")
SEED = 20261126
TARGET_COUNT = 500
GENERATOR_VERSION = 1
NORMALIZER_VERSION = 1
CONFIG_VERSION = "saltwater-opening-police-person-seed-v1"
SOURCE_REF = "SW-OPENING-POLICE-PERSON-SEED-V1"


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


def build_opening_police_person_seed() -> dict[str, Any]:
    config = _load_config()
    # A generous deterministic pool allows quality screening without predictable
    # sequence suffixes or fallback placeholder names.
    candidates = generate_candidates(
        "person", TARGET_COUNT * 20, seed=SEED, config=config
    )
    accepted: list[dict[str, str]] = []
    exact_keys: set[str] = set()
    accepted_names: list[str] = []

    for full_name in candidates:
        parts = full_name.split()
        if len(parts) != 3:
            continue
        key = normalize_name(full_name)
        if key in exact_keys:
            continue
        if any(pg_trgm_similarity(full_name, prior) > 0.90 for prior in accepted_names):
            continue
        given, middle, family = parts
        candidate_ref = f"SWPSEED-{len(accepted) + 1:06d}"
        accepted.append({
            "candidate_ref": candidate_ref,
            "source_ref": f"{SOURCE_REF}:{candidate_ref}",
            "given_name": given,
            "middle_name": middle,
            "family_name": family,
            "display_name": full_name,
            "identity_status": "UNMATERIALISED_CANDIDATE",
            "name_reservation_status": "PENDING_AUTHORITATIVE_REGISTRY_CHECK",
            "personnel_category": None,
            "person_id": None,
        })
        exact_keys.add(key)
        accepted_names.append(full_name)
        if len(accepted) == TARGET_COUNT:
            break

    if len(accepted) != TARGET_COUNT:
        raise ValueError(
            f"person vocabulary yielded only {len(accepted)} candidates after "
            "exact and PostgreSQL-compatible near-duplicate screening"
        )

    candidate_payload = {
        "schema": "saltwater-opening-person-seed/1.0",
        "dataset_id": "SW-OPENING-POLICE-PERSON-SEED-V1",
        "generator_version": GENERATOR_VERSION,
        "normalizer_version": NORMALIZER_VERSION,
        "config_version": CONFIG_VERSION,
        "seed": SEED,
        "target_count": TARGET_COUNT,
        "candidate_count": len(accepted),
        "intended_cohort": "opening_police_personnel",
        "cohort_basis": "BP-03 and SW-CANON-001 exact opening target of 500 active police-service people",
        "category_allocation_status": "NOT_ASSIGNED_PENDING_BP05_BP06_STAFFING_ALLOCATION",
        "identity_materialisation_status": "CANDIDATES_ONLY_NO_BP03_PERSON_ROWS_CREATED",
        "name_reservation_status": "PENDING_SW_UNS_001_AUTHORITATIVE_DATABASE_RESERVATION",
        "demographic_policy": "No date of birth, age, sex, gender, ethnicity, nationality, citizenship, address, residence or personal history is inferred by this seed.",
        "production_import_authorized": False,
        "records": accepted,
    }
    canonical = json.dumps(
        candidate_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    candidate_payload["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return candidate_payload


def write_opening_police_person_seed() -> dict[str, Any]:
    payload = build_opening_police_person_seed()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT_PATH.write_text(text, encoding="utf-8")
    with COMPRESSED_PATH.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, compresslevel=9) as stream:
            stream.write(text.encode("utf-8"))
    return {
        "dataset_id": payload["dataset_id"],
        "candidate_count": payload["candidate_count"],
        "manifest_sha256": payload["manifest_sha256"],
        "json_bytes": OUTPUT_PATH.stat().st_size,
        "gzip_bytes": COMPRESSED_PATH.stat().st_size,
        "name_reservation_status": payload["name_reservation_status"],
        "identity_materialisation_status": payload["identity_materialisation_status"],
        "production_import_authorized": payload["production_import_authorized"],
    }


if __name__ == "__main__":
    print(json.dumps(write_opening_police_person_seed(), indent=2))
