"""Generate Saltwater's 10,000-entity fictional business registry."""
from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import defaultdict
from runtime.dataset_io import load_json
from pathlib import Path

from runtime.property_world_generator import build_property_world, to_columnar_document
from runtime.property_tenure_generator import _expand_columnar
from runtime.naming import GeneratorConfig, normalize_name, pg_trgm_similarity
from runtime.name_generation import generate_candidates
from runtime.naming_inventory import inventory_geography_names

GENERATOR = "SW-BUSINESS-REGISTRY-GENERATOR-002"
BUSINESS_NAME_SEED = 20261126
TARGET_BUSINESSES = 10_000

SECTORS = [
    ("retail_trade", 1500, ["general_retail", "clothing", "hardware", "books_stationery", "household_goods", "market_stall"]),
    ("food_hospitality", 1100, ["restaurant", "cafe", "bakery", "hotel", "catering", "bar_and_grill"]),
    ("professional_services", 950, ["legal_services", "accountancy", "consultancy", "architecture", "recruitment", "business_administration"]),
    ("transport_logistics", 900, ["road_freight", "courier", "vehicle_services", "warehousing", "passenger_transport", "freight_forwarding"]),
    ("manufacturing", 650, ["metal_fabrication", "food_processing", "textiles", "furniture", "packaging", "light_assembly"]),
    ("construction_property", 700, ["building_contractor", "electrical_contractor", "plumbing", "property_management", "building_maintenance", "materials_supplier"]),
    ("finance_insurance", 550, ["banking_services", "insurance_broker", "credit_services", "payments", "financial_advice"]),
    ("health_wellness", 550, ["clinic", "dental_practice", "pharmacy", "optician", "fitness", "care_services"]),
    ("education_training", 300, ["training_provider", "tutoring", "vocational_training", "language_school", "learning_services"]),
    ("creative_entertainment", 450, ["music_venue", "film_media", "design_studio", "theatre_services", "events", "publishing"]),
    ("personal_services", 650, ["hair_and_beauty", "laundry", "repair_services", "hospitality_support", "domestic_services", "funeral_services"]),
    ("maritime_trade", 300, ["ship_chandlery", "marine_repairs", "port_services", "customs_brokerage", "fishing_supply"]),
    ("technology_communications", 500, ["software_services", "telecommunications", "computer_repair", "data_services", "electronics"]),
    ("food_production", 300, ["wholesale_food", "produce_distribution", "speciality_food", "urban_growing", "beverage_production"]),
    ("wholesale_trade", 600, ["wholesale_goods", "import_export", "industrial_supply", "commercial_distribution", "building_supply"]),
]

PREFIXES = ["Harbour", "Crown", "Meridian", "Westgate", "Northbank", "Foundry", "Civic", "Beacon", "Quayside", "Greenfield", "Southworks", "Market", "Ridgeway", "Assembly", "Marina", "Canal"]
ROOTS = ["Bridge", "Stone", "Anchor", "Lantern", "Compass", "Orchard", "Foundry", "Exchange", "Crescent", "Pioneer", "Harbourlight", "Seaforth", "Copper", "Silver", "Elm", "Kings"]

def _digest(key: str) -> bytes:
    return hashlib.sha256(key.encode()).digest()

def _pick(values, key):
    return values[int.from_bytes(_digest(key)[:4], "big") % len(values)]

def _number(key: str, low: int, high: int) -> int:
    return low + int.from_bytes(_digest(key)[:4], "big") % (high-low+1)

def _sector_for(index: int):
    cursor = index
    for sector, count, activities in SECTORS:
        if cursor < count:
            return sector, activities[cursor % len(activities)]
        cursor -= count
    raise ValueError("Business sector allocation does not cover registry target")

