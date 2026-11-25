"""Load the phased Saltwater property/business/maintenance stack into disposable PostgreSQL.

The release includes property, business, tenure, building-services, maintenance, security, valuation, insurance and tax sources.
Production use is deliberately blocked. The command accepts only the disposable
saltwater_test database unless an explicit future implementation changes this
guard through reviewed code. It imports compressed columnar JSON losslessly.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

DATASETS = {
    "SW-PROPERTY-WORLD-V1": "data/property/saltwater-property-world-v1.json.gz",
    "SW-BUSINESS-REGISTRY-V1": "data/business/saltwater-business-registry-v1.json.gz",
    "SW-PROPERTY-TENURE-V1": "data/property/saltwater-property-tenure-v1.json.gz",
    "SW-BUILDING-SERVICES-V1": "data/property/saltwater-building-services-v1.json.gz",
    "SW-PROPERTY-MAINTENANCE-V1": "data/property/saltwater-property-maintenance-v1.json.gz",
    "SW-PROPERTY-SECURITY-ACCESS-V1": "data/property/saltwater-property-security-access-v1.json.gz",
    "SW-PROPERTY-VALUE-RISK-TAX-V1": "data/property/saltwater-property-value-risk-tax-v1.json.gz",
}

def read_document(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    payload = gzip.decompress(raw) if path.suffix == ".gz" else raw
    doc = json.loads(payload)
    if doc.get("storage_format") != "textual_json_columnar_v1":
        raise ValueError(f"Unsupported dataset storage format: {path}")
    if not isinstance(doc.get("metadata"), dict) or not isinstance(doc.get("tables"), dict):
        raise ValueError(f"Malformed columnar dataset: {path}")
    return doc, raw

def rows(doc: dict, name: str) -> list[dict]:
    table = doc["tables"].get(name)
    if table is None:
        return []
    columns, values = table.get("columns"), table.get("rows")
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"Malformed columnar collection: {name}")
    result = []
    for index, values_row in enumerate(values):
        if len(values_row) != len(columns):
            raise ValueError(f"{name}[{index}] has {len(values_row)} values for {len(columns)} columns")
        result.append(dict(zip(columns, values_row)))
    return result

def pick(row: dict, *keys: str, default=None):
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value
    return default

def text_value(value):
    if value is None:
        return None
    return str(value)

def numeric_value(value):
    if value is None or isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def boolean_value(value):
    if value is None or isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "t", "yes", "y", "1"}:
            return True
        if lowered in {"false", "f", "no", "n", "0"}:
            return False
    raise ValueError(f"Expected boolean-compatible source value, got {value!r}")

def record(table: str, source_dataset: str, row: dict, values: dict) -> tuple:
    values["source_dataset"] = source_dataset
    values["source_record"] = Jsonb(row)
    return table, values

def build_batches(documents: dict[str, dict]) -> tuple[dict[str, list[dict]], dict[str, int]]:
    batches: dict[str, list[dict]] = {}
    counts: dict[str, int] = {}

    def add(table: str, dataset: str, source_rows: list[dict], mapper):
        counts[f"{dataset}.{table}"] = len(source_rows)
        batches.setdefault(table, []).extend(mapper(dataset, row) for row in source_rows)

    def mapped(ds, row, columns, booleans=()):
        result = {column: row.get(column) for column in columns}
        for column in booleans:
            result[column] = boolean_value(row.get(column))
        result["source_dataset"] = ds
        return result

    world = documents["SW-PROPERTY-WORLD-V1"]
    registry = documents["SW-BUSINESS-REGISTRY-V1"]
    tenure = documents["SW-PROPERTY-TENURE-V1"]
    services = documents["SW-BUILDING-SERVICES-V1"]
    maintenance = documents["SW-PROPERTY-MAINTENANCE-V1"]
    security = documents["SW-PROPERTY-SECURITY-ACCESS-V1"]
    value_risk = documents["SW-PROPERTY-VALUE-RISK-TAX-V1"]

    # The tenure register is the superset: it already contains every property owner organisation plus historical owners and managers.
    add("organisation", "SW-PROPERTY-TENURE-V1", rows(tenure, "organisations"),
        lambda ds, r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"registered_city":r.get("registered_city"),"status":r.get("status"),"source_dataset":ds})

    add("property_site", "SW-PROPERTY-WORLD-V1", rows(world, "properties"),
        lambda ds,r: {"property_id":r["property_id"],"display_name":pick(r,"display_name","property_name","name",default=r["property_id"]),"district_id":pick(r,"district_id","source_district_id"),"neighbourhood_id":pick(r,"neighbourhood_id","source_neighbourhood_id"),"address_id":r.get("address_id"),"site_area_m2":numeric_value(pick(r,"site_area_m2","area_m2","area")),"use_class":pick(r,"primary_use","use_class","property_use"),"lifecycle_status":pick(r,"canonical_status","lifecycle_status","site_state"),"source_dataset":ds})
    add("street_address", "SW-PROPERTY-WORLD-V1", rows(world, "addresses"),
        lambda ds,r: {"address_id":r["address_id"],"property_id":r["property_id"],"display_name":pick(r,"address_label","display_name"),"road_id":r.get("road_id"),"house_number":text_value(pick(r,"street_number","house_number")),"postcode":r.get("postcode"),"source_dataset":ds})
    add("building", "SW-PROPERTY-WORLD-V1", rows(world, "buildings"),
        lambda ds,r: {"building_id":r["building_id"],"property_id":r["property_id"],"display_name":pick(r,"display_name","building_name","name",default=r["building_id"]),"building_use":pick(r,"building_use","primary_use","use_class"),"storeys":pick(r,"storeys_above","storeys","floors_above"),"gross_floor_area_m2":numeric_value(pick(r,"gross_floor_area_m2","floor_area_m2","gross_internal_area_m2")),"construction_year":r.get("construction_year"),"lifecycle_status":pick(r,"canonical_status","lifecycle_status"),"source_dataset":ds})
    add("premises", "SW-PROPERTY-WORLD-V1", rows(world, "premises"),
        lambda ds,r: {"premises_id":r["premises_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"display_name":pick(r,"display_name","premises_name","name",default=r["premises_id"]),"premises_use":pick(r,"premises_use","premises_type","use_class","primary_use"),"floor_name":pick(r,"floor_name","floor_code"),"lifecycle_status":pick(r,"canonical_status","lifecycle_status"),"source_dataset":ds})
    add("unit_space", "SW-PROPERTY-WORLD-V1", rows(world, "units"),
        lambda ds,r: {"unit_id":r["unit_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r["premises_id"],"display_name":pick(r,"display_name","unit_name","unit_locator","name",default=r["unit_id"]),"unit_class":r.get("unit_class"),"use_class":pick(r,"use_class","primary_use","unit_use"),"floor_order":r.get("floor_order"),"floor_area_m2":numeric_value(r.get("floor_area_m2")),"lifecycle_status":pick(r,"canonical_status","lifecycle_status"),"source_dataset":ds})
    add("access_point", "SW-PROPERTY-WORLD-V1", rows(world, "access_points"),
        lambda ds,r: {"access_point_id":r["access_point_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r.get("unit_id"),"display_name":pick(r,"display_name","access_point_name",default=r["access_point_id"]),"access_type":r.get("access_type"),"access_modes":r.get("access_modes"),"road_link_road_id":r.get("road_link_road_id"),"source_dataset":ds})
    add("access_route", "SW-PROPERTY-WORLD-V1", rows(world, "access_routes"),
        lambda ds,r: {"route_id":r["route_id"],"access_point_id":r["access_point_id"],"road_id":r.get("road_id"),"route_type":r.get("route_type"),"access_modes":[m for m,ok in (("vehicle",r.get("vehicle_access")),("pedestrian",r.get("pedestrian_access"))) if ok],"route_status":r.get("route_state"),"source_dataset":ds})
    add("site_feature", "SW-PROPERTY-WORLD-V1", rows(world, "site_features"),
        lambda ds,r: {"site_feature_id":r["site_feature_id"],"property_id":r["property_id"],"feature_type":r.get("feature_type"),"display_name":pick(r,"display_name","design_type","subtype",default=r["site_feature_id"]),"source_dataset":ds})
    add("building_component", "SW-PROPERTY-WORLD-V1", rows(world, "building_components"),
        lambda ds,r: {"component_id":r["component_id"],"building_id":r["building_id"],"component_type":r.get("component_type"),"display_name":pick(r,"display_name","material",default=r["component_id"]),"source_dataset":ds})
    add("premises_room", "SW-PROPERTY-WORLD-V1", rows(world, "premises_rooms"),
        lambda ds,r: {"room_id":r["room_id"],"premises_id":r["premises_id"],"display_name":pick(r,"room_name","display_name","room_code",default=r["room_id"]),"room_type":r.get("room_type"),"floor_name":pick(r,"floor_name","floor_level"),"source_dataset":ds})
    add("ownership_interest", "SW-PROPERTY-WORLD-V1", rows(world, "ownership_interests"),
        lambda ds,r: {"ownership_interest_id":r["ownership_interest_id"],"property_id":r["property_id"],"owner_organisation_id":r["owner_organisation_id"],"management_model":r.get("management_model"),"interest_type":r.get("interest_type"),"source_dataset":ds})

    add("business", "SW-BUSINESS-REGISTRY-V1", rows(registry, "businesses"),
        lambda ds,r: {"business_id":r["business_id"],"display_name":pick(r,"registered_name","trading_name","display_name","business_name","name",default=r["business_id"]),"sector":pick(r,"sector","business_sector",default="unclassified"),"primary_activity":pick(r,"primary_activity","activity"),"status":r.get("status","active"),"parent_business_id":r.get("parent_business_id"),"primary_establishment_id":r.get("primary_establishment_id"),"source_dataset":ds})
    add("establishment", "SW-BUSINESS-REGISTRY-V1", rows(registry, "establishments"),
        lambda ds,r: {"establishment_id":r["establishment_id"],"business_id":r["business_id"],"property_id":r.get("property_id"),"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r.get("unit_id"),"display_name":pick(r,"establishment_name","display_name","name",default=r["establishment_id"]),"establishment_type":r.get("establishment_type"),"status":pick(r,"operating_status","status"),"source_dataset":ds})
    add("business_unit_link", "SW-BUSINESS-REGISTRY-V1", rows(registry, "business_unit_links"),
        lambda ds,r: {"business_unit_link_id":r["business_unit_link_id"],"business_id":r["business_id"],"establishment_id":r["establishment_id"],"unit_id":r["unit_id"],"premises_id":r["premises_id"],"valid_from_tick":r.get("valid_from_tick",0),"valid_to_tick":r.get("valid_to_tick"),"occupancy_relationship":r.get("occupancy_relationship"),"occupancy_status":r.get("occupancy_status"),"source_dataset":ds})

    add("occupancy_agreement", "SW-PROPERTY-TENURE-V1", rows(tenure, "agreements"),
        lambda ds,r: {"agreement_id":r["agreement_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r["unit_id"],"landlord_organisation_id":r.get("landlord_organisation_id"),"tenant_business_id":r.get("tenant_business_id"),"operator_business_id":r.get("operator_business_id"),"establishment_id":r.get("establishment_id"),"agreement_type":r["agreement_type"],"commencement_year":r.get("commencement_year"),"expiry_year":r.get("expiry_year"),"agreement_status":r["agreement_status"],"source_dataset":ds})
    add("occupancy", "SW-PROPERTY-TENURE-V1", rows(tenure, "occupancies"),
        lambda ds,r: {"occupancy_id":r["occupancy_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r["unit_id"],"occupant_business_id":r.get("occupant_business_id"),"establishment_id":r.get("establishment_id"),"agreement_id":r.get("agreement_id"),"occupant_type":r["occupant_type"],"occupancy_status":r["occupancy_status"],"effective_from_year":r.get("effective_from_year"),"effective_to_year":r.get("effective_to_year"),"source_dataset":ds})

    # Utility providers extend the canonical organisation registry; do not assume
    # every service provider was already present in the property-tenure register.
    add("organisation", "SW-BUILDING-SERVICES-V1", rows(services, "utility_providers"),
        lambda ds,r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"registered_city":r.get("registered_city"),"status":r.get("status"),"source_dataset":ds})

    # Phase 2: typed building systems and utility/service relationships.
    add("building_system", "SW-BUILDING-SERVICES-V1", rows(services, "building_systems"),
        lambda ds,r: {"building_system_id":r["building_system_id"],"property_id":r["property_id"],"building_id":r["building_id"],"system_type":r["system_type"],"system_status":r.get("system_status"),"condition":r.get("condition"),"capacity_band":r.get("capacity_band"),"redundancy_profile":r.get("redundancy_profile"),"control_mode":r.get("control_mode"),"inspection_cycle_days":r.get("inspection_cycle_days"),"last_inspection_year":r.get("last_inspection_year"),"next_inspection_due_tick":r.get("next_inspection_due_tick"),"provider_organisation_id":r.get("provider_organisation_id"),"effective_from_tick":r.get("effective_from_tick"),"source_dataset":ds})
    add("business_utility_responsibility", "SW-BUILDING-SERVICES-V1", rows(services, "business_utility_responsibilities"),
        lambda ds,r: {"service_responsibility_id":r["service_responsibility_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r.get("unit_id"),"occupancy_id":r.get("occupancy_id"),"occupant_business_id":r.get("occupant_business_id"),"utility_scope":r["utility_scope"],"responsibility_profile":r.get("responsibility_profile"),"metering_basis":r.get("metering_basis"),"financial_postings_created":boolean_value(r["financial_postings_created"]),"source_dataset":ds})
    add("equipment_asset", "SW-BUILDING-SERVICES-V1", rows(services, "equipment_assets"),
        lambda ds,r: {"equipment_id":r["equipment_id"],"building_system_id":r["building_system_id"],"property_id":r["property_id"],"building_id":r["building_id"],"equipment_type":r["equipment_type"],"equipment_reference":r.get("equipment_reference"),"manufacturer_profile":r.get("manufacturer_profile"),"installation_year":r.get("installation_year"),"condition":r.get("condition"),"operational_state":r.get("operational_state"),"maintenance_class":r.get("maintenance_class"),"replacement_priority":r.get("replacement_priority"),"source_dataset":ds})
    add("meter", "SW-BUILDING-SERVICES-V1", rows(services, "meters"),
        lambda ds,r: {"meter_id":r["meter_id"],"utility_account_id":r["utility_account_id"],"utility_connection_id":r["utility_connection_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"unit_id":r.get("unit_id"),"utility_type":r["utility_type"],"meter_role":r.get("meter_role"),"meter_type":r.get("meter_type"),"serial_reference":r.get("serial_reference"),"read_frequency":r.get("read_frequency"),"meter_state":r.get("meter_state"),"reading_value":numeric_value(r.get("reading_value")),"effective_from_tick":r.get("effective_from_tick"),"source_dataset":ds})
    add("system_inspection", "SW-BUILDING-SERVICES-V1", rows(services, "system_inspections"),
        lambda ds,r: {"inspection_id":r["inspection_id"],"building_system_id":r["building_system_id"],"property_id":r["property_id"],"building_id":r["building_id"],"inspection_type":r["inspection_type"],"inspection_interval_days":r.get("inspection_interval_days"),"last_completed_year":r.get("last_completed_year"),"next_due_tick":r.get("next_due_tick"),"inspection_status":r.get("inspection_status"),"result_profile":r.get("result_profile"),"source_dataset":ds})
    add("utility_account", "SW-BUILDING-SERVICES-V1", rows(services, "utility_accounts"),
        lambda ds,r: {"utility_account_id":r["utility_account_id"],"utility_connection_id":r["utility_connection_id"],"property_id":r["property_id"],"utility_type":r["utility_type"],"provider_organisation_id":r.get("provider_organisation_id"),"account_holder_organisation_id":r.get("account_holder_organisation_id"),"property_manager_organisation_id":r.get("property_manager_organisation_id"),"account_scope":r.get("account_scope"),"billing_responsibility_profile":r.get("billing_responsibility_profile"),"metering_basis":r.get("metering_basis"),"account_status":r.get("account_status"),"financial_postings_created":boolean_value(r["financial_postings_created"]),"source_dataset":ds})
    add("utility_connection", "SW-BUILDING-SERVICES-V1", rows(services, "utility_connections"),
        lambda ds,r: {"utility_connection_id":r["utility_connection_id"],"property_id":r["property_id"],"primary_building_id":r.get("primary_building_id"),"utility_type":r["utility_type"],"provider_organisation_id":r.get("provider_organisation_id"),"connection_point_type":r.get("connection_point_type"),"connection_capacity_band":r.get("connection_capacity_band"),"supply_redundancy":r.get("supply_redundancy"),"connection_state":r.get("connection_state"),"is_live_game_connection":boolean_value(r["is_live_game_connection"]),"effective_from_tick":r.get("effective_from_tick"),"source_dataset":ds})
    add("utility_provider_profile", "SW-BUILDING-SERVICES-V1", rows(services, "utility_providers"),
        lambda ds,r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"registered_city":r.get("registered_city"),"status":r.get("status"),"fictional_entity":boolean_value(r["fictional_entity"]),"service_area":r.get("service_area"),"source_dataset":ds})
    # Phase 3: maintenance, defects, repairs and equipment lifecycle.
    # Contractor organisations extend the canonical organisation registry.
    add("organisation", "SW-PROPERTY-MAINTENANCE-V1", rows(maintenance, "maintenance_contractors"),
        lambda ds,r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"registered_city":None,"status":r.get("status"),"source_dataset":ds})
    maintenance_maps = [
      ("maintenance_contractor_profile","maintenance_contractors",["organisation_id","specialisms","status","fictional_entity"],["fictional_entity"]),
      ("maintenance_plan","maintenance_plans",["maintenance_plan_id","property_id","building_id","responsible_organisation_id","plan_type","plan_status","review_interval_days","risk_profile","effective_tick"],[]),
      ("maintenance_cycle","maintenance_cycles",["maintenance_cycle_id","maintenance_plan_id","property_id","building_id","cycle_type","interval_days","next_due_tick","priority"],[]),
      ("maintenance_inspection","inspections",["inspection_id","property_id","building_id","building_system_id","inspection_type","inspection_scope","interval_days","last_completed_tick","next_due_tick","inspection_status","responsible_organisation_id","result"],[]),
      ("maintenance_defect","defects",["defect_id","property_id","building_id","building_system_id","equipment_id","defect_location_type","severity","defect_category","discovery_source","discovered_tick","defect_status","operational_impact","safety_implication","root_cause_profile","repair_urgency","temporary_control","raised_work_request_id"],[]),
      ("maintenance_work_request","work_requests",["work_request_id","property_id","building_id","building_system_id","equipment_id","defect_id","request_type","priority","requested_tick","request_status","raised_by_organisation_id","responsible_organisation_id","description_code"],[]),
      ("maintenance_work_order","work_orders",["work_order_id","work_request_id","property_id","building_id","building_system_id","equipment_id","defect_id","maintenance_plan_id","work_type","priority","work_order_status","responsible_contractor_organisation_id","managing_organisation_id","required_trade","estimated_duration_hours_band","labour_costing","scheduled_tick","completion_tick","verification_required"],["verification_required"]),
      ("maintenance_work_order_line","work_order_lines",["work_order_line_id","work_order_id","line_type","asset_id","description_code","quantity_band","trade"],[]),
      ("maintenance_material_issue","material_issues",["material_issue_id","work_order_id","equipment_id","material_class","quantity_band","stock_source_profile","financial_posting_created"],["financial_posting_created"]),
      ("maintenance_event","maintenance_events",["maintenance_event_id","work_order_id","equipment_id","property_id","building_id","event_type","event_tick","event_status","verification_state"],[]),
      ("equipment_warranty","warranties",["warranty_id","equipment_id","property_id","building_id","warranty_provider_profile","start_year","end_year","warranty_state","terms_profile"],[]),
      ("equipment_replacement_forecast","replacement_forecasts",["replacement_plan_id","equipment_id","property_id","building_id","building_system_id","replacement_reason","target_year","priority","capital_approval_state","financial_commitment_created"],["financial_commitment_created"]),
      ("building_emergency_procedure","emergency_procedures",["procedure_id","property_id","building_id","procedure_scope","scenarios","first_response_organisation_id","continuity_arrangements","person_records_created"],[])
    ]
    for target, source, columns, booleans in maintenance_maps:
        add(target, "SW-PROPERTY-MAINTENANCE-V1", rows(maintenance, source),
            lambda ds,r,cols=columns,flags=booleans: mapped(ds,r,cols,flags))
    # Phase 4: physical security, key control and organisation-level access.
    add("security_door", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "doors"),
        lambda ds,r: {"door_id":r["door_id"],"access_point_id":r["access_point_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"door_role":r.get("door_role"),"door_type":r.get("door_type"),"clear_width_m":numeric_value(r.get("clear_width_m")),"opening_direction_profile":r.get("opening_direction_profile"),"fire_or_smoke_rating_profile":r.get("fire_or_smoke_rating_profile"),"egress_hardware":r.get("egress_hardware"),"door_state":r.get("door_state"),"route_id":r.get("route_id"),"maintenance_dataset":r.get("maintenance_dataset"),"source_dataset":ds})
    add("security_lock", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "locks"),
        lambda ds,r: {"lock_id":r["lock_id"],"door_id":r["door_id"],"access_point_id":r["access_point_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"lock_type":r.get("lock_type"),"security_grade":r.get("security_grade"),"outside_entry_control":r.get("outside_entry_control"),"inside_egress":r.get("inside_egress"),"fail_state":r.get("fail_state"),"monitoring_state":r.get("monitoring_state"),"lock_state":r.get("lock_state"),"source_dataset":ds})
    add("key_cylinder", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "key_cylinders"),
        lambda ds,r: {"cylinder_id":r["cylinder_id"],"lock_id":r["lock_id"],"keyway_profile":r.get("keyway_profile"),"key_control_class":r.get("key_control_class"),"master_keyed":boolean_value(r.get("master_keyed")),"key_copy_control":r.get("key_copy_control"),"source_dataset":ds})
    add("physical_key", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "physical_keys"),
        lambda ds,r: {"key_id":r["key_id"],"cylinder_id":r["cylinder_id"],"property_id":r["property_id"],"key_class":r.get("key_class"),"key_status":r.get("key_status"),"issue_to_person_id":r.get("issue_to_person_id"),"issue_to_organisation_id":r.get("issue_to_organisation_id"),"duplicate_control":r.get("duplicate_control"),"source_dataset":ds})
    add("security_device", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "security_devices"),
        lambda ds,r: {"security_device_id":r["security_device_id"],"device_type":r.get("device_type"),"access_point_id":r["access_point_id"],"door_id":r["door_id"],"lock_id":r["lock_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"device_state":r.get("device_state"),"power_backup_profile":r.get("power_backup_profile"),"network_path":r.get("network_path"),"tamper_monitoring":boolean_value(r.get("tamper_monitoring")),"source_dataset":ds})
    add("access_zone", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "access_zones"),
        lambda ds,r: {"access_zone_id":r["access_zone_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r.get("unit_id"),"zone_type":r["zone_type"],"security_level":r.get("security_level"),"zone_state":r.get("zone_state"),"parent_zone_id":r.get("parent_zone_id"),"source_dataset":ds})
    add("access_group", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "access_groups"),
        lambda ds,r: {"access_group_id":r["access_group_id"],"group_type":r["group_type"],"property_id":r["property_id"],"building_id":r.get("building_id"),"premises_id":r.get("premises_id"),"unit_id":r["unit_id"],"business_id":r.get("business_id"),"occupancy_id":r.get("occupancy_id"),"group_status":r.get("group_status"),"member_person_ids":r.get("member_person_ids",[]),"credential_issue_mode":r.get("credential_issue_mode"),"source_dataset":ds})
    permission_rows=rows(security,"permission_sets")
    add("permission_set", "SW-PROPERTY-SECURITY-ACCESS-V1", permission_rows,
        lambda ds,r: {"permission_set_id":r["permission_set_id"],"access_group_id":r["access_group_id"],"permission_scope":r.get("permission_scope"),"schedule_profile":r.get("schedule_profile"),"privileges":r.get("privileges",[]),"prohibited_privileges":r.get("prohibited_privileges",[]),"effective_from_tick":r.get("effective_from_tick"),"revocable":boolean_value(r.get("revocable")),"source_dataset":ds})
    grant_rows=[]
    for row in permission_rows:
        for index, zone_id in enumerate(row.get("permitted_zone_ids",[]),1):
            grant_rows.append({"grant_id":"SWPZG-"+hashlib.sha256((row["permission_set_id"]+"|"+zone_id).encode()).hexdigest()[:24].upper(),"permission_set_id":row["permission_set_id"],"access_zone_id":zone_id,"grant_order":index,"source_dataset":"SW-PROPERTY-SECURITY-ACCESS-V1"})
    counts["SW-PROPERTY-SECURITY-ACCESS-V1.permission_zone_grant"]=len(grant_rows)
    batches.setdefault("permission_zone_grant",[]).extend(grant_rows)
    add("organisation_access_assignment", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "organisation_access_assignments"),
        lambda ds,r: {"access_assignment_id":r["access_assignment_id"],"access_group_id":r["access_group_id"],"business_id":r.get("business_id"),"occupancy_id":r.get("occupancy_id"),"permission_set_id":r["permission_set_id"],"assignment_basis":r.get("assignment_basis"),"assignment_status":r.get("assignment_status"),"person_credentials_created":r.get("person_credentials_created",0),"source_dataset":ds})
    add("key_cabinet", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "key_cabinets"),
        lambda ds,r: {"key_cabinet_id":r["key_cabinet_id"],"property_id":r["property_id"],"managing_organisation_id":r["managing_organisation_id"],"cabinet_type":r.get("cabinet_type"),"access_control":r.get("access_control"),"key_inventory_count":r.get("key_inventory_count"),"issue_register_required":boolean_value(r.get("issue_register_required")),"audit_interval_days":r.get("audit_interval_days"),"person_records_created":r.get("person_records_created",0),"source_dataset":ds})
    add("access_policy", "SW-PROPERTY-SECURITY-ACCESS-V1", rows(security, "access_policies"),
        lambda ds,r: {"access_policy_id":r["access_policy_id"],"access_point_id":r.get("access_point_id"),"door_id":r.get("door_id"),"property_id":r["property_id"],"building_id":r.get("building_id"),"policy_scope":r.get("policy_scope"),"schedule_profile":r.get("schedule_profile"),"emergency_override":r.get("emergency_override"),"anti_passback":r.get("anti_passback"),"tailgating_control":r.get("tailgating_control"),"visitor_management":r.get("visitor_management"),"contractor_access":r.get("contractor_access"),"lost_credential_response":r.get("lost_credential_response"),"emergency_services":r.get("emergency_services"),"source_dataset":ds})
    # Phase 5: condition, valuation, insurance exposure and property tax.
    add("organisation", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "insurer_organisations"),
        lambda ds,r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"registered_city":None,"status":r.get("status"),"source_dataset":ds})
    add("insurer_profile", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "insurer_organisations"),
        lambda ds,r: {"organisation_id":r["organisation_id"],"display_name":r["display_name"],"organisation_type":r["organisation_type"],"status":r.get("status"),"fictional_entity":boolean_value(r.get("fictional_entity")),"source_dataset":ds})
    add("property_condition_assessment", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "condition_assessments"),
        lambda ds,r: {"condition_assessment_id":r["condition_assessment_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"assessment_scope":r.get("assessment_scope"),"condition_grade":r["condition_grade"],"observed_risk_profiles":r.get("observed_risk_profiles"),"gross_floor_area_sqm":numeric_value(r.get("gross_floor_area_sqm")),"system_count":r.get("system_count"),"open_defect_count":r.get("open_defect_count"),"critical_defect_count":r.get("critical_defect_count"),"assessment_tick":r.get("assessment_tick"),"evidence_basis":r.get("evidence_basis"),"follow_up_required":boolean_value(r.get("follow_up_required")),"source_dataset":ds})
    add("land_valuation", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "land_valuations"),
        lambda ds,r: {"land_valuation_id":r["land_valuation_id"],"property_id":r["property_id"],"valuation_basis":r.get("valuation_basis"),"land_use_profile":r.get("land_use_profile"),"site_area_sqm":numeric_value(r.get("site_area_sqm")),"rate_per_sqm_swc":r.get("rate_per_sqm_swc"),"assessed_land_value_swc":r["assessed_land_value_swc"],"valuation_tick":r.get("valuation_tick"),"valuation_status":r.get("valuation_status"),"source_dataset":ds})
    add("improvement_valuation", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "improvement_valuations"),
        lambda ds,r: {"improvement_valuation_id":r["improvement_valuation_id"],"property_id":r["property_id"],"building_id":r["building_id"],"building_use":r.get("building_use"),"gross_floor_area_sqm":numeric_value(r.get("gross_floor_area_sqm")),"construction_quality_profile":r.get("construction_quality_profile"),"replacement_value_swc":r["replacement_value_swc"],"depreciation_profile":r.get("depreciation_profile"),"valuation_tick":r.get("valuation_tick"),"source_dataset":ds})
    add("asset_valuation", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "asset_valuations"),
        lambda ds,r: {"asset_valuation_id":r["asset_valuation_id"],"property_id":r["property_id"],"building_id":r.get("building_id"),"land_valuation_id":r["land_valuation_id"],"improvement_valuation_id":r.get("improvement_valuation_id"),"valuation_purpose":r.get("valuation_purpose"),"currency":r["currency"],"assessed_value_swc":r["assessed_value_swc"],"value_band":r.get("value_band"),"valuation_method":r.get("valuation_method"),"valuation_tick":r.get("valuation_tick"),"valuation_status":r.get("valuation_status"),"source_dataset":ds})
    add("premises_valuation", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "premises_valuations"),
        lambda ds,r: {"premises_valuation_id":r["premises_valuation_id"],"property_id":r["property_id"],"building_id":r["building_id"],"premises_id":r["premises_id"],"valuation_basis":r.get("valuation_basis"),"assessed_value_swc":r["assessed_value_swc"],"value_band":r.get("value_band"),"valuation_tick":r.get("valuation_tick"),"source_dataset":ds})
    add("insurance_policy", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "insurance_policies"),
        lambda ds,r: {"insurance_policy_id":r["insurance_policy_id"],"property_id":r["property_id"],"policyholder_organisation_id":r["policyholder_organisation_id"],"insured_property_manager_organisation_id":r["insured_property_manager_organisation_id"],"insurer_organisation_id":r["insurer_organisation_id"],"policy_type":r.get("policy_type"),"policy_status":r.get("policy_status"),"effective_tick":r.get("effective_tick"),"renewal_interval_days":r.get("renewal_interval_days"),"currency":r.get("currency"),"sum_insured_swc":r["sum_insured_swc"],"deductible_band":r.get("deductible_band"),"premium_calculation":r.get("premium_calculation"),"claim_history":r.get("claim_history"),"source_dataset":ds})
    add("insurance_coverage", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "insurance_coverages"),
        lambda ds,r: {"coverage_id":r["coverage_id"],"insurance_policy_id":r["insurance_policy_id"],"coverage_type":r.get("coverage_type"),"limit_swc":r["limit_swc"],"coverage_state":r.get("coverage_state"),"source_dataset":ds})
    add("property_risk", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "property_risks"),
        lambda ds,r: {"property_risk_id":r["property_risk_id"],"property_id":r["property_id"],"insurance_policy_id":r["insurance_policy_id"],"risk_profile":r.get("risk_profile"),"risk_factors":r.get("risk_factors"),"mitigation_links":r.get("mitigation_links"),"risk_review_interval_days":r.get("risk_review_interval_days"),"review_status":r.get("review_status"),"source_dataset":ds})
    add("property_tax_assessment", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "property_tax_assessments"),
        lambda ds,r: {"property_tax_assessment_id":r["property_tax_assessment_id"],"property_id":r["property_id"],"liable_organisation_id":r["liable_organisation_id"],"tax_year":r["tax_year"],"tax_base_swc":r["tax_base_swc"],"tax_rate_basis_points":r["tax_rate_basis_points"],"assessed_annual_tax_swc":r["assessed_annual_tax_swc"],"assessment_status":r["assessment_status"],"appeal_status":r.get("appeal_status"),"assessment_tick":r.get("assessment_tick"),"currency":r["currency"],"source_dataset":ds})
    add("tax_exemption_review", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "tax_exemption_reviews"),
        lambda ds,r: {"tax_exemption_review_id":r["tax_exemption_review_id"],"property_id":r["property_id"],"review_state":r.get("review_state"),"exemption_reason":r.get("exemption_reason"),"effective_tax_year":r.get("effective_tax_year"),"source_dataset":ds})
    add("property_tax_rule", "SW-PROPERTY-VALUE-RISK-TAX-V1", rows(value_risk, "tax_rules"),
        lambda ds,r: {"tax_rule_id":r["tax_rule_id"],"tax_year":r["tax_year"],"rule_type":r.get("rule_type"),"currency":r["currency"],"collection_cycle":r.get("collection_cycle"),"billing_and_payment_authority":r.get("billing_and_payment_authority"),"effective_tick":r.get("effective_tick"),"fictional_rule":boolean_value(r.get("fictional_rule")),"source_dataset":ds})
    return batches, counts

def import_package(root: Path, dsn: str, expected_database: str = "saltwater_test") -> dict:
    with psycopg.connect(dsn) as conn:
        dbname = conn.execute("select current_database()").fetchone()[0]
        if dbname != expected_database:
            raise RuntimeError(f"Refusing non-disposable database {dbname!r}; expected {expected_database!r}")
        documents, manifest_files, archive_payloads = {}, {}, {}
        for dataset_id, relative in DATASETS.items():
            path = root / relative
            doc, raw = read_document(path)
            if doc["metadata"].get("dataset_id") != dataset_id:
                raise ValueError(f"Dataset ID mismatch in {relative}")
            documents[dataset_id] = doc
            archive_payloads[dataset_id] = raw
            manifest_files[dataset_id] = {
                "source_path": relative, "source_sha256": hashlib.sha256(raw).hexdigest(),
                "compressed_bytes": len(raw), "uncompressed_bytes": len(gzip.decompress(raw)),
            }
        batches, source_counts = build_batches(documents)
        package_sha = hashlib.sha256(json.dumps(manifest_files,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        commit = os.environ.get("GITHUB_SHA", "local-unpinned")
        release_id = "SWREL-" + hashlib.sha256((commit + package_sha).encode()).hexdigest()[:20].upper()
        manifest = {"release_id":release_id,"source_commit":commit,"package_sha256":package_sha,"files":manifest_files,"source_collection_counts":source_counts}
        with conn.transaction():
            conn.execute("SET CONSTRAINTS ALL DEFERRED")
            conn.execute("""INSERT INTO sw_property.import_release AS current(release_id,source_commit,package_sha256,manifest)
                VALUES (%s,%s,%s,%s) ON CONFLICT(release_id) DO UPDATE SET
                source_commit=excluded.source_commit, package_sha256=excluded.package_sha256, manifest=excluded.manifest
                WHERE current.source_commit IS DISTINCT FROM excluded.source_commit
                   OR current.package_sha256 IS DISTINCT FROM excluded.package_sha256
                   OR current.manifest IS DISTINCT FROM excluded.manifest""",
                (release_id,commit,package_sha,Jsonb(manifest)))
            for dataset_id, info in manifest_files.items():
                payload = archive_payloads[dataset_id]
                conn.execute("""INSERT INTO sw_property.source_dataset_archive
                    (source_sha256,dataset_id,source_path,compressed_bytes,uncompressed_bytes,compressed_payload)
                    VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT(source_sha256) DO NOTHING""",
                    (info["source_sha256"],dataset_id,info["source_path"],info["compressed_bytes"],info["uncompressed_bytes"],payload))
                collection_count = sum(v for k,v in source_counts.items() if k.startswith(dataset_id+"."))
                conn.execute("""INSERT INTO sw_property.import_dataset AS current
                    (release_id,dataset_id,source_path,source_sha256,compressed_bytes,uncompressed_bytes,source_record_count,loaded_record_count)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT(release_id,dataset_id) DO UPDATE SET source_path=excluded.source_path,
                    source_sha256=excluded.source_sha256,compressed_bytes=excluded.compressed_bytes,
                    uncompressed_bytes=excluded.uncompressed_bytes,source_record_count=excluded.source_record_count,
                    loaded_record_count=excluded.loaded_record_count
                    WHERE current.source_sha256 IS DISTINCT FROM excluded.source_sha256
                       OR current.source_path IS DISTINCT FROM excluded.source_path
                       OR current.compressed_bytes IS DISTINCT FROM excluded.compressed_bytes
                       OR current.uncompressed_bytes IS DISTINCT FROM excluded.uncompressed_bytes
                       OR current.source_record_count IS DISTINCT FROM excluded.source_record_count
                       OR current.loaded_record_count IS DISTINCT FROM excluded.loaded_record_count""",
                    (release_id,dataset_id,info["source_path"],info["source_sha256"],info["compressed_bytes"],info["uncompressed_bytes"],collection_count,collection_count))
            table_order = ["organisation","property_site","street_address","building","premises","unit_space","access_point","access_route","site_feature","building_component","premises_room","ownership_interest","business","establishment","business_unit_link","occupancy_agreement","occupancy","building_system","utility_connection","utility_provider_profile","utility_account","meter","equipment_asset","system_inspection","business_utility_responsibility","maintenance_contractor_profile","maintenance_plan","maintenance_cycle","maintenance_inspection","maintenance_defect","maintenance_work_request","maintenance_work_order","maintenance_work_order_line","maintenance_material_issue","maintenance_event","equipment_warranty","equipment_replacement_forecast","building_emergency_procedure","security_door","security_lock","key_cylinder","physical_key","security_device","access_zone","access_group","permission_set","permission_zone_grant","organisation_access_assignment","key_cabinet","access_policy","insurer_profile","property_condition_assessment","land_valuation","improvement_valuation","asset_valuation","premises_valuation","insurance_policy","insurance_coverage","property_risk","property_tax_assessment","tax_exemption_review","property_tax_rule"]
            for table in table_order:
                entries = batches.get(table, [])
                if not entries:
                    continue
                columns = list(entries[0].keys())
                if any(list(entry.keys()) != columns for entry in entries):
                    raise ValueError(f"Inconsistent mapped columns for {table}")
                placeholders = ",".join(["%s"] * len(columns))
                col_sql = ",".join(f'"{c}"' for c in columns)
                updates = ",".join(f'"{c}"=excluded."{c}"' for c in columns if c not in {"organisation_id","property_id","address_id","building_id","premises_id","unit_id","access_point_id","route_id","site_feature_id","component_id","room_id","ownership_interest_id","business_id","establishment_id","business_unit_link_id","agreement_id","occupancy_id","building_system_id","utility_connection_id","organisation_id","utility_account_id","meter_id","equipment_id","inspection_id","service_responsibility_id","maintenance_contractor_profile_id","maintenance_plan_id","maintenance_cycle_id","inspection_id","defect_id","work_request_id","work_order_id","work_order_line_id","material_issue_id","maintenance_event_id","warranty_id","replacement_plan_id","procedure_id","door_id","lock_id","cylinder_id","key_id","security_device_id","access_zone_id","access_group_id","permission_set_id","grant_id","access_assignment_id","key_cabinet_id","access_policy_id","condition_assessment_id","land_valuation_id","improvement_valuation_id","asset_valuation_id","premises_valuation_id","insurance_policy_id","coverage_id","property_risk_id","tax_exemption_review_id","tax_rule_id"})
                pk = {
                    "organisation":"organisation_id","property_site":"property_id","street_address":"address_id","building":"building_id","premises":"premises_id","unit_space":"unit_id","access_point":"access_point_id","access_route":"route_id","site_feature":"site_feature_id","building_component":"component_id","premises_room":"room_id","ownership_interest":"ownership_interest_id","business":"business_id","establishment":"establishment_id","business_unit_link":"business_unit_link_id","occupancy_agreement":"agreement_id","occupancy":"occupancy_id","building_system":"building_system_id","utility_connection":"utility_connection_id","utility_provider_profile":"organisation_id","utility_account":"utility_account_id","meter":"meter_id","equipment_asset":"equipment_id","system_inspection":"inspection_id","business_utility_responsibility":"service_responsibility_id", "maintenance_contractor_profile":"organisation_id","maintenance_plan":"maintenance_plan_id","maintenance_cycle":"maintenance_cycle_id","maintenance_inspection":"inspection_id","maintenance_defect":"defect_id","maintenance_work_request":"work_request_id","maintenance_work_order":"work_order_id","maintenance_work_order_line":"work_order_line_id","maintenance_material_issue":"material_issue_id","maintenance_event":"maintenance_event_id","equipment_warranty":"warranty_id","equipment_replacement_forecast":"replacement_plan_id","building_emergency_procedure":"procedure_id", "security_door":"door_id","security_lock":"lock_id","key_cylinder":"cylinder_id","physical_key":"key_id","security_device":"security_device_id","access_zone":"access_zone_id","access_group":"access_group_id","permission_set":"permission_set_id","permission_zone_grant":"grant_id","organisation_access_assignment":"access_assignment_id","key_cabinet":"key_cabinet_id","access_policy":"access_policy_id", "insurer_profile":"organisation_id","property_condition_assessment":"condition_assessment_id","land_valuation":"land_valuation_id","improvement_valuation":"improvement_valuation_id","asset_valuation":"asset_valuation_id","premises_valuation":"premises_valuation_id","insurance_policy":"insurance_policy_id","insurance_coverage":"coverage_id","property_risk":"property_risk_id","property_tax_assessment":"property_tax_assessment_id","tax_exemption_review":"tax_exemption_review_id","property_tax_rule":"tax_rule_id"
                }[table]
                compare_current = ",".join(f'current."{column}"' for column in columns if column != pk)
                compare_excluded = ",".join(f'excluded."{column}"' for column in columns if column != pk)
                predicate = f"({compare_current}) IS DISTINCT FROM ({compare_excluded})"
                action = f"DO UPDATE SET {updates} WHERE {predicate}" if updates else "DO NOTHING"
                sql = f'INSERT INTO sw_property."{table}" AS current ({col_sql}) VALUES ({placeholders}) ON CONFLICT ("{pk}") {action}'
                values = [tuple(entry[c] for c in columns) for entry in entries]
                with conn.cursor() as cur:
                    cur.executemany(sql, values)

            expected = {table:len(entries) for table,entries in batches.items()}
            expected["organisation"] = len({entry["organisation_id"] for entry in batches.get("organisation", [])})
            actual = {}
            for table, count in expected.items():
                actual[table] = conn.execute(f'SELECT count(*) FROM sw_property."{table}"').fetchone()[0]
                if actual[table] != count:
                    raise RuntimeError(f"{table}: expected {count} imported rows, database contains {actual[table]}")
            # Verify all FK relationships now, before transaction commit.
            fk_violations = conn.execute("""
                SELECT count(*) FROM (
                  SELECT u.unit_id FROM sw_property.unit_space u
                  LEFT JOIN sw_property.premises p ON p.premises_id=u.premises_id
                  LEFT JOIN sw_property.building b ON b.building_id=u.building_id
                  LEFT JOIN sw_property.property_site s ON s.property_id=u.property_id
                  WHERE p.premises_id IS NULL OR s.property_id IS NULL OR (u.building_id IS NOT NULL AND b.building_id IS NULL)
                  UNION ALL
                  SELECT e.establishment_id FROM sw_property.establishment e
                  LEFT JOIN sw_property.business b USING(business_id)
                  WHERE b.business_id IS NULL
                ) v
            """).fetchone()[0]
            if fk_violations:
                raise RuntimeError(f"Cross-reference reconciliation failed: {fk_violations} violations")
            size_bytes = conn.execute("SELECT pg_database_size(current_database())").fetchone()[0]
        return {"database":dbname,"release_id":release_id,"package_sha256":package_sha,"file_manifest":manifest_files,"source_collection_counts":source_counts,"verified_table_counts":actual,"cross_reference_violations":fk_violations,"database_size_bytes":size_bytes}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dsn",default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--expected-database",default="saltwater_test")
    args=parser.parse_args()
    if not args.dsn:
        parser.error("Set DATABASE_URL to the disposable PostgreSQL connection.")
    print(json.dumps(import_package(args.root,args.dsn,args.expected_database),indent=2,sort_keys=True))

if __name__=="__main__":
    main()
