"""Shared deterministic naming rules and candidate generation for Saltwater.

The in-memory registry is a test/reference adapter. PostgreSQL is authoritative
for persisted names; all writes must pass its transactional reservation function.
"""
from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Iterable, Mapping


NORMALIZER_VERSION = 1
GENERATOR_VERSION = 1
ROAD_SUFFIXES = {
    "rd": "road", "st": "street", "ave": "avenue", "av": "avenue",
    "cres": "crescent", "cl": "close", "ln": "lane", "dr": "drive",
    "sq": "square", "pl": "place", "ct": "court", "mews": "mews",
}
PUNCTUATION = str.maketrans({
    "’": "'", "‘": "'", "ʼ": "'", "＇": "'",
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    "“": '"', "”": '"', "„": '"',
})


class NamingError(ValueError):
    """A proposed name is invalid or cannot be reserved."""


class NameCollision(NamingError):
    """A name is already reserved by a different entity."""


class NameReviewRequired(NamingError):
    """A name is too similar to an existing name and needs human review."""


def normalize_name(value: str, *, road_suffixes: Mapping[str, str] | None = None) -> str:
    """Return a deterministic comparison key without changing display spelling."""
    if not isinstance(value, str):
        raise TypeError("name must be text")
    value = unicodedata.normalize("NFKC", value).translate(PUNCTUATION)
    if any(unicodedata.category(ch) in {"Cc", "Cs"} for ch in value):
        raise NamingError("control or surrogate characters are not permitted")
    value = value.casefold().strip()
    value = value.replace("'", "")
    value = re.sub(r"[-‐‑‒–—−]+", " ", value)
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    tokens = value.split()
    if not tokens:
        raise NamingError("name cannot be empty")
    suffixes = dict(ROAD_SUFFIXES)
    if road_suffixes:
        suffixes.update({str(k).casefold(): str(v).casefold() for k, v in road_suffixes.items()})
    if tokens:
        tokens[-1] = suffixes.get(tokens[-1], tokens[-1])
    return " ".join(tokens)


@dataclass(frozen=True, slots=True)
class NameRecord:
    entity_type: str
    entity_id: str
    display_name: str
    normalized_key: str
    name_form: str
    status: str = "active"
    normalizer_version: int = NORMALIZER_VERSION


@dataclass(frozen=True, slots=True)
class NameSearchResult:
    records: tuple[NameRecord, ...]
    ambiguous: bool


