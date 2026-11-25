"""Generate linked property maintenance, defects, inspections and repair records."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR = "SW-PROPERTY-MAINTENANCE-001"

def _n(key, lo, hi):
    d=hashlib.sha256(key.encode()).digest()
    return lo + int.from_bytes(d[:4],"big") % (hi-lo+1)

def _pick(values,key): return values[_n(key,0,len(values)-1)]
def _slug(v): return "".join(c for c in str(v).upper() if c.isalnum())[:24]

def build_property_maintenance(world, tenure, services):
    props={x["property_id"]:x for x in world["properties"]}
    buildings={x["building_id"]:x for x in world["buildings"]}
    premises={x["premises_id"]:x for x in world["premises"]}
    units={x["unit_id"]:x for x in world["units"]}
    systems=services["building_systems"]; equipment=services["equipment_assets"]
    managers={x["property_id"]:x["manager_organisation_id"] for x in tenure["management_appointments"]}
    owners={x["property_id"]:x["owner_organisation_id"] for x in tenure["current_ownership_interests"]}
    organisations={x["organisation_id"]:x for x in tenure["organisations"]}
    for provider in services["utility_providers"]: organisations[provider["organisation_id"]]=provider
    trades=["electrical_engineering","mechanical_engineering","plumbing","fire_safety","lift_engineering","building_fabric","roofing_and_waterproofing","security_systems","telecommunications","civil_and_drainage","general_building_maintenance"]
    contractors=[]
    for i,trade in enumerate(trades,1):
        oid=f"SWORG-MAINT-{i:02d}"
        contractors.append({"organisation_id":oid,"display_name":f"Saltwater {trade.replace('_',' ').title()} Services","organisation_type":"maintenance_contractor","specialisms":[trade],"status":"active","fictional_entity":True})
    plans=[]; cycles=[]; inspections=[]; defects=[]; requests=[]; orders=[]; lines=[]; history=[]; parts=[]; warranties=[]; replacements=[]; procedures=[]
    critical_types={"fire_detection_and_suppression","electrical_distribution","vertical_transport","potable_water_distribution","wastewater_and_sanitary","physical_security_and_access"}
    for bid,b in sorted(buildings.items()):
        pid=b["property_id"]; manager=managers[pid]
        plan_id=f"SWMPLAN-{_slug(bid)}"
        plans.append({"maintenance_plan_id":plan_id,"property_id":pid,"building_id":bid,"responsible_organisation_id":manager,"plan_type":"integrated_building_asset_maintenance","plan_status":"active","review_interval_days":365,"risk_profile":"critical" if b.get("building_use") in {"port_maritime","warehouse","industrial","healthcare","transport","data_centre","financial"} else "standard","effective_tick":0})
        for c,cycle in enumerate(["statutory_safety","preventive_plant","fabric_and_envelope","life_safety_and_security","utilities_resilience"],1):
            cycles.append({"maintenance_cycle_id":f"SWMCYC-{_slug(bid)}-{c}","maintenance_plan_id":plan_id,"property_id":pid,"building_id":bid,"cycle_type":cycle,"interval_days":_n(bid+cycle,30,730),"next_due_tick":_n(bid+cycle+"due",15,360),"priority":"critical" if cycle in ("statutory_safety","life_safety_and_security") else "routine"})
        procedures.append({"procedure_id":f"SWMPRC-{_slug(bid)}","property_id":pid,"building_id":bid,"procedure_scope":"building_emergency_maintenance","scenarios":["loss_of_electricity","water_supply_failure","flood_or_water_ingress","fire_system_fault","lift_entrapment","communications_failure"],"first_response_organisation_id":manager,"continuity_arrangements":["isolate_affected_service","activate_redundant_supply_where_fitted","protect_occupants_and_assets","notify_relevant_emergency_service","record_incident_and_restore_service"],"person_records_created":0})
    for s in systems:
        sid=s["building_system_id"]; bid=s["building_id"]; pid=s["property_id"]
        plan=next(x["maintenance_plan_id"] for x in plans if x["building_id"]==bid)
        iid=f"SWMINSP-{_slug(sid)}"
        inspections.append({"inspection_id":iid,"property_id":pid,"building_id":bid,"building_system_id":sid,"inspection_type":"planned_condition_and_functional_inspection","inspection_scope":"visual_functional_and_record_review","interval_days":_n(sid+"int",30,365),"last_completed_tick":0,"next_due_tick":s.get("next_inspection_due_tick",90),"inspection_status":"scheduled","responsible_organisation_id":managers[pid],"result":"baseline_serviceable_pending_first_simulation_inspection"})
    for seq,e in enumerate(equipment,1):
        eid=e["equipment_id"]; bid=e["building_id"]; pid=e["property_id"]; sid=e["building_system_id"]
        trade=_pick(trades,eid+"trade"); contractor=f"SWORG-MAINT-{trades.index(trade)+1:02d}"
        warranty_end=e["installation_year"]+_n(eid+"warranty",2,8)
        warranties.append({"warranty_id":f"SWWAR-{_slug(eid)}","equipment_id":eid,"property_id":pid,"building_id":bid,"warranty_provider_profile":_pick(["manufacturer","installer","integrated_system_supplier"],eid+"wp"),"start_year":e["installation_year"],"end_year":warranty_end,"warranty_state":"expired_historical" if warranty_end<2026 else "in_force","terms_profile":_pick(["parts_and_labour","parts_only","comprehensive","limited_components"],eid+"wt")})
        if seq%3==0 or e.get("replacement_priority")=="critical":
            severity=_pick(["low","moderate","high","critical"],eid+"sev")
            status="open" if severity in ("high","critical") else _pick(["open","monitoring","rectified_at_baseline"],eid+"status")
            defect_id=f"SWDEF-{_slug(eid)}"
            defects.append({"defect_id":defect_id,"property_id":pid,"building_id":bid,"building_system_id":sid,"equipment_id":eid,"defect_location_type":"equipment_or_plant_location","severity":severity,"defect_category":_pick(["wear_and_deterioration","control_or_sensor_fault","leak_or_seal_failure","corrosion_or_material_degradation","electrical_or_connection_fault","performance_degradation"],eid+"cat"),"discovery_source":"baseline_condition_assessment","discovered_tick":0,"defect_status":status,"operational_impact":_pick(["no_service_interruption","reduced_capacity","localised_service_restriction","system_redundancy_reduced"],eid+"impact"),"safety_implication":"requires_priority_review" if severity=="critical" else "managed_by_risk_based_controls","root_cause_profile":_pick(["age_and_wear","environmental_exposure","component_failure","maintenance_interval","installation_or_adjustment"],eid+"root"),"repair_urgency":"immediate" if severity=="critical" else ("urgent" if severity=="high" else "planned"),"temporary_control":_pick(["enhanced_monitoring","isolate_component_if_deteriorates","use_redundant_train","restricted_operation_pending_repair"],eid+"control"),"raised_work_request_id":f"SWWRQ-{_slug(eid)}","person_records_created":0})
            requests.append({"work_request_id":f"SWWRQ-{_slug(eid)}","property_id":pid,"building_id":bid,"building_system_id":sid,"equipment_id":eid,"defect_id":defect_id,"request_type":"corrective_maintenance","priority":"emergency" if severity=="critical" else severity,"requested_tick":0,"request_status":"accepted_for_work_order" if status=="open" else "monitor_or_close","raised_by_organisation_id":managers[pid],"responsible_organisation_id":contractor,"description_code":"repair_or_reinstate_asset_to_serviceable_condition"})
            if status=="open":
                oid=f"SWWO-{_slug(eid)}"
                orders.append({"work_order_id":oid,"work_request_id":f"SWWRQ-{_slug(eid)}","property_id":pid,"building_id":bid,"building_system_id":sid,"equipment_id":eid,"defect_id":defect_id,"maintenance_plan_id":plan,"work_type":"corrective_repair","priority":"emergency" if severity=="critical" else severity,"work_order_status":"planned","responsible_contractor_organisation_id":contractor,"managing_organisation_id":managers[pid],"required_trade":trade,"estimated_duration_hours_band":_pick(["under_2","2_to_4","4_to_8","1_to_2_days","over_2_days"],eid+"dur"),"labour_costing":"excluded_finance_bp34","scheduled_tick":_n(eid+"schedule",1,30),"completion_tick":None,"verification_required":True})
                lines.append({"work_order_line_id":f"SWWOL-{_slug(eid)}-01","work_order_id":oid,"line_type":"repair_or_component_replacement","asset_id":eid,"description_code":"diagnose_repair_test_and_return_to_service","quantity_band":_pick(["one","two_to_three","four_or_more"],eid+"qty"),"trade":trade})
                parts.append({"material_issue_id":f"SWMAT-{_slug(eid)}","work_order_id":oid,"equipment_id":eid,"material_class":_pick(["electrical_component","mechanical_component","seal_and_gasket","sensor_or_control","fastener_and_fitting","fire_safety_component"],eid+"mat"),"quantity_band":"one_or_small_batch","stock_source_profile":"contractor_or_estate_maintenance_store","financial_posting_created":False})
                history.append({"maintenance_event_id":f"SWMEV-{_slug(eid)}","work_order_id":oid,"equipment_id":eid,"property_id":pid,"building_id":bid,"event_type":"work_order_raised","event_tick":0,"event_status":"open","verification_state":"pending"})
        if e.get("replacement_priority") in ("critical","elevated") or e["installation_year"]<=2012:
            replacements.append({"replacement_plan_id":f"SWRPL-{_slug(eid)}","equipment_id":eid,"property_id":pid,"building_id":bid,"building_system_id":sid,"replacement_reason":_pick(["age_and_obsolescence","reliability_risk","capacity_or_efficiency","spares_availability"],eid+"rr"),"target_year":max(2027,e["installation_year"]+_n(eid+"life",15,25)),"priority":e.get("replacement_priority","planned"),"capital_approval_state":"forecast_only","financial_commitment_created":False})
    for prop in props.values():
        pid=prop["property_id"]
        inspections.append({"inspection_id":f"SWMINSP-SITE-{_slug(pid)}","property_id":pid,"building_id":None,"building_system_id":None,"inspection_type":"site_condition_drainage_access_and_boundary_inspection","inspection_scope":"site_features_access_routes_drainage_and_external_fabric","interval_days":180,"last_completed_tick":0,"next_due_tick":180,"inspection_status":"scheduled","responsible_organisation_id":managers[pid],"result":"baseline_recorded_pending_first_simulation_inspection"})
    body={"schema":"saltwater-property-maintenance/1.0","dataset_id":"SW-PROPERTY-MAINTENANCE-V1","canon_status":"CANONICAL_FICTIONAL_GAME_WORLD","generator":GENERATOR,"effective_tick":0,"city":"Saltwater","summary":{"property_count":len(props),"building_count":len(buildings),"maintenance_plan_count":len(plans),"maintenance_cycle_count":len(cycles),"inspection_schedule_count":len(inspections),"defect_count":len(defects),"work_request_count":len(requests),"work_order_count":len(orders),"work_order_line_count":len(lines),"material_issue_count":len(parts),"maintenance_event_count":len(history),"warranty_count":len(warranties),"replacement_forecast_count":len(replacements),"emergency_procedure_count":len(procedures),"maintenance_contractor_count":len(contractors),"person_records_created":0,"population_records_created":0,"financial_postings_created":0},"maintenance_contractors":contractors,"maintenance_plans":plans,"maintenance_cycles":cycles,"inspections":inspections,"defects":defects,"work_requests":requests,"work_orders":orders,"work_order_lines":lines,"material_issues":parts,"maintenance_events":history,"warranties":warranties,"replacement_forecasts":replacements,"emergency_procedures":procedures,"lineage":{"property_world_dataset":"SW-PROPERTY-WORLD-V1","property_tenure_dataset":"SW-PROPERTY-TENURE-V1","building_services_dataset":"SW-BUILDING-SERVICES-V1"},"gameplay":{"maintenance":"Plans and cycles cover every building; inspections cover every building system and every property site.","defects":"Equipment-linked condition defects carry severity, operational impact, safety implications, urgency and temporary controls.","repairs":"Open defects create linked work requests, orders, trade requirements, material records and lifecycle events.","asset_lifecycle":"Warranties and capital replacement forecasts link to canonical equipment assets.","finance_boundary":"No invoices, payments, cost ledger, rent or capital commitments are posted; BP-34 owns financial records.","population":"No residents, employees, contractors-as-persons or other person records are created."}}
    canonical=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(); body["manifest_sha256"]=hashlib.sha256(canonical).hexdigest()
    return body

def main():
    root=Path(__file__).resolve().parents[1]
    def load(path): return _expand_columnar(json.loads((root/path).read_text(encoding="utf-8")))
    result=build_property_maintenance(load("data/property/saltwater-property-world-v1.json"),load("data/property/saltwater-property-tenure-v1.json"),load("data/property/saltwater-building-services-v1.json"))
    out=root/"data/property/saltwater-property-maintenance-v1.json"; doc=to_columnar_document(result); doc["schema"]="saltwater-property-maintenance-columnar/1.0"
    out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"]|{"manifest_sha256":result["manifest_sha256"],"output_bytes":out.stat().st_size},indent=2,sort_keys=True))
if __name__=="__main__": main()
