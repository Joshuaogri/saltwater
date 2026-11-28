"""Deterministic, globally distinct fictional organisation names for BP04."""
from __future__ import annotations

import hashlib
from typing import MutableSet

from runtime.naming import normalize_name

# Curated compound place/family-style roots, deliberately separate from the
# business generator's adjective/noun vocabulary. 32 x 32 combinations provide
# 1,024 stable names without numeric suffixes or sequence placeholders.
ROOT_LEFT = (
    "Alderwick", "Ashcombe", "Briarholt", "Caldermere",
    "Dunraven", "Eldermere", "Fallowby", "Glenhaven",
    "Hawkridge", "Kestrelby", "Larkstone", "Mereford",
    "Oakstead", "Ravensmere", "Thornfield", "Wychwood",
    "Brackenholt", "Foxcombe", "Wrenford", "Cedarwell",
    "Whitcombe", "Marshfield", "Bellhurst", "Fairholm",
    "Redmere", "Winterbourne", "Westmere", "Eastwell",
    "Northwick", "Southmere", "Kingsmere", "Holloway",
)
ROOT_RIGHT = (
    "Barrow", "Bramwell", "Cavendish", "Dunley",
    "Eversham", "Farnham", "Grafton", "Hartwell",
    "Ingleby", "Jarrow", "Kirkham", "Langley",
    "Marlowe", "Norwood", "Ormsby", "Pemberton",
    "Quenby", "Rothwell", "Sedgewick", "Tavistock",
    "Underhill", "Vane", "Waverley", "Yardley",
    "Zennor", "Ashford", "Bexley", "Chiltern",
    "Dorset", "Elmsley", "Fenton", "Grinstead",
)
ROLE_SUFFIX = {
    "property_owner": "Property Holdings",
    "property_manager": "Property Management",
    "historical_owner": "Estate Trust",
    "head_lessee": "Leasehold Holdings",
}


def organisation_name_reservations(display_names) -> set[str]:
    """Return normalized full-name and root reservations from existing names."""
    reserved: set[str] = set()
    normalized_suffixes = tuple(
        sorted((normalize_name(value) for value in ROLE_SUFFIX.values()),
               key=len, reverse=True)
    )
    for display in display_names:
        key = normalize_name(str(display))
        reserved.add(key)
        for suffix in normalized_suffixes:
            marker = " " + suffix
            if key.endswith(marker):
                reserved.add(key[:-len(marker)])
                break
    return reserved


def unique_organisation_name(
    entity_id: str, role: str, reserved_names: MutableSet[str],
) -> str:
    """Return a reproducible name and reserve its root against reuse.

    reserved_names contains normalized canonical names and is updated in place.
    Root pairs are also reserved so separate organisation roles cannot receive
    near-identical names that differ only by a legal descriptor.
    """
    if not isinstance(entity_id, str) or not entity_id.strip():
        raise ValueError("organisation stable ID is required")
    if role not in ROLE_SUFFIX:
        raise ValueError(f"unsupported organisation naming role: {role}")
    total = len(ROOT_LEFT) * len(ROOT_RIGHT)
    start = int.from_bytes(hashlib.sha256(entity_id.encode("utf-8")).digest()[:8], "big") % total
    for offset in range(total):
        index = (start + offset) % total
        root = f"{ROOT_LEFT[index // len(ROOT_RIGHT)]} {ROOT_RIGHT[index % len(ROOT_RIGHT)]}"
        root_key = normalize_name(root)
        display = f"{root} {ROLE_SUFFIX[role]}"
        key = normalize_name(display)
        if root_key in reserved_names or key in reserved_names:
            continue
        reserved_names.add(root_key)
        reserved_names.add(key)
        return display
    raise ValueError("organisation naming vocabulary exhausted; do not append numeric suffixes")
