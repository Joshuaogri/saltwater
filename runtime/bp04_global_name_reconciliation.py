"""Cross-domain SW-UNS-001 name reconciliation for BP04.

Reads committed fictional canon datasets only. It does not write to PostgreSQL,
reserve production names, or alter domain-owned identities.
"""
from __future__ import annotations

import gzip
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime.naming import normalize_name, pg_trgm_similarity
from runtime.naming_inventory import inventory_geography_names

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(
    r"^(?:business|property|organisation|organization|person|resident|officer|"
    r"building|premises|facility|npc|entity)(?:\s*[-#:]?\s*\d+)?$",
    re.IGNORECASE,
)
PLACEHOLDER_WORDS = {"unknown", "unnamed", "placeholder", "test", "tbc", "n a", "na"}


@dataclass(frozen=True, slots=True)
class NameCandidate:
    domain: str
    entity_type: str
    entity_id: str
    name_form: str
    display_name: str
    source_ref: str

    @property
    def owner(self) -> tuple[str, str]:
        return self.entity_type, self.entity_id


def _read_json(path: str) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def _columnar_rows(document: dict[str, Any], collection: str) -> list[dict[str, Any]]:
    table = document.get("tables", {}).get(collection)
    if table is None:
        return []
    columns, values = table.get("columns"), table.get("rows")
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"malformed columnar collection: {collection}")
    result = []
    for index, row in enumerate(values):
        if len(row) != len(columns):
            raise ValueError(f"{collection}[{index}] column count mismatch")
        result.append(dict(zip(columns, row)))
    return result


def _add(
    result: list[NameCandidate], domain: str, entity_type: str,
    entity_id: Any, name: Any, form: str, source: str,
) -> None:
    stable_id = str(entity_id or "").strip()
    display = str(name or "").strip()
    if not stable_id:
        raise ValueError(f"{source}: named entity has no stable ID")
    if not display:
        return  # unnamed physical records are not invented into named entities
    result.append(NameCandidate(domain, entity_type, stable_id, form, display, source))