@dataclass(slots=True)
class NameRegistry:
    """Deterministic reference registry with the one Saltwater root exception."""
    review_threshold: float = 0.90
    records: list[NameRecord] = field(default_factory=list)

    _SALTWATER_ROOTS = {
        ("geography_sovereign_root", "saltwater-state"),
        ("geography_playable_city", "saltwater-city"),
    }

    def _owner(self, entity_type: str, entity_id: str) -> tuple[str, str]:
        return entity_type.strip().casefold(), str(entity_id)

    def _saltwater_slot(self, owner: tuple[str, str], key: str, form: str) -> bool:
        return key == "saltwater" and form == "canonical" and owner in self._SALTWATER_ROOTS

    def _near_matches(self, key: str) -> tuple[str, ...]:
        found = set()
        for record in self.records:
            ratio = SequenceMatcher(a=key, b=record.normalized_key).ratio()
            if ratio >= self.review_threshold and key != record.normalized_key:
                found.add(record.display_name)
        return tuple(sorted(found, key=str.casefold))

    def _reactivate(self, record: NameRecord, owner: tuple[str, str]) -> NameRecord:
        if record.name_form == "canonical":
            for index, other in enumerate(self.records):
                if (
                    self._owner(other.entity_type, other.entity_id) == owner
                    and other.name_form == "canonical"
                    and other.status == "active"
                    and other.normalized_key != record.normalized_key
                ):
                    self.records[index] = NameRecord(
                        other.entity_type, other.entity_id, other.display_name,
                        other.normalized_key, other.name_form, "superseded",
                        other.normalizer_version,
                    )
        restored = NameRecord(
            record.entity_type, record.entity_id, record.display_name,
            record.normalized_key, record.name_form, "active",
            record.normalizer_version,
        )
        self.records[self.records.index(record)] = restored
        return restored

    def reserve(
        self, entity_type: str, entity_id: str, display_name: str,
        *, name_form: str = "canonical", review_near_duplicates: bool = True,
    ) -> NameRecord:
        owner = self._owner(entity_type, entity_id)
        if not all(owner):
            raise NamingError("entity type and stable entity ID are required")
        form = name_form.strip().casefold()
        if form not in {"canonical", "preferred", "alias", "legal", "trading", "call_sign"}:
            raise NamingError("unsupported name form")
        key = normalize_name(display_name)

        if key == "saltwater" and not self._saltwater_slot(owner, key, form):
            raise NameCollision("Saltwater is reserved only for the sovereign territory and playable city")
        if key == "saltwater" and display_name != "Saltwater":
            raise NameCollision("the Saltwater root exception permits only exact display spelling")
        if self._saltwater_slot(owner, key, form):
            for existing in self.records:
                if existing.normalized_key == key:
                    existing_owner = self._owner(existing.entity_type, existing.entity_id)
                    if existing_owner not in self._SALTWATER_ROOTS:
                        raise NameCollision("Saltwater is reserved by a non-root entity")
                    if existing_owner == owner and existing.name_form == form:
                        return existing if existing.status == "active" else self._reactivate(existing, owner)
        else:
            for existing in self.records:
                if existing.normalized_key == key:
                    if self._owner(existing.entity_type, existing.entity_id) == owner and existing.name_form == form:
                        return existing if existing.status == "active" else self._reactivate(existing, owner)
                    raise NameCollision(f"name already reserved: {display_name}")

        if review_near_duplicates:
            matches = self._near_matches(key)
            if matches:
                raise NameReviewRequired("near-duplicate review required: " + ", ".join(matches))

        if form == "canonical":
            for index, existing in enumerate(self.records):
                if (
                    self._owner(existing.entity_type, existing.entity_id) == owner
                    and existing.name_form == "canonical"
                    and existing.status == "active"
                    and existing.normalized_key != key
                ):
                    self.records[index] = NameRecord(
                        existing.entity_type, existing.entity_id, existing.display_name,
                        existing.normalized_key, existing.name_form, "superseded",
                        existing.normalizer_version,
                    )
        record = NameRecord(owner[0], owner[1], display_name, key, form)
        self.records.append(record)
        return record

    def rename(self, entity_type: str, entity_id: str, new_name: str) -> NameRecord:
        owner = self._owner(entity_type, entity_id)
        active = [r for r in self.records if self._owner(r.entity_type, r.entity_id) == owner
                  and r.name_form == "canonical" and r.status == "active"]
        if len(active) > 1:
            raise NamingError("entity has multiple active canonical names")
        return self.reserve(entity_type, entity_id, new_name, review_near_duplicates=False)

    def retire(self, entity_type: str, entity_id: str, display_name: str) -> None:
        owner = self._owner(entity_type, entity_id)
        key = normalize_name(display_name)
        for index, record in enumerate(self.records):
            if self._owner(record.entity_type, record.entity_id) == owner and record.normalized_key == key:
                self.records[index] = NameRecord(
                    record.entity_type, record.entity_id, record.display_name,
                    record.normalized_key, record.name_form, "retired",
                    record.normalizer_version,
                )
                return
        raise NamingError("name reservation not found")

    def search(self, value: str) -> NameSearchResult:
        key = normalize_name(value)
        found = tuple(r for r in self.records if r.normalized_key == key)
        return NameSearchResult(found, len(found) > 1)


@dataclass(frozen=True, slots=True)
class GeneratorConfig:
    given_names: tuple[str, ...]
    middle_names: tuple[str, ...]
    family_names: tuple[str, ...]
    place_roots: tuple[str, ...]
    business_roots: tuple[str, ...]
    business_forms: tuple[str, ...] = ("Works", "House", "Trading", "Services", "Group")
    building_roots: tuple[str, ...] = ()
    building_forms: tuple[str, ...] = ("House", "Court", "Tower", "Hall", "Residences", "Mews")
    organisation_roots: tuple[str, ...] = ()
    organisation_forms: tuple[str, ...] = ("Association", "Foundation", "Authority", "Trust", "Institute", "Group")
    operational_roots: tuple[str, ...] = ()
    operational_forms: tuple[str, ...] = ("Beacon", "Harbour", "Civic", "Rapid", "Delta", "Summit", "North", "South")
    config_version: str = "1"