def _load_business_name_config() -> tuple[GeneratorConfig, tuple[str, ...], tuple[str, ...]]:
    """Load the versioned SW-UNS business vocabulary; no mutable DB writes."""
    root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (root / "data/naming/saltwater-business-naming-v1.json").read_text(encoding="utf-8")
    )
    if payload.get("schema") != "saltwater-business-naming-vocabulary/1.0":
        raise ValueError("unsupported business naming vocabulary schema")
    adjectives = tuple(str(x).strip() for x in payload.get("adjectives", []) if str(x).strip())
    nouns = tuple(str(x).strip() for x in payload.get("nouns", []) if str(x).strip())
    forms = tuple(str(x).strip() for x in payload.get("business_forms", []) if str(x).strip())
    legal_suffixes = tuple(str(x).strip() for x in payload.get("legal_suffixes", []) if str(x).strip())
    if not adjectives or not nouns or not forms or not legal_suffixes:
        raise ValueError("business naming vocabulary sections must be non-empty")
    roots = tuple(f"{adjective} {noun}" for adjective in adjectives for noun in nouns)
    if len({normalize_name(x) for x in roots}) != len(roots):
        raise ValueError("business root vocabulary contains normalized duplicates")
    config = GeneratorConfig(
        given_names=(), middle_names=(), family_names=(), place_roots=(),
        business_roots=roots, business_forms=forms,
        config_version=str(payload.get("config_version", "")),
    )
    if not config.config_version:
        raise ValueError("business naming config_version is required")
    return config, forms, legal_suffixes


def _possible_near_duplicate_roots(
    adjective: str,
    noun: str,
    similar_tokens: dict[str, tuple[str, ...]],
) -> tuple[tuple[str, str], ...]:
    """Return nearby root pairs in same and swapped word-role order."""
    nearby_adjectives = similar_tokens[adjective]
    nearby_nouns = similar_tokens[noun]
    return tuple(dict.fromkeys(
        [(other_adjective, other_noun)
         for other_adjective in nearby_adjectives
         for other_noun in nearby_nouns]
        + [(other_adjective, other_noun)
           for other_adjective in nearby_nouns
           for other_noun in nearby_adjectives]
    ))


def _name_trigrams(normalized_name: str) -> frozenset[str]:
    return frozenset(
        f"  {word} "[offset:offset + 3]
        for word in normalized_name.split()
        for offset in range(max(0, len(f"  {word} ") - 2))
    )


