"""Dry-run inventory of existing geography canon for SW-NAM-001.

This module never writes to PostgreSQL. It inventories source IDs, detects
collisions, and explicitly reports names that cannot yet be bound to spatial_id.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Mapping

from runtime.naming import normalize_name


@dataclass(frozen=True, slots=True)
class CanonNameCandidate:
    entity_type: str
    source_id: str
    display_name: str
    source_ref: str


@dataclass(frozen=True, slots=True)
class CanonNameConflict:
    normalized_key: str
    candidates: tuple[CanonNameCandidate, ...]


@dataclass(frozen=True, slots=True)
class GeographyNameInventory:
    dataset_id: str
    source_status: str
    candidates: tuple[CanonNameCandidate, ...]
    conflicts: tuple[CanonNameConflict, ...]
    near_duplicate_pairs: tuple[tuple[str, str], ...]
    unresolved_spatial_ids: tuple[str, ...]
    can_import: bool


def inventory_geography_names(payload: Mapping[str, Any]) -> GeographyNameInventory:
    """Build a stable, dry-run name inventory from the SW-GEO-V1 JSON object."""
    if payload.get("schema") != "saltwater-geography/1.0":
        raise ValueError("unsupported geography dataset schema")
    dataset_id = str(payload.get("dataset_id", "")).strip()
    if not dataset_id:
        raise ValueError("geography dataset_id is required")

    candidates: list[CanonNameCandidate] = []

    def add(entity_type: str, source_id: Any, name: Any, source_ref: str) -> None:
        entity_id = str(source_id or "").strip()
        display = str(name or "").strip()
        if not entity_id or not display:
            return
        candidates.append(CanonNameCandidate(entity_type, entity_id, display, source_ref))

    # This pair is a project-level canon exception, not derived from the map's
    # descriptive boundary label. Their database IDs remain separately resolved.
    add("GEOGRAPHY", "saltwater-state", "Saltwater", "project-canon:sovereign-root")
    add("GEOGRAPHY", "saltwater-city", "Saltwater", "project-canon:playable-city")

    for row in payload.get("districts", []):
        add("GEOGRAPHY", row.get("id"), row.get("name"), f"{dataset_id}:district")
    for row in payload.get("neighbourhoods", []):
        add("GEOGRAPHY", row.get("id"), row.get("name"), f"{dataset_id}:neighbourhood")
    for row in payload.get("roads", []):
        add("GEOGRAPHY", row.get("id"), row.get("name"), f"{dataset_id}:road")
    for row in payload.get("network", {}).get("routes", []):
        add("GEOGRAPHY", row.get("id"), row.get("name"), f"{dataset_id}:route")

    # District/neighbourhood features repeat the same stable source identities;
    # skip them because their canonical records were already inventoried above.
    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        kind = props.get("entity_type")
        if kind in {"district", "neighbourhood", "city_state_boundary", "city_boundary"}:
            continue
        if kind in {"harbour_water", "constructed_water", "terrain_feature", "landmark"}:
            add("GEOGRAPHY", feature.get("id"), props.get("name"), f"{dataset_id}:{kind}")

    # A repeated source ID must have exactly one display name.
    by_id: dict[str, set[str]] = defaultdict(set)
    for item in candidates:
        by_id[item.source_id].add(item.display_name)
    invalid_ids = {source_id for source_id, names in by_id.items() if len(names) > 1}
    if invalid_ids:
        raise ValueError("one source entity ID has multiple names: " + ", ".join(sorted(invalid_ids)))

    grouped: dict[str, list[CanonNameCandidate]] = defaultdict(list)
    for item in candidates:
        grouped[normalize_name(item.display_name)].append(item)

    conflicts = []
    for key, group in grouped.items():
        if len(group) <= 1:
            continue
        owners = {(x.entity_type, x.source_id) for x in group}
        approved_root_pair = key == "saltwater" and owners == {
            ("GEOGRAPHY", "saltwater-state"),
            ("GEOGRAPHY", "saltwater-city"),
        }
        if not approved_root_pair:
            conflicts.append(CanonNameConflict(key, tuple(sorted(
                group, key=lambda x: (x.entity_type, x.source_id, x.display_name.casefold())
            ))))

    unique_names = sorted(grouped)
    near = []
    for index, left in enumerate(unique_names):
        for right in unique_names[index + 1:]:
            if SequenceMatcher(a=left, b=right).ratio() >= 0.90:
                near.append((left, right))

    # The database currently has only the two roots from proposal 0002. All
    # source IDs from SW-GEO-V1 therefore require a future stable-ID mapping.
    unresolved = tuple(sorted(
        item.source_id for item in candidates
        if item.source_id not in {"saltwater-state", "saltwater-city"}
    ))
    source_status = str(payload.get("status", "unknown"))
    can_import = (
        source_status == "APPROVED_FOR_OPERATIONAL_SEED"
        and not conflicts and not near and not unresolved
    )
    return GeographyNameInventory(
        dataset_id=dataset_id,
        source_status=source_status,
        candidates=tuple(sorted(
            candidates, key=lambda x: (x.entity_type, x.source_id, x.display_name.casefold())
        )),
        conflicts=tuple(sorted(conflicts, key=lambda x: x.normalized_key)),
        near_duplicate_pairs=tuple(near),
        unresolved_spatial_ids=unresolved,
        can_import=can_import,
    )
