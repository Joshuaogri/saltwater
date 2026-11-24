"""Dry-run inventory of existing geography canon for SW-NAM-001.

This module never writes to PostgreSQL. It inventories source IDs, detects
collisions, and builds portable entity_code mappings. Database-generated spatial_id
surrogates are looked up by entity_code when a database is materialised.
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
    database_spatial_ids_not_embedded: tuple[str, ...]
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

    # The portable manifest intentionally excludes integer surrogate IDs.
    # The stable source_id -> entity_code mapping is complete; each database
    # assigns spatial_id and it is retrieved by entity_code during materialisation.
    database_ids_not_embedded = tuple(sorted(
        item.source_id for item in candidates
        if item.source_id not in {"saltwater-state", "saltwater-city"}
    ))
    source_status = str(payload.get("status", "unknown"))
    can_import = (
        source_status == "APPROVED_FOR_OPERATIONAL_SEED"
        and not conflicts and not near
    )
    return GeographyNameInventory(
        dataset_id=dataset_id,
        source_status=source_status,
        candidates=tuple(sorted(
            candidates, key=lambda x: (x.entity_type, x.source_id, x.display_name.casefold())
        )),
        conflicts=tuple(sorted(conflicts, key=lambda x: x.normalized_key)),
        near_duplicate_pairs=tuple(near),
        database_spatial_ids_not_embedded=database_ids_not_embedded,
        can_import=can_import,
    )


@dataclass(frozen=True, slots=True)
class SpatialIdentityMapEntry:
    """Stable source-to-entity-code mapping; spatial_id is assigned only on materialisation."""
    source_id: str
    entity_code: str
    entity_type: str
    entity_kind: int
    display_name: str
    parent_entity_code: str
    source_ref: str
    spatial_id: None = None


@dataclass(frozen=True, slots=True)
class SpatialIdentityMap:
    dataset_id: str
    source_status: str
    operational_seed_approved: bool
    entries: tuple[SpatialIdentityMapEntry, ...]


def build_spatial_identity_map(payload: Mapping[str, Any]) -> SpatialIdentityMap:
    """Create a deterministic source-ID mapping without inventing database IDs.

    The source ID is preserved as the future stable sw_geo.entity.entity_code.
    PostgreSQL-generated spatial_id values are deliberately left unassigned
    until a disposable materialisation run records the actual returned IDs.
    """
    if payload.get("schema") != "saltwater-geography/1.0":
        raise ValueError("unsupported geography dataset schema")
    dataset_id = str(payload.get("dataset_id", "")).strip()
    if not dataset_id:
        raise ValueError("geography dataset_id is required")

    rows: list[SpatialIdentityMapEntry] = []

    def add(source_id: Any, entity_type: str, entity_kind: int,
            display_name: Any, parent_code: str) -> None:
        code = str(source_id or "").strip()
        name = str(display_name or "").strip()
        if not code or not name:
            raise ValueError("every mapped spatial identity requires a source ID and display name")
        if code in {"saltwater-state", "saltwater-city"}:
            raise ValueError("project root IDs are already defined by the foundation")
        rows.append(SpatialIdentityMapEntry(
            source_id=code,
            entity_code=code,
            entity_type=entity_type,
            entity_kind=entity_kind,
            display_name=name,
            parent_entity_code=parent_code,
            source_ref=f"{dataset_id}:{entity_type.lower()}:{code}",
        ))

    for item in payload.get("districts", []):
        add(item.get("id"), "DISTRICT", 3, item.get("name"), "saltwater-city")
    for item in payload.get("neighbourhoods", []):
        district_code = str(item.get("district_id") or "").strip()
        if not district_code:
            raise ValueError("neighbourhood requires its source district_id")
        add(item.get("id"), "NEIGHBOURHOOD", 4, item.get("name"), district_code)
    for item in payload.get("roads", []):
        add(item.get("id"), "ROAD", 7, item.get("name"), "saltwater-city")
    for item in payload.get("network", {}).get("routes", []):
        add(item.get("id"), "ROUTE", 9, item.get("name"), "saltwater-city")

    feature_kinds = {
        "harbour_water": ("GEO_ZONE", 5),
        "constructed_water": ("GEO_ZONE", 5),
        "terrain_feature": ("GEO_ZONE", 5),
        "landmark": ("LANDMARK", 10),
    }
    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        feature_type = props.get("entity_type")
        if feature_type not in feature_kinds:
            continue
        mapped_type, mapped_kind = feature_kinds[feature_type]
        add(feature.get("id"), mapped_type, mapped_kind, props.get("name"), "saltwater-city")

    rows.sort(key=lambda item: item.source_id)
    ids = [item.source_id for item in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("spatial source IDs must be globally unique")
    codes = {item.entity_code for item in rows} | {"saltwater-state", "saltwater-city"}
    if any(item.parent_entity_code not in codes for item in rows):
        raise ValueError("spatial parent entity code does not resolve")
    if len({normalize_name(item.display_name) for item in rows}) != len(rows):
        raise ValueError("spatial map contains a duplicate normalized display name")

    source_status = str(payload.get("status", "unknown"))
    return SpatialIdentityMap(
        dataset_id=dataset_id,
        source_status=source_status,
        operational_seed_approved=(source_status == "APPROVED_FOR_OPERATIONAL_SEED"),
        entries=tuple(rows),
    )
