"""Generate Saltwater building systems, utility connections and metering.

Consumes the persisted compact property and tenure datasets. It does not
rebuild geography, create people, post bills or alter the population ledger.
"""
from __future__ import annotations

import hashlib
import json
from runtime.dataset_io import load_json
from pathlib import Path

from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR = "SW-BUILDING-SYSTEMS-UTILITIES-001"

PROVIDERS = {
    "electricity": ("SWORG-UTIL-ELECTRIC", "Saltwater Grid and Power Authority", "electricity_network_operator"),
    "potable_water": ("SWORG-UTIL-WATER", "Saltwater Waterworks Corporation", "water_utility_operator"),
    "wastewater": ("SWORG-UTIL-WASTE", "Saltwater Wastewater and Sewerage Authority", "wastewater_utility_operator"),
    "telecommunications": ("SWORG-UTIL-TELECOM", "Saltwater Fibre and Communications Exchange", "telecommunications_network_operator"),
}


def _n(key: str, low: int, high: int) -> int:
    digest = hashlib.sha256(key.encode()).digest()
    return low + int.from_bytes(digest[:4], "big") % (high - low + 1)


def _pick(values, key: str):
    return values[_n(key, 0, len(values) - 1)]


def _slug(value: str) -> str:
    return "".join(c for c in value.upper() if c.isalnum())[:24]


