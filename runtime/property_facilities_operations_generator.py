"""Build integrated facilities and property-operations schedules."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR = "SW-PROPERTY-FACILITIES-OPERATIONS-001"

SERVICES = [
 ("cleaning","common_areas_and_shared_circulation","daily","daily","cleanliness_score","critical"),
 ("waste_general","general_commercial_waste","daily","daily","collection_completion","high"),
 ("waste_recycling","segregated_recyclables_and_packaging","weekly","weekly","segregation_compliance","normal"),
 ("waste_organics","food_and_organic_waste","daily","daily","collection_completion","high"),
 ("pest_management","integrated_pest_management","monthly","monthly","pest_activity_and_treatment","high"),
 ("grounds","landscape_external_space_and_drainage","weekly","weekly","grounds_condition","normal"),
 ("water_hygiene","potable_water_hygiene_and_tank_controls","quarterly","quarterly","water_hygiene_compliance","critical"),
 ("fire_routine","fire_detection_suppression_and_egress_checks","monthly","monthly","inspection_completion","critical"),
 ("vertical_transport","lift_escalator_and_moving_walkway_service","monthly","monthly","equipment_availability","critical"),
 ("hvac_environment","ventilation_air_quality_and_hvac_service","quarterly","quarterly","environmental_compliance","high"),
 ("security_systems","doors_locks_readers_and_perimeter_checks","monthly","monthly","access_control_integrity","critical"),
 ("energy_management","energy_metering_controls_and_efficiency","monthly","monthly","energy_intensity_review","normal"),
 ("drainage_flood","surface_water_drainage_and_flood_defence_checks","monthly","monthly","drainage_readiness","critical"),
 ("facade_roof","roof_envelope_and_facade_condition","annual","annual","fabric_condition","high"),
 ("port_specialist","cargo_marshalling_and_maritime_facility_housekeeping","per_shift","daily","operational_clearance","critical"),
 ("clinical_waste","segregated_clinical_and_specialist_waste","per_collection","daily","chain_of_custody_compliance","critical"),
]

def _id(prefix, value):
    return prefix + "-" + hashlib.sha256(str(value).encode()).hexdigest()[:12].upper()

def _class(row):
    return str(row.get("building_use") or row.get("property_use") or row.get("use_class") or row.get("property_type") or "general").lower()

def build_facilities_operations(world, tenure, services, maintenance):
    properties = world["properties"]
    buildings = world["buildings"]
    premises = world["premises"]
    units = world.get("units", [])
    managers = {x["property_id"]: x for x in tenure["management_appointments"]}
    contractors = maintenance.get("maintenance_contractors", maintenance.get("contractor_organisations", []))
    contractor_ids = [x.get("organisation_id") for x in contractors if x.get("organisation_id")]
    property_ids = {x["property_id"] for x in properties}
    building_by_id = {x["building_id"]: x for x in buildings}
    premises_by_id = {x["premises_id"]: x for x in premises}
    unit_ids = {x["unit_id"] for x in units}
    tenure_unit_ids = {x["unit_id"] for x in tenure["unit_occupancy_states"]}
    meter_unit_ids = {x["unit_id"] for x in services["meters"] if x.get("meter_role") == "unit_submeter"}
    unit_reconciliation = {
      "property_world_unit_count": len(unit_ids),
      "tenure_unit_occupancy_state_count": len(tenure_unit_ids),
      "building_services_unit_submeter_count": len(meter_unit_ids),
      "property_development_control_unit_count": 62585,
      "world_vs_tenure_missing_unit_count": len(unit_ids - tenure_unit_ids),
      "world_vs_metering_missing_unit_count": len(unit_ids - meter_unit_ids),
      "tenure_unit_ids_not_in_world_count": len(tenure_unit_ids - unit_ids),
      "meter_unit_ids_not_in_world_count": len(meter_unit_ids - unit_ids),
      "reconciliation_status": "reconciled" if unit_ids == tenure_unit_ids == meter_unit_ids and len(unit_ids) == 62585 else "mismatch_preserved_for_reconciliation",
      "note": "The development-control count is cross-checked against source unit identities; no missing occupancy or meter records are fabricated."
    }
    contracts, schedules, zones, sla, escalation = [], [], [], [], []
    for index, p in enumerate(sorted(properties, key=lambda x:x["property_id"])):
        pid = p["property_id"]
        manager = managers.get(pid, {})
        managing_org = manager.get("manager_organisation_id") or manager.get("property_manager_organisation_id")
        for service, scope, frequency, window, metric, priority in SERVICES:
            # Port and clinical streams are applied only to matching operational uses.
            use = _class(p)
            if service == "port_specialist" and not any(k in use for k in ("port","maritime","cargo","terminal","logistics","warehouse")):
                continue
            if service == "clinical_waste" and not any(k in use for k in ("health","hospital","clinic","medical","laboratory")):
                continue
            cid = _id("SWFMC", pid + service)
            vendor = contractor_ids[index % len(contractor_ids)] if contractor_ids else None
            contracts.append({
              "facilities_contract_id": cid, "property_id": pid, "service_type": service,
              "service_scope": scope, "managing_organisation_id": managing_org,
              "service_provider_organisation_id": vendor,
              "contract_state": "baseline_service_arrangement",
              "service_frequency": frequency, "service_window": window,
              "effective_from_tick": 0, "financial_terms": "not_modelled_bp34",
              "performance_actuals": "not_yet_recorded"
            })
            zones.append({
              "service_zone_id": _id("SWFSZ", pid + service), "property_id": pid,
              "building_id": None, "premises_id": None, "service_type": service,
              "scope": "property_wide_site_and_shared_external_areas",
              "access_constraints": "use_authorised_access_points_and_current_property_security_policy",
              "zone_state": "baseline_defined"
            })
            sla.append({
              "sla_id": _id("SWSLA", pid + service), "facilities_contract_id": cid,
              "service_type": service, "target_frequency": frequency,
              "response_priority": priority, "performance_measure": metric,
              "target_state": "contractual_target_profile_not_measured_actual",
              "missed_service_escalation": "log_service_failure_notify_property_manager_and_open_corrective_request",
              "critical_failure_escalation": "protect_life_safety_and_continuity_notify_emergency_control"
            })
            schedules.append({
              "service_schedule_id": _id("SWFSS", pid + service), "property_id": pid,
              "building_id": None, "premises_id": None, "service_type": service,
              "service_frequency": frequency, "next_due_tick": 0,
              "schedule_state": "planned_not_yet_performed",
              "service_contract_id": cid
            })
    # Building-level technical and shared-area operations.
    for b in sorted(buildings, key=lambda x:x["building_id"]):
        bid, pid = b["building_id"], b["property_id"]
        use = _class(b)
        selected = ["cleaning","fire_routine","security_systems","hvac_environment","energy_management","facade_roof"]
        if any(k in use for k in ("office","tower","hotel","residential","commercial","terminal")):
            selected += ["vertical_transport","water_hygiene"]
        if any(k in use for k in ("port","maritime","cargo","terminal","logistics","warehouse")):
            selected += ["port_specialist","drainage_flood"]
        if any(k in use for k in ("health","hospital","clinic","medical","laboratory")):
            selected += ["clinical_waste","water_hygiene"]
        for service in sorted(set(selected)):
            spec = next(x for x in SERVICES if x[0] == service)
            schedules.append({
              "service_schedule_id": _id("SWFSS", bid + service), "property_id": pid,
              "building_id": bid, "premises_id": None, "service_type": service,
              "service_frequency": spec[2], "next_due_tick": 0,
              "schedule_state": "planned_not_yet_performed",
              "service_contract_id": _id("SWFMC", pid + service)
            })
    # Premises-level waste, cleaning and specialist servicing; no per-unit duplication.
    for pr in sorted(premises, key=lambda x:x["premises_id"]):
        pid, bid = pr["property_id"], pr.get("building_id")
        use = _class(pr)
        selected = ["cleaning","waste_general","waste_recycling"]
        if any(k in use for k in ("food","restaurant","catering","hospitality")):
            selected += ["waste_organics","pest_management"]
        if any(k in use for k in ("health","hospital","clinic","medical","laboratory")):
            selected += ["clinical_waste"]
        for service in sorted(set(selected)):
            schedules.append({
              "service_schedule_id": _id("SWFSS", pr["premises_id"] + service),
              "property_id": pid, "building_id": bid, "premises_id": pr["premises_id"],
              "service_type": service, "service_frequency": next(x[2] for x in SERVICES if x[0] == service),
              "next_due_tick": 0, "schedule_state": "planned_not_yet_performed",
              "service_contract_id": _id("SWFMC", pid + service)
            })
    escalation = [
      {"failure_type":"missed_routine_service","priority":"normal","action":"record_failure_notify_manager_and_rebook"},
      {"failure_type":"critical_plant_or_life_safety_failure","priority":"critical","action":"protect_people_isolate_unsafe_system_and_notify_emergency_control"},
      {"failure_type":"waste_overflow_or_hazardous_misclassification","priority":"high","action":"secure_area_preserve_specialist_handling_and_escalate"},
      {"failure_type":"flood_or_drainage_obstruction","priority":"critical","action":"activate_flood_contingency_and_protect_critical_access"},
      {"failure_type":"repeated_sla_failure","priority":"high","action":"supplier_performance_review_and_contract_remediation"}
    ]
    body = {
      "schema":"saltwater-property-facilities-operations/1.0",
      "dataset_id":"SW-PROPERTY-FACILITIES-OPERATIONS-V1",
      "canon_status":"CANONICAL_FICTIONAL_GAME_WORLD",
      "generator":GENERATOR,"effective_tick":0,"city":"Saltwater",
      "summary":{
        "property_count":len(properties),"building_count":len(buildings),
        "premises_count":len(premises),"world_unit_count":len(units),
        "facilities_contract_count":len(contracts),"service_schedule_count":len(schedules),
        "service_zone_count":len(zones),"sla_count":len(sla),
        "service_request_count":0,"completed_service_visit_count":0,
        "measured_sla_actual_count":0,"invoice_count":0,"payment_count":0,
        "financial_postings_created":0,"person_records_created":0,
        "population_records_created":0
      },
      "unit_count_reconciliation":unit_reconciliation,
      "facilities_contracts":contracts,"service_schedules":schedules,
      "service_zones":zones,"service_level_agreements":sla,
      "service_failure_escalation_rules":escalation,
      "service_requests":[],"service_visits":[],"supplier_performance_actuals":[],
      "lineage":{"property_world":"SW-PROPERTY-WORLD-V1","property_tenure":"SW-PROPERTY-TENURE-V1","building_services":"SW-BUILDING-SERVICES-V1","property_maintenance":"SW-PROPERTY-MAINTENANCE-V1"},
      "governance":{
        "baseline":"Schedules and target SLAs define the opening operating model; no visit or performance result is invented.",
        "waste":"Waste streams are service definitions, not fabricated tonnage or manifests.",
        "finance":"No invoices, charges or payments are created; BP-34 is the sole financial posting authority.",
        "people":"No staff, contractors-as-persons, residents or other person records are created.",
        "units":"The differing unit counts remain explicitly visible until identity-level reconciliation is completed."
      }
    }
    body["manifest_sha256"] = hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    return body

def main():
    root=Path(__file__).resolve().parents[1]
    def load(path): return _expand_columnar(json.loads((root/path).read_text(encoding="utf-8")))
    data=build_facilities_operations(load("data/property/saltwater-property-world-v1.json"),load("data/property/saltwater-property-tenure-v1.json"),load("data/property/saltwater-building-services-v1.json"),load("data/property/saltwater-property-maintenance-v1.json"))
    out=root/"data/property/saltwater-property-facilities-operations-v1.json"
    doc=to_columnar_document(data);doc["schema"]="saltwater-property-facilities-operations-columnar/1.0"
    out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(data["summary"]|{"unit_count_reconciliation":data["unit_count_reconciliation"],"manifest_sha256":data["manifest_sha256"],"output_bytes":out.stat().st_size},indent=2,sort_keys=True))
if __name__=="__main__": main()