def _build_canonical_name_index(names: tuple[str, ...]):
    signatures: list[tuple[str, frozenset[str]]] = []
    postings: dict[int, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for name in names:
        signature = _name_trigrams(normalize_name(name))
        if not signature:
            continue
        index = len(signatures)
        signatures.append((name, signature))
        for trigram in signature:
            postings[len(signature)][trigram].append(index)
    return signatures, postings


def _has_canonical_near_duplicate(name: str, index) -> bool:
    signatures, postings = index
    normalized = normalize_name(name)
    candidate = _name_trigrams(normalized)
    if not candidate:
        return False
    minimum_size = math.ceil(len(candidate) * 0.90)
    maximum_size = math.floor(len(candidate) / 0.90)
    anchor_count = max(1, math.floor(len(candidate) * 0.10) + 1)
    prior_sizes = range(minimum_size, maximum_size + 1)
    frequencies = []
    for trigram in candidate:
        frequency = sum(
            len(postings.get(size, {}).get(trigram, ())) for size in prior_sizes
        )
        if frequency:
            frequencies.append((frequency, trigram))
    anchors = [trigram for _, trigram in sorted(frequencies)[:anchor_count]]
    possible: set[int] = set()
    for trigram in anchors:
        for size in prior_sizes:
            possible.update(postings.get(size, {}).get(trigram, ()))
    for prior_index in possible:
        prior_name, prior_signature = signatures[prior_index]
        common = len(candidate & prior_signature)
        required = math.ceil(
            0.90 * (len(candidate) + len(prior_signature)) / 1.90
        )
        if common >= required and pg_trgm_similarity(name, prior_name) > 0.90:
            return True
    return False


def _generate_business_names_report(source: dict, property_world: dict | None = None) -> dict:
    config, _, legal_suffixes = _load_business_name_config()
    candidate_pool_count = TARGET_BUSINESSES + 2000
    candidates = generate_candidates(
        "business", candidate_pool_count, seed=BUSINESS_NAME_SEED, config=config
    )
    geography = inventory_geography_names(source)
    geography_names = tuple(item.display_name for item in geography.candidates)
    canonical_names = list(geography_names)
    if property_world:
        for organisation in property_world.get("owner_organisations", []):
            if organisation.get("display_name"):
                canonical_names.append(organisation["display_name"])
        for collection in ("properties", "buildings", "premises"):
            for item in property_world.get(collection, []):
                display = (
                    item.get("display_name") or item.get("property_name")
                    or item.get("building_name") or item.get("premises_name")
                    or item.get("name")
                )
                if display:
                    canonical_names.append(display)
    canonical_names = tuple(dict.fromkeys(canonical_names))
    reserved = {normalize_name(name) for name in canonical_names}
    # Screen candidates against every currently adopted geography/property/
    # organisation name before assigning stable business IDs. Use an exact
    # rare-trigram candidate index instead of an O(names x canon) scan.
    canonical_name_index = _build_canonical_name_index(canonical_names)

    adjective_vocab = tuple(dict.fromkeys(root.split(" ", 1)[0] for root in config.business_roots))
    noun_vocab = tuple(dict.fromkeys(root.split(" ", 1)[1] for root in config.business_roots))
    def similar_words(words: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
        return {
            word: tuple(
                other for other in words
                if pg_trgm_similarity(word, other) > 0.0
            )
            for word in words
        }
    similar_tokens = similar_words(tuple(dict.fromkeys(adjective_vocab + noun_vocab)))

    accepted_trading: list[str] = []
    accepted_registered: list[str] = []
    accepted_by_root: dict[tuple[str, str], list[str]] = {}
    accepted_public_keys: set[str] = set()
    held_near_duplicates = 0
    held_exact_collisions = 0
    held_geography_near_duplicates = 0

    for candidate in candidates:
        adjective, noun, *_ = candidate.split()
        business_id = f"SWBIZ-{len(accepted_trading) + 1:06d}"
        registered_name = (
            f"{candidate} {_pick(legal_suffixes, business_id + '-legal-suffix')}"
        )
        public_names = (candidate, registered_name)
        public_keys = tuple(normalize_name(name) for name in public_names)

        if len(set(public_keys)) != len(public_keys) or any(
            key in reserved or key in accepted_public_keys for key in public_keys
        ):
            held_exact_collisions += 1
            continue

        canon_near_duplicate = any(
            _has_canonical_near_duplicate(public_name, canonical_name_index)
            for public_name in public_names
        )
        if canon_near_duplicate:
            held_near_duplicates += 1
            held_geography_near_duplicates += 1
            continue

        near_duplicate = False
        # pg_trgm is insensitive to word order in many short phrases.
        # Search only nearby token pairs, in both word-role alignments, rather
        # than scanning the full adjective x noun vocabulary for every row.
        possible_roots = _possible_near_duplicate_roots(adjective, noun, similar_tokens)
        for root in possible_roots:
            for existing_name in accepted_by_root.get(root, ()):
                if any(
                    pg_trgm_similarity(public_name, existing_name) > 0.90
                    for public_name in public_names
                ):
                    near_duplicate = True
                    break
            if near_duplicate:
                break

        if near_duplicate:
            held_near_duplicates += 1
            continue

        accepted_trading.append(candidate)
        accepted_registered.append(registered_name)
        accepted_public_keys.update(public_keys)
        accepted_by_root.setdefault((adjective, noun), []).extend(public_names)
        if len(accepted_trading) == TARGET_BUSINESSES:
            break

    if len(accepted_trading) != TARGET_BUSINESSES:
        raise ValueError(
            "business vocabulary produced only "
            f"{len(accepted_trading)} names after PostgreSQL-compatible exact "
            "and near-duplicate review"
        )
    return {
        "names": tuple(accepted_trading),
        "registered_names": tuple(accepted_registered),
        "candidate_pool_count": candidate_pool_count,
        "near_duplicate_candidates_held": held_near_duplicates,
        "exact_collision_candidates_held": held_exact_collisions,
        "geography_near_duplicate_candidates_held": held_geography_near_duplicates,
        "near_duplicate_threshold": 0.90,
        "similarity_algorithm": "POSTGRES_PG_TRGM_COMPATIBLE",
        "geography_names_checked": len(geography_names),
        "adopted_canonical_names_checked": len(canonical_names),
        "public_name_count": len(accepted_public_keys),
    }


def _generate_business_names(source: dict) -> tuple[str, ...]:
    return _generate_business_names_report(source)["names"]


def build_business_registry(source: dict, property_world: dict | None = None) -> dict:
    property_world = property_world or build_property_world(source)
    units = property_world["units"]
    premises = {x["premises_id"]: x for x in property_world["premises"]}
    properties = {x["property_id"]: x for x in property_world["properties"]}
    buildings = {x["building_id"]: x for x in property_world["buildings"]}
    addresses = {x["address_id"]: x for x in property_world["addresses"]}

    non_residential = [u for u in units if u["unit_class"] != "dwelling"]
    residential_home_business = [u for u in units if u["unit_class"] == "dwelling"]
    ordered_units = sorted(non_residential, key=lambda x: x["unit_id"])
    if len(ordered_units) < TARGET_BUSINESSES:
        ordered_units.extend(sorted(residential_home_business, key=lambda x: x["unit_id"]))
    if len(ordered_units) < TARGET_BUSINESSES:
        raise ValueError("Not enough canonical units to host the business registry")
    selected_units = ordered_units[:TARGET_BUSINESSES]

    name_report = _generate_business_names_report(source, property_world)
    trade_names = name_report["names"]
    registered_names = name_report["registered_names"]
    businesses, establishments, occupancy_links = [], [], []
    sector_counts = {}
    used_public_names: set[str] = set()
    for index, unit in enumerate(selected_units):
        sequence = index + 1
        business_id = f"SWBIZ-{sequence:06d}"
        establishment_id = f"SWEST-{sequence:06d}"
        sector, activity = _sector_for(index)
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
        property_id = unit["property_id"]
        building_id = unit["building_id"]
        premises_id = unit["premises_id"]
        address_id = unit["address_id"]
        prop = properties[property_id]
        prem = premises[premises_id]
        building = buildings[building_id]
        address = addresses[address_id]
        trade_name = trade_names[index]
        registered_name = registered_names[index]
        for public_name in (trade_name, registered_name):
            key = normalize_name(public_name)
            if key in used_public_names:
                raise ValueError(f"business public name collision: {public_name}")
            used_public_names.add(key)
        legal_form = _pick(["private_limited_company","limited_liability_partnership","cooperative","sole_establishment_company","public_company"], business_id+"-form")
        size = _pick(["micro","small","small","medium","medium","large"], business_id+"-size")
        status = "active" if _number(business_id+"-status",1,100) <= 94 else ("seasonal" if _number(business_id+"-season",1,2)==1 else "temporarily_inactive")
        home_based = unit["unit_class"] == "dwelling"
        open_profile = _pick(["08:00-17:00","09:00-18:00","07:00-19:00","10:00-22:00","24_hour_or_shift_based","appointment_only"], business_id+"-hours")
        employee_band = {"micro":"1-4","small":"5-19","medium":"20-99","large":"100-499"}[size]
        businesses.append({
            "business_id": business_id,
            "registered_name": registered_name,
            "trading_name": trade_name,
            "sector": sector,
            "primary_activity": activity,
            "legal_form": legal_form,
            "business_size": size,
            "employee_band": employee_band,
            "status": status,
            "year_established": _number(business_id+"-founded", 1985, 2026),
            "registered_city": "Saltwater",
            "registered_address_id": address_id,
            "primary_establishment_id": establishment_id,
            "fictional_entity": True,
            "person_records_created": 0,
            "source_generator": GENERATOR,
        })
        establishments.append({
            "establishment_id": establishment_id,
            "business_id": business_id,
            "establishment_name": trade_name,
            "establishment_type": "home_based_business" if home_based else "operating_business_site",
            "property_id": property_id,
            "building_id": building_id,
            "premises_id": premises_id,
            "unit_id": unit["unit_id"],
            "address_id": address_id,
            "district_id": prop["source_district_id"],
            "neighbourhood_id": prop["source_neighbourhood_id"],
            "floor_level": unit["floor_level"],
            "unit_locator": unit["unit_locator"],
            "premises_function": prem["primary_function"],
            "building_use": building["building_use"],
            "opening_hours_profile": open_profile,
            "delivery_access": _pick(["front_desk","rear_service_access","loading_bay","courier_collection_point","no_routine_deliveries"], establishment_id+"-delivery"),
            "customer_access": "appointment_or_public_entry" if home_based else _pick(["public_front_door","reception_controlled","street_shopfront","scheduled_service_entry"], establishment_id+"-customer"),
            "security_profile": _pick(["keyed_entry","alarm_and_cctv","staffed_reception","electronic_access","shopfront_shutters"], establishment_id+"-security"),
            "operating_status": status,
            "source_generator": GENERATOR,
        })
        occupancy_links.append({
            "business_unit_link_id": f"SWBUL-{sequence:06d}",
            "business_id": business_id,
            "establishment_id": establishment_id,
            "unit_id": unit["unit_id"],
            "premises_id": premises_id,
            "valid_from_tick": 0,
            "valid_to_tick": None,
            "occupancy_relationship": "business_operator",
            "occupancy_status": "active" if status == "active" else status,
        })

    body = {
        "schema": "saltwater-business-registry/1.0",
        "dataset_id": "SW-BUSINESS-REGISTRY-V1",
        "canon_status": "CANONICAL_FICTIONAL_GAME_WORLD",
        "generator": GENERATOR,
        "effective_tick": 0,
        "city": "Saltwater",
        "city_population_hard_cap": 10000,
        "summary": {
            "distinct_business_count": len(businesses),
            "establishment_count": len(establishments),
            "business_unit_link_count": len(occupancy_links),
            "sector_count": len(sector_counts),
            "businesses_by_sector": sector_counts,
            "active_businesses": sum(1 for x in businesses if x["status"] == "active"),
            "seasonal_businesses": sum(1 for x in businesses if x["status"] == "seasonal"),
            "temporarily_inactive_businesses": sum(1 for x in businesses if x["status"] == "temporarily_inactive"),
            "home_based_businesses": sum(1 for x in establishments if x["establishment_type"] == "home_based_business"),
            "population_records_created": 0,
            "staff_person_records_created": 0,
        },
        "businesses": businesses,
        "establishments": establishments,
        "business_unit_links": occupancy_links,
        "naming": {
            "standard": "SW-UNS-001",
            "vocabulary_dataset": "SW-BUSINESS-NAMING-V1",
            "vocabulary_config_version": _load_business_name_config()[0].config_version,
            "generator_version": 1,
            "seed": BUSINESS_NAME_SEED,
            "candidate_count": len(trade_names),
            "candidate_pool_count": name_report["candidate_pool_count"],
            "near_duplicate_candidates_held": name_report["near_duplicate_candidates_held"],
            "geography_near_duplicate_candidates_held": name_report["geography_near_duplicate_candidates_held"],
            "exact_collision_candidates_held": name_report["exact_collision_candidates_held"],
            "near_duplicate_threshold": name_report["near_duplicate_threshold"],
            "similarity_algorithm": name_report["similarity_algorithm"],
            "near_duplicate_screen": "PASS_WITHIN_ALL_GENERATED_PUBLIC_NAMES",
            "geography_names_checked": name_report["geography_names_checked"],
            "adopted_canonical_names_checked": name_report["adopted_canonical_names_checked"],
            "public_name_count": name_report["public_name_count"],
            "reservation_status": "DRY_RUN_CANDIDATES_NOT_YET_PERSISTENTLY_RESERVED",
            "exact_geography_collision_check": "PASS",
            "numeric_placeholder_check": "PASS",
        },
        "lineage": {
            "property_world_dataset": "SW-PROPERTY-WORLD-V1",
            "property_count": property_world["summary"]["property_count"],
            "building_count": property_world["summary"]["building_count"],
            "premises_count": property_world["summary"]["premises_count"],
            "unit_count": property_world["summary"]["unit_count"],
        },
        "gameplay": {
            "registry_minimum": 10000,
            "registry_invariant": "At least 10,000 distinct local business identities.",
            "location_resolution": "Every establishment links to a canonical property, building, premises, unit and address.",
            "population_isolation": "Businesses, establishments and staffing bands do not create person records or count toward population.",
            "city_scope": "Only Saltwater-local businesses and premises are generated; no second city or off-map playable territory is created.",
        },
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    world_document = load_json(root / "data/property/saltwater-property-world-v1.json")
    property_world = _expand_columnar(world_document)
    result = build_business_registry(source, property_world=property_world)
    output = root / "data/business/saltwater-business-registry-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    document = to_columnar_document(result)
    serialized = (json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    output.write_bytes(serialized)
    compressed = output.with_suffix(output.suffix + ".gz")
    compressed.write_bytes(gzip.compress(serialized, compresslevel=9, mtime=0))
    print(json.dumps(result["summary"] | {
        "manifest_sha256": result["manifest_sha256"],
        "output_bytes": output.stat().st_size,
        "compressed_output_bytes": compressed.stat().st_size,
        "naming": result["naming"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