def build_building_services(world: dict, tenure: dict) -> dict:
    properties = {x["property_id"]: x for x in world["properties"]}
    buildings = {x["building_id"]: x for x in world["buildings"]}
    units = {x["unit_id"]: x for x in world["units"]}
    owners = {x["property_id"]: x["owner_organisation_id"] for x in tenure["current_ownership_interests"]}
    managers = {x["property_id"]: x["manager_organisation_id"] for x in tenure["management_appointments"]}
    occupancies = {x["unit_id"]: x for x in tenure["occupancies"]}
    premises = {x["premises_id"]: x for x in world["premises"]}

    providers = [
        {"organisation_id": oid, "display_name": name, "organisation_type": kind,
         "registered_city": "Saltwater", "status": "active", "fictional_entity": True,
         "service_area": "citywide_and_port_estate"}
        for oid, name, kind in PROVIDERS.values()
    ]

    connections, accounts, meters = [], [], []
    systems, equipment, inspections, tenant_responsibilities = [], [], [], []
    system_types = [
        "electrical_distribution", "potable_water_distribution",
        "wastewater_and_sanitary", "heating_ventilation_and_cooling",
        "fire_detection_and_suppression", "physical_security_and_access",
        "building_management_controls", "vertical_transport",
    ]
    for pid in sorted(properties):
        prop = properties[pid]
        owner_id = owners[pid]
        manager_id = managers[pid]
        for service, (provider_id, _, _) in PROVIDERS.items():
            connection_id = f"SWUCON-{_slug(pid)}-{service[:3].upper()}"
            connections.append({
                "utility_connection_id": connection_id,
                "property_id": pid,
                "primary_building_id": prop.get("primary_building_id"),
                "utility_type": service,
                "provider_organisation_id": provider_id,
                "connection_point_type": _pick(["street_main","estate_distribution_main","dedicated_service_cabinet","port_estate_service_corridor"], pid+service+"-point"),
                "connection_capacity_band": _pick(["standard","enhanced","high_capacity","critical_infrastructure"], pid+service+"-capacity"),
                "supply_redundancy": _pick(["single_feed","dual_feed","ring_fed","independent_backup"], pid+service+"-redundancy") if service == "electricity" else _pick(["single_feed","looped_distribution","dual_supply"], pid+service+"-redundancy"),
                "connection_state": "connected_and_available",
                "is_live_game_connection": True,
                "effective_from_tick": 0,
            })
            account_id = f"SWUACC-{_slug(pid)}-{service[:3].upper()}"
            accounts.append({
                "utility_account_id": account_id,
                "utility_connection_id": connection_id,
                "property_id": pid,
                "utility_type": service,
                "provider_organisation_id": provider_id,
                "account_holder_organisation_id": owner_id,
                "property_manager_organisation_id": manager_id,
                "account_scope": "property_master_account",
                "billing_responsibility_profile": _pick(["owner_master_account","managed_estate_account","tenant_recovery_account"], pid+service+"-billing"),
                "metering_basis": "master_meter_with_unit_submetering" if service in ("electricity","potable_water") else "property_master_meter",
                "account_status": "active",
                "financial_postings_created": 0,
            })
            meters.append({
                "meter_id": f"SWMTR-{_slug(pid)}-{service[:3].upper()}-M",
                "utility_account_id": account_id,
                "utility_connection_id": connection_id,
                "property_id": pid,
                "building_id": None,
                "unit_id": None,
                "utility_type": service,
                "meter_role": "property_master_meter",
                "meter_type": _pick(["smart_interval","remote_read","digital_cumulative"], pid+service+"-meter"),
                "serial_reference": f"SW-{service[:3].upper()}-{_slug(pid)}-0001",
                "read_frequency": "daily_interval" if service == "electricity" else "monthly_cumulative",
                "meter_state": "installed_and_active",
                "reading_value": None,
                "effective_from_tick": 0,
            })

    equipment_catalog = {
        "electrical_distribution": ["main_switchboard","distribution_board","protective_relay","earthing_and_bonding"],
        "potable_water_distribution": ["incoming_meter_set","booster_pump","storage_tank","backflow_prevention"],
        "wastewater_and_sanitary": ["soil_stack","waste_stack","sump_pump","grease_interceptor"],
        "heating_ventilation_and_cooling": ["air_handling_unit","chiller_or_heat_pump","extract_fan","zone_controller"],
        "fire_detection_and_suppression": ["fire_alarm_panel","smoke_detector_loop","sprinkler_control_valve","fire_pump_set"],
        "physical_security_and_access": ["access_control_panel","cctv_recorder","intruder_alarm_panel","door_controller"],
        "building_management_controls": ["building_management_controller","environmental_sensor","plant_monitor","remote_alarm_gateway"],
        "vertical_transport": ["passenger_lift","goods_lift","lift_controller","emergency_communication_unit"],
    }
    system_condition = ["good","fair","maintained","recently_refurbished","serviceable"]
    for bid in sorted(buildings):
        b = buildings[bid]
        pid = b["property_id"]
        use = b.get("building_use", "mixed_use")
        critical = use in {"port_maritime","warehouse","industrial","healthcare","transport","data_centre","financial"}
        active_types = list(system_types)
        if "passenger_lift" not in b.get("vertical_circulation", []) and "goods_lift" not in b.get("vertical_circulation", []):
            active_types.remove("vertical_transport")
        if b.get("heating_cooling") == "natural_ventilation":
            active_types.remove("heating_ventilation_and_cooling")
        for stype in active_types:
            sid = f"SWSYS-{_slug(bid)}-{_slug(stype)}"
            capacity = "critical" if critical else ("high" if b.get("storeys_above", 0) >= 4 else "standard")
            systems.append({
                "building_system_id": sid,
                "property_id": pid,
                "building_id": bid,
                "system_type": stype,
                "system_status": "operational",
                "condition": _pick(system_condition, bid+stype+"-condition"),
                "capacity_band": capacity,
                "redundancy_profile": _pick(["single_train","duty_standby","dual_train","distributed_resilience"], bid+stype+"-redundancy") if critical else _pick(["single_train","duty_standby"], bid+stype+"-redundancy"),
                "control_mode": _pick(["local_manual_and_automatic","central_building_management","staff_supervised"], bid+stype+"-control"),
                "inspection_cycle_days": _n(bid+stype+"-inspection", 30, 365),
                "last_inspection_year": _n(bid+stype+"-inspection-year", 2023, 2026),
                "next_inspection_due_tick": _n(bid+stype+"-due", 30, 365),
                "provider_organisation_id": PROVIDERS["electricity"][0] if stype == "electrical_distribution" else None,
                "effective_from_tick": 0,
            })
            catalog = equipment_catalog[stype]
            count = 3 if critical else 2
            if stype == "vertical_transport":
                count = max(1, len(b.get("vertical_circulation", [])))
            for seq in range(1, count + 1):
                kind = catalog[_n(bid+stype+str(seq), 0, len(catalog)-1)]
                equipment.append({
                    "equipment_id": f"SWEQP-{_slug(bid)}-{_slug(stype)}-{seq:02d}",
                    "building_system_id": sid,
                    "property_id": pid,
                    "building_id": bid,
                    "equipment_type": kind,
                    "equipment_reference": f"{_slug(bid)}-{_slug(stype)}-{seq:02d}",
                    "manufacturer_profile": _pick(["Saltwater Industrial Systems","Meridian Engineering","Harbour Technical Works","Civic Building Technologies","Northbank Controls"], bid+stype+str(seq)+"-maker"),
                    "installation_year": _n(bid+stype+str(seq)+"-install", 2008, 2025),
                    "condition": _pick(system_condition, bid+stype+str(seq)+"-condition"),
                    "operational_state": "in_service",
                    "maintenance_class": _pick(["planned_preventive","condition_based","statutory_inspection","critical_asset_monitoring"], bid+stype+str(seq)+"-maint"),
                    "replacement_priority": _pick(["routine","planned","elevated","critical"], bid+stype+str(seq)+"-priority"),
                })
            inspections.append({
                "inspection_id": f"SWINS-{_slug(bid)}-{_slug(stype)}",
                "building_system_id": sid,
                "property_id": pid,
                "building_id": bid,
                "inspection_type": "planned_system_condition_inspection",
                "inspection_interval_days": _n(bid+stype+"-interval", 90, 365),
                "last_completed_year": _n(bid+stype+"-last", 2023, 2026),
                "next_due_tick": _n(bid+stype+"-next", 30, 365),
                "inspection_status": "in_date",
                "result_profile": "serviceable_no_open_critical_defect",
            })

    for unit_id in sorted(units):
        unit = units[unit_id]
        pid = unit["property_id"]
        bid = unit["building_id"]
        for service, code in (("electricity","E"),("potable_water","W")):
            account_id = f"SWUACC-{_slug(pid)}-{service[:3].upper()}"
            meters.append({
                "meter_id": f"MTR-{_slug(unit_id)}-{code}",
                "utility_account_id": account_id,
                "utility_connection_id": f"SWUCON-{_slug(pid)}-{service[:3].upper()}",
                "property_id": pid,
                "building_id": bid,
                "unit_id": unit_id,
                "utility_type": service,
                "meter_role": "unit_submeter",
                "meter_type": "smart_submeter",
                "serial_reference": f"SW-SUB-{code}-{_slug(unit_id)}",
                "read_frequency": "daily_interval" if code == "E" else "monthly_cumulative",
                "meter_state": "installed_and_active",
                "reading_value": None,
                "effective_from_tick": 0,
            })
        occ = occupancies.get(unit_id)
        if occ:
            tenant_responsibilities.append({
                "service_responsibility_id": f"SWSRA-{_slug(unit_id)}",
                "property_id": pid,
                "building_id": bid,
                "premises_id": unit["premises_id"],
                "unit_id": unit_id,
                "occupancy_id": occ["occupancy_id"],
                "occupant_business_id": occ["occupant_business_id"],
                "utility_scope": ["electricity","potable_water"],
                "responsibility_profile": _pick(["tenant_direct","landlord_recovered","included_in_lease","shared_allocation"], unit_id+"-utility-responsibility"),
                "metering_basis": "dedicated_unit_submeters",
                "financial_postings_created": 0,
            })

    body = {
        "schema": "saltwater-building-services/1.0",
        "dataset_id": "SW-BUILDING-SERVICES-V1",
        "canon_status": "CANONICAL_FICTIONAL_GAME_WORLD",
        "generator": GENERATOR,
        "effective_tick": 0,
        "city": "Saltwater",
        "city_population_hard_cap": 10000,
        "summary": {
            "property_count": len(properties),
            "building_count": len(buildings),
            "utility_provider_count": len(providers),
            "utility_connection_count": len(connections),
            "utility_account_count": len(accounts),
            "meter_count": len(meters),
            "building_system_count": len(systems),
            "equipment_asset_count": len(equipment),
            "system_inspection_schedule_count": len(inspections),
            "business_utility_responsibility_count": len(tenant_responsibilities),
            "unit_count": len(units),
            "person_records_created": 0,
            "financial_postings_created": 0,
            "population_records_created": 0,
        },
        "utility_providers": providers,
        "utility_connections": connections,
        "utility_accounts": accounts,
        "meters": meters,
        "building_systems": systems,
        "equipment_assets": equipment,
        "system_inspections": inspections,
        "business_utility_responsibilities": tenant_responsibilities,
        "lineage": {
            "property_world_dataset": "SW-PROPERTY-WORLD-V1",
            "property_tenure_dataset": "SW-PROPERTY-TENURE-V1",
            "fictional_world_facts": True,
        },
        "gameplay": {
            "utilities": "Property connections, accounts, master meters and unit submeters are explicit and linked.",
            "building_operations": "Building systems and equipment have operational state, condition, redundancy and inspection schedules.",
            "business_occupancy": "Business utility responsibility follows current unit occupancy and lease links.",
            "finance_boundary": "No bills, payments, balances, rent, taxes or accounting entries are generated; BP-34 owns all financial postings.",
            "population": "No residents, employees, customers or other person records are generated.",
            "simulation_time": "All service and equipment records begin at simulation tick zero; future outages, readings and repairs are runtime events.",
        },
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    world_doc = load_json(root / "data/property/saltwater-property-world-v1.json")
    tenure_doc = json.loads((root / "data/property/saltwater-property-tenure-v1.json").read_text(encoding="utf-8"))
    world = _expand_columnar(world_doc)
    tenure = _expand_columnar(tenure_doc)
    result = build_building_services(world, tenure)
    output = root / "data/property/saltwater-building-services-v1.json"
    document = to_columnar_document(result)
    document["schema"] = "saltwater-building-services-columnar/1.0"
    output.write_text(json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"] | {
        "manifest_sha256": result["manifest_sha256"],
        "storage_format": document["storage_format"],
        "output_bytes": output.stat().st_size,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