@dataclass(frozen=True, slots=True)
class GeneratedNameBatch:
    domain: str
    generator_version: int
    normalizer_version: int
    config_version: str
    seed: int
    candidates: tuple[str, ...]
    manifest_sha256: str


def generate_candidates(domain: str, count: int, *, seed: int, config: GeneratorConfig) -> tuple[str, ...]:
    """Generate deterministic fictional candidates; reservation remains separate."""
    if count < 0 or count > 100_000:
        raise ValueError("count must be between 0 and 100000")
    rng = random.Random(seed)
    domain = domain.strip().casefold()
    output: list[str] = []
    seen: set[str] = set()
    attempts = max(100, count * 30)
    for _ in range(attempts):
        if len(output) >= count:
            break
        if domain == "person":
            if not (config.given_names and config.middle_names and config.family_names):
                raise ValueError("person vocabularies must not be empty")
            candidate = " ".join((rng.choice(config.given_names),
                                  rng.choice(config.middle_names),
                                  rng.choice(config.family_names)))
        elif domain == "road":
            if not config.place_roots:
                raise ValueError("place_roots must not be empty")
            candidate = f"{rng.choice(config.place_roots)} {rng.choice(('Road','Street','Avenue','Crescent','Close','Lane','Drive','Walk','Mews','Square'))}"
        elif domain == "business":
            if not config.business_roots:
                raise ValueError("business_roots must not be empty")
            # Business roots are sampled without replacement. A root is used once
            # per batch, so uniqueness never depends on appending numeric IDs.
            normalized_roots = [normalize_name(root) for root in config.business_roots]
            if len(normalized_roots) != len(set(normalized_roots)):
                raise NamingError("business root vocabulary contains normalized duplicates")
            if count > len(config.business_roots):
                raise NamingError("business root vocabulary is too small for requested batch")
            selected_roots = rng.sample(list(config.business_roots), count)
            output = [
                f"{root} {rng.choice(config.business_forms)}"
                for root in selected_roots
            ]
            normalized_candidates = [normalize_name(name) for name in output]
            if len(normalized_candidates) != len(set(normalized_candidates)):
                raise NamingError("business candidate batch contains normalized duplicates")
            return tuple(output)
        elif domain == "building":
            roots = config.building_roots or config.place_roots
            if not roots:
                raise ValueError("building_roots or place_roots must not be empty")
            candidate = f"{rng.choice(roots)} {rng.choice(config.building_forms)}"
        elif domain == "organisation":
            roots = config.organisation_roots or config.business_roots
            if not roots:
                raise ValueError("organisation_roots or business_roots must not be empty")
            candidate = f"{rng.choice(roots)} {rng.choice(config.organisation_forms)}"
        elif domain == "operational":
            if not config.operational_roots:
                raise ValueError("operational_roots must not be empty")
            candidate = f"{rng.choice(config.operational_roots)} {rng.choice(config.operational_forms)}"
        else:
            raise ValueError("unsupported naming domain")
        key = normalize_name(candidate)
        if key not in seen:
            seen.add(key)
            output.append(candidate)
    if len(output) != count:
        raise NamingError(f"vocabulary produced only {len(output)} unique candidates for {count} requested")
    return tuple(output)


def generate_batch(domain: str, count: int, *, seed: int, config: GeneratorConfig) -> GeneratedNameBatch:
    """Return deterministic candidates with a compact reproducibility manifest."""
    import hashlib
    import json

    candidates = generate_candidates(domain, count, seed=seed, config=config)
    manifest = {
        "domain": domain.strip().casefold(),
        "generator_version": GENERATOR_VERSION,
        "normalizer_version": NORMALIZER_VERSION,
        "config_version": config.config_version,
        "seed": seed,
        "candidates": candidates,
    }
    digest = hashlib.sha256(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    return GeneratedNameBatch(
        domain=manifest["domain"],
        generator_version=GENERATOR_VERSION,
        normalizer_version=NORMALIZER_VERSION,
        config_version=config.config_version,
        seed=seed,
        candidates=candidates,
        manifest_sha256=digest,
    )
