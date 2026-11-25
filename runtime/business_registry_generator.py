"""Generate Saltwater's 10,000-entity fictional business registry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from runtime.property_world_generator import build_property_world, to_columnar_document

GENERATOR = "SW-BUSINESS-REGISTRY-GENERATOR-001"
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

def build_business_registry(source: dict) -> dict:
    property_world = build_property_world(source)
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

    businesses, establishments, occupancy_links = [], [], []
    sector_counts = {}
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
        prefix = _pick(PREFIXES, business_id + "-prefix")
        root = _pick(ROOTS, business_id + "-root")
        trade_name = f"{prefix} {root} {sequence:05d}"
        legal_form = _pick(["private_limited_company","limited_liability_partnership","cooperative","sole_establishment_company","public_company"], business_id+"-form")
        size = _pick(["micro","small","small","medium","medium","large"], business_id+"-size")
        status = "active" if _number(business_id+"-status",1,100) <= 94 else ("seasonal" if _number(business_id+"-season",1,2)==1 else "temporarily_inactive")
        home_based = unit["unit_class"] == "dwelling"
        open_profile = _pick(["08:00-17:00","09:00-18:00","07:00-19:00","10:00-22:00","24_hour_or_shift_based","appointment_only"], business_id+"-hours")
        employee_band = {"micro":"1-4","small":"5-19","medium":"20-99","large":"100-499"}[size]
        businesses.append({
            "business_id": business_id,
            "registered_name": f"{trade_name} {_pick(['Limited','Company','Trading','Enterprises','Cooperative'], business_id+'-suffix')}",
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
    result = build_business_registry(source)
    output = root / "data/business/saltwater-business-registry-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    document = to_columnar_document(result)
    output.write_text(json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"] | {"manifest_sha256": result["manifest_sha256"], "output_bytes": output.stat().st_size}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