def build_global_name_inventory() -> dict[str, Any]:
    candidates: list[NameCandidate] = []

    geography = _read_json("data/geography/saltwater-geography-v1.json")
    geo = inventory_geography_names(geography)
    for item in geo.candidates:
        _add(candidates, "geography", "GEOGRAPHY", item.source_id,
             item.display_name, "canonical", item.source_ref)

    business_doc = _read_json("data/business/saltwater-business-registry-v1.json.gz")
    businesses = _columnar_rows(business_doc, "businesses")
    for row in businesses:
        business_id = row.get("business_id")
        _add(candidates, "business", "BUSINESS", business_id,
             row.get("trading_name"), "trading", "SW-BUSINESS-REGISTRY-V1:businesses")
        _add(candidates, "business", "BUSINESS", business_id,
             row.get("registered_name"), "legal", "SW-BUSINESS-REGISTRY-V1:businesses")

    world_doc = _read_json("data/property/saltwater-property-world-v1.json.gz")
    property_name_fields = {
        "properties": ("display_name", "property_name", "name"),
        "buildings": ("display_name", "building_name", "name"),
        "premises": ("display_name", "premises_name", "name"),
    }
    property_id_fields = {
        "properties": "property_id",
        "buildings": "building_id",
        "premises": "premises_id",
    }
    for collection, name_fields in property_name_fields.items():
        for row in _columnar_rows(world_doc, collection):
            name = next((row.get(field) for field in name_fields if row.get(field)), None)
            _add(candidates, "property", collection.upper(), row.get(property_id_fields[collection]),
                 name, "canonical", f"SW-PROPERTY-WORLD-V1:{collection}")

    tenure_doc = _read_json("data/property/saltwater-property-tenure-v1.json.gz")
    for row in _columnar_rows(tenure_doc, "organisations"):
        _add(candidates, "organisation", "ORGANISATION", row.get("organisation_id"),
             row.get("display_name"), "canonical", "SW-PROPERTY-TENURE-V1:organisations")

    civilian = _read_json("data/people/saltwater-opening-civilian-resident-seed-v1.json")
    police = _read_json("data/people/saltwater-opening-police-person-seed-v1.json")
    for dataset, payload, domain in (
        ("SW-OPENING-CIVILIAN-RESIDENT-SEED-V1", civilian, "npc_candidate"),
        ("SW-OPENING-POLICE-PERSON-SEED-V1", police, "npc_candidate"),
    ):
        records = payload.get("records")
        if not isinstance(records, list):
            raise ValueError(f"{dataset}: records array is required")
        for row in records:
            _add(candidates, domain, "PERSON_CANDIDATE", row.get("candidate_ref"),
                 row.get("display_name"), "candidate", dataset)

    # A repeated stable ID must never acquire conflicting canonical spellings.
    names_by_owner: dict[tuple[str, str], set[str]] = defaultdict(set)
    for item in candidates:
        names_by_owner[item.owner].add(normalize_name(item.display_name))
    owner_conflicts = {
        owner: sorted(names) for owner, names in names_by_owner.items() if len(names) > 1
        and owner[0] not in {"BUSINESS"}
    }

    by_key: dict[str, list[NameCandidate]] = defaultdict(list)
    placeholders: list[NameCandidate] = []
    for item in candidates:
        key = normalize_name(item.display_name)
        if key.isdigit() or key in PLACEHOLDER_WORDS or PLACEHOLDER.fullmatch(key):
            placeholders.append(item)
        by_key[key].append(item)

    exact_conflicts = []
    for key, group in sorted(by_key.items()):
        owners = {item.owner for item in group}
        saltwater_pair = key == "saltwater" and owners == {
            ("GEOGRAPHY", "saltwater-state"),
            ("GEOGRAPHY", "saltwater-city"),
        }
        if len(owners) > 1 and not saltwater_pair:
            exact_conflicts.append({
                "normalized_key": key,
                "entities": [
                    {
                        "domain": item.domain, "entity_type": item.entity_type,
                        "entity_id": item.entity_id, "name_form": item.name_form,
                        "display_name": item.display_name, "source_ref": item.source_ref,
                    }
                    for item in sorted(group, key=lambda x: (x.domain, x.entity_type, x.entity_id, x.name_form))
                ],
            })

    # Existing per-domain suites screen within-domain near duplicates. This pass
    # focuses on cross-domain near duplicates while excluding multiple names
    # belonging to the same stable entity.
    signatures: list[tuple[frozenset[str], NameCandidate]] = []
    postings: dict[str, dict[int, dict[str, list[int]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    near_pairs: list[dict[str, Any]] = []
    for key, group in sorted(by_key.items()):
        for item in group:
            words = key.split()
            trigrams = frozenset(
                f"  {word} "[offset:offset + 3]
                for word in words
                for offset in range(max(0, len(f"  {word} ") - 2))
            )
            # For a >=0.90 Jaccard match, at most floor(10% of the
            # candidate trigrams) can be absent. Probe one more than that
            # number of the rarest trigrams: every qualifying match must share
            # at least one probe. This is an exact candidate filter, not a
            # heuristic that can hide a qualifying near duplicate.
            minimum_size = math.ceil(len(trigrams) * 0.90)
            maximum_size = math.floor(len(trigrams) / 0.90)
            anchor_count = max(1, math.floor(len(trigrams) * 0.10) + 1)
            for prior_domain, domain_index in postings.items():
                if prior_domain == item.domain:
                    continue
                prior_sizes = range(minimum_size, maximum_size + 1)
                frequencies = []
                for trigram in trigrams:
                    frequency = sum(
                        len(domain_index.get(prior_size, {}).get(trigram, ()))
                        for prior_size in prior_sizes
                    )
                    frequencies.append((frequency, trigram))
                anchors = [trigram for _, trigram in sorted(frequencies)[:anchor_count]]
                candidate_indices: set[int] = set()
                for trigram in anchors:
                    for prior_size in prior_sizes:
                        candidate_indices.update(
                            domain_index.get(prior_size, {}).get(trigram, ())
                        )
                for prior_index in candidate_indices:
                    prior_trigrams, prior = signatures[prior_index]
                    if item.owner == prior.owner or key == normalize_name(prior.display_name):
                        continue
                    common = len(trigrams & prior_trigrams)
                    required = math.ceil(
                        0.90 * (len(trigrams) + len(prior_trigrams)) / 1.90
                    )
                    if common >= required and pg_trgm_similarity(
                        item.display_name, prior.display_name
                    ) >= 0.90:
                        near_pairs.append({
                            "left": {"domain": prior.domain, "entity_id": prior.entity_id,
                                     "name": prior.display_name, "source": prior.source_ref},
                            "right": {"domain": item.domain, "entity_id": item.entity_id,
                                      "name": item.display_name, "source": item.source_ref},
                        })
            signature_index = len(signatures)
            signatures.append((trigrams, item))
            for trigram in trigrams:
                postings[item.domain][len(trigrams)][trigram].append(signature_index)

    domain_counts: dict[str, int] = defaultdict(int)
    for item in candidates:
        domain_counts[item.domain] += 1

    return {
        "schema": "saltwater-global-name-inventory/1.0",
        "normalizer_version": 1,
        "candidate_count": len(candidates),
        "domain_counts": dict(sorted(domain_counts.items())),
        "unique_normalized_names": len(by_key),
        "exact_conflicts": exact_conflicts,
        "cross_domain_near_duplicate_count": len(near_pairs),
        "cross_domain_near_duplicates": near_pairs,
        "placeholder_count": len(placeholders),
        "placeholders": [
            {"domain": x.domain, "entity_id": x.entity_id,
             "name": x.display_name, "source": x.source_ref}
            for x in placeholders
        ],
        "owner_name_conflicts": [
            {"entity_type": owner[0], "entity_id": owner[1], "normalized_names": names}
            for owner, names in sorted(owner_conflicts.items())
        ],
        "geography_name_count": len(geo.candidates),
        "business_entity_count": len(businesses),
        "business_public_name_count": sum(
            1 for item in candidates if item.domain == "business"
        ),
        "person_candidate_count": sum(
            1 for item in candidates if item.domain == "npc_candidate"
        ),
        "pass": not exact_conflicts and not near_pairs and not placeholders and not owner_conflicts,
    }


if __name__ == "__main__":
    report = build_global_name_inventory()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["pass"]:
        raise SystemExit(1)
