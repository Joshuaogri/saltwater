"""Generate fictional development control, construction and lawful-use records."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR="SW-PROPERTY-DEVELOPMENT-CONTROL-001"
def _n(k,lo,hi):
 d=hashlib.sha256(k.encode()).digest()
 return lo+int.from_bytes(d[:4],"big")%(hi-lo+1)
def _pick(v,k): return v[_n(k,0,len(v)-1)]
def _slug(v): return "".join(c for c in str(v).upper() if c.isalnum())[:24]
def build_development_control(world,tenure,services,maintenance,valuation):
 properties={x["property_id"]:x for x in world["properties"]}
 buildings={x["building_id"]:x for x in world["buildings"]}
 premises={x["premises_id"]:x for x in world["premises"]}
 units={x["unit_id"]:x for x in world["units"]}
 owners={x["property_id"]:x["owner_organisation_id"] for x in tenure["current_ownership_interests"]}
 managers={x["property_id"]:x["manager_organisation_id"] for x in tenure["management_appointments"]}
 condition={x["building_id"]:x for x in valuation["condition_assessments"] if x.get("building_id")}
 defects_by_building={}
 for d in maintenance["defects"]: defects_by_building.setdefault(d["building_id"],[]).append(d)
 premises_by_building={}
 for p in premises.values(): premises_by_building.setdefault(p["building_id"],[]).append(p)
 units_by_premises={}
 for u in units.values(): units_by_premises.setdefault(u["premises_id"],[]).append(u)
 site_plans=[]; planning_permissions=[]; applications=[]; building_control=[]; inspections=[]; certificates=[]; lawful_uses=[]; development_projects=[]; restrictions=[]; occupancy_compliance=[]
 use_map={
  "port_maritime":"port_and_maritime_operations","warehouse":"logistics_and_warehousing","industrial":"industrial_and_export_manufacturing",
  "healthcare":"healthcare_and_clinical_services","transport":"transport_and_transit_operations","data_centre":"data_centre_and_critical_digital_infrastructure",
  "financial":"financial_and_professional_services","commercial":"commercial_business_use","residential":"residential_use",
  "office":"office_and_corporate_headquarters","hospitality":"hotel_and_hospitality","education":"education_and_training",
  "institutional":"public_and_institutional_use","retail":"retail_and_customer_services","mixed_use":"mixed_use"
 }
 allowed_by_use={
  "port_and_maritime_operations":["port_and_maritime_operations","logistics_and_warehousing","industrial_and_export_manufacturing"],
  "logistics_and_warehousing":["logistics_and_warehousing","industrial_and_export_manufacturing","commercial_business_use"],
  "industrial_and_export_manufacturing":["industrial_and_export_manufacturing","logistics_and_warehousing"],
  "healthcare_and_clinical_services":["healthcare_and_clinical_services","office_and_corporate_headquarters"],
  "transport_and_transit_operations":["transport_and_transit_operations","commercial_business_use"],
  "data_centre_and_critical_digital_infrastructure":["data_centre_and_critical_digital_infrastructure","office_and_corporate_headquarters"],
  "financial_and_professional_services":["financial_and_professional_services","office_and_corporate_headquarters","commercial_business_use"],
  "commercial_business_use":["commercial_business_use","retail_and_customer_services","office_and_corporate_headquarters"],
  "residential_use":["residential_use"],
  "office_and_corporate_headquarters":["office_and_corporate_headquarters","financial_and_professional_services","commercial_business_use"],
  "hotel_and_hospitality":["hotel_and_hospitality","commercial_business_use"],
  "education_and_training":["education_and_training","office_and_corporate_headquarters"],
  "public_and_institutional_use":["public_and_institutional_use","education_and_training","healthcare_and_clinical_services"],
  "retail_and_customer_services":["retail_and_customer_services","commercial_business_use"],
  "mixed_use":["mixed_use","commercial_business_use","residential_use","retail_and_customer_services"]
 }
 # Every existing site/building/premises receives an auditable baseline control record.
 for pid,p in sorted(properties.items()):
  owner=owners[pid]; manager=managers[pid]
  use=p.get("primary_use","commercial")
  plan_id=f"SWDEVPLAN-{_slug(pid)}"
  zoning=use_map.get(use,"commercial_business_use")
  site_plans.append({"site_development_plan_id":plan_id,"property_id":pid,"applicant_organisation_id":owner,"land_use_designation":zoning,"development_intensity":"existing_baseline","site_plan_status":"adopted_existing_development","site_constraints":["coastal_flood_and_surge_review","fire_appliance_access","utility_capacity","road_frontage_and_emergency_access"],"planning_policy_version":"SW-PLAN-2026-01","adoption_tick":0,"source_basis":"existing_canonical_property_world"})
  # Record the permission basis for current built form, not a pending application.
  for b in sorted([x for x in buildings.values() if x["property_id"]==pid],key=lambda x:x["building_id"]):
   bid=b["building_id"]; build_year=int(b.get("construction_year") or 2000); buse=b.get("building_use","commercial")
   permitted=use_map.get(buse,zoning)
   permission_id=f"SWPLANPERM-{_slug(bid)}"
   planning_permissions.append({"planning_permission_id":permission_id,"site_development_plan_id":plan_id,"property_id":pid,"building_id":bid,"applicant_organisation_id":owner,"permission_type":"retrospective_canonical_baseline_development_consent","development_description":f"Existing {permitted.replace('_',' ')} building and associated site works","approved_use_class":permitted,"decision":"granted","decision_tick":0,"decision_basis":"fictional_existing_world_baseline","conditions":["maintain_fire_and_emergency_access","maintain_approved_drainage_and_coastal_protection","no_material_change_of_use_without_permission","maintain_accessible_egress_and_utility_capacity"],"permission_validity":"existing_development_authorised_in_game_canon","historic_application_fabricated":False})
   control_id=f"SWBCONTROL-{_slug(bid)}"
   bc_status="completion_certified"
   building_control.append({"building_control_case_id":control_id,"property_id":pid,"building_id":bid,"planning_permission_id":permission_id,"applicant_organisation_id":owner,"principal_contractor_organisation_id":None,"control_route":"full_plan_and_inspection_control","case_status":bc_status,"design_standard_profile":"SW-BUILDING-CODE-2026-01","fire_safety_review":"recorded_in_baseline","structural_review":"recorded_in_baseline","accessibility_review":"recorded_in_baseline","utility_and_drainage_review":"recorded_in_baseline","construction_year":build_year,"case_basis":"canonical_existing_building_baseline","inspection_history":"baseline_certification_not_fabricated_visit_log"})
   cert_id=f"SWCOMPCERT-{_slug(bid)}"
   certificates.append({"completion_certificate_id":cert_id,"property_id":pid,"building_id":bid,"building_control_case_id":control_id,"certificate_type":"building_completion_and_safe_use_certificate","certificate_status":"issued","issue_tick":0,"issue_basis":"existing_canonical_building_baseline","approved_use_class":permitted,"conditions":["fire_systems_maintained","structural_and_envelope_maintenance","emergency_egress_kept_clear","utility_systems_operated_within_capacity"],"certificate_number":f"SW-CC-{_slug(bid)}"})
   c=condition.get(bid,{})
   due_tick=_n(bid+"inspection-due",30,180)
   inspections.append({"building_inspection_schedule_id":f"SWINSP-{_slug(bid)}","property_id":pid,"building_id":bid,"building_control_case_id":control_id,"inspection_type":"periodic_building_safety_and_code_compliance","inspection_interval_days":365,"next_due_tick":due_tick,"inspection_status":"scheduled_not_completed","priority":"urgent" if c.get("critical_defect_count",0)>0 else ("elevated" if c.get("follow_up_required") else "routine"),"linked_open_defects":len(defects_by_building.get(bid,[])),"inspection_visit_created":False})
   for pr in sorted(premises_by_building.get(bid,[]),key=lambda x:x["premises_id"]):
    prid=pr["premises_id"]; declared=permitted
    lawful_uses.append({"lawful_use_certificate_id":f"SWUSE-{_slug(prid)}","property_id":pid,"building_id":bid,"premises_id":prid,"completion_certificate_id":cert_id,"lawful_use_class":declared,"certificate_status":"current","effective_tick":0,"change_of_use_permission_required":True,"use_conditions":["remain_within_approved_use_class","fire_capacity_and_egress_maintained","accessibility_and_sanitation_requirements_met","no hazardous_or_high-impact_activity_without_specific_consent"],"evidence_basis":"existing_premises_and_building_use_canon"})
    # Unit compliance is generated once for the units in this premises.
    # It does not imply that an occupant/person exists.
    for u in units_by_premises.get(prid,[]):
     occupancy_compliance.append({"use_compliance_id":f"SWUSECOMP-{_slug(u['unit_id'])}","property_id":pid,"building_id":bid,"premises_id":prid,"unit_id":u["unit_id"],"permitted_use_class":permitted,"compliance_state":"unoccupied_or_occupancy_not_assessed","inspection_required_on_occupation":True,"person_records_created":0})
   # A small subset of properties carries ongoing permitted capital works projects.
   if _n(pid+"capital-works",1,100)<=18:
    project_id=f"SWPROJECT-{_slug(pid)}"
    development_projects.append({"development_project_id":project_id,"property_id":pid,"project_type":_pick(["building_rehabilitation","utility_capacity_upgrade","fire_and_life_safety_upgrade","coastal_resilience_works","accessibility_upgrade"],pid+"project-type"),"project_status":"approved_preconstruction","project_sponsor_organisation_id":owner,"property_manager_organisation_id":manager,"planning_permission_id":next((x["planning_permission_id"] for x in planning_permissions if x["property_id"]==pid),None),"project_start_tick":None,"project_completion_tick":None,"construction_activity_started":False,"financial_commitments_created":False,"project_history_basis":"fictional_current_development_pipeline"})
 for rule in [
  ("SW-PLAN-PORT-01","port_and_maritime_operations","port_and_maritime_operations",["navigation_safety","hazardous_cargo_separation","security_perimeter","emergency_response_access"]),
  ("SW-PLAN-LOG-01","logistics_and_warehousing","logistics_and_warehousing",["heavy_vehicle_circulation","freight_queue_management","fire_appliance_access"]),
  ("SW-PLAN-RES-01","residential_use","residential_use",["habitable_room_standards","daylight_and_ventilation","sanitation","fire_egress"]),
  ("SW-PLAN-CRIT-01","critical_infrastructure","data_centre_and_critical_digital_infrastructure",["resilience","backup_power","physical_security","utility_redundancy"])
 ]:
  restrictions.append({"development_control_rule_id":rule[0],"regulated_site_profile":rule[1],"permitted_use_class":rule[2],"mandatory_assessment_topics":rule[3],"rule_status":"active","effective_tick":0,"fictional_code":"SW-PLAN-2026-01"})
 # Applications table intentionally empty: baseline approvals are not fake new applications.
 summary={"property_count":len(properties),"site_development_plan_count":len(site_plans),"planning_permission_count":len(planning_permissions),"planning_application_count":len(applications),"building_control_case_count":len(building_control),"building_inspection_schedule_count":len(inspections),"completion_certificate_count":len(certificates),"lawful_use_certificate_count":len(lawful_uses),"unit_use_compliance_count":len(occupancy_compliance),"unit_identity_count":len(units),"development_project_count":len(development_projects),"development_control_rule_count":len(restrictions),"issued_permission_count":sum(x["decision"]=="granted" for x in planning_permissions),"pending_applications":0,"construction_projects_started":0,"financial_commitments_created":0,"invoices_created":0,"person_records_created":0,"population_records_created":0}
 body={"schema":"saltwater-property-development-control/1.0","dataset_id":"SW-PROPERTY-DEVELOPMENT-CONTROL-V1","canon_status":"CANONICAL_FICTIONAL_GAME_WORLD","generator":GENERATOR,"effective_tick":0,"city":"Saltwater","summary":summary,"site_development_plans":site_plans,"planning_permissions":planning_permissions,"planning_applications":applications,"building_control_cases":building_control,"building_inspection_schedules":inspections,"completion_certificates":certificates,"lawful_use_certificates":lawful_uses,"unit_use_compliance":occupancy_compliance,"development_projects":development_projects,"development_control_rules":restrictions,"lineage":{"property_world":"SW-PROPERTY-WORLD-V1","tenure":"SW-PROPERTY-TENURE-V1","valuation_condition":"SW-PROPERTY-VALUE-RISK-TAX-V1","maintenance":"SW-PROPERTY-MAINTENANCE-V1"},"gameplay":{"existing_baseline":"Existing properties and buildings receive canonical existing-development permission and completion/use records; these are not represented as newly filed applications or invented historical site visits.","future_play":"Player-controlled development applications, objections, decisions, construction inspections, enforcement and completion events are created as runtime events when gameplay occurs.","finance_boundary":"No fees, charges, invoices, payments, contracts or financial commitments are created; BP-34 owns transactions.","people_boundary":"No applicants as individuals, contractors, occupants, residents or other person records are created."}}
 canonical=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(); body["manifest_sha256"]=hashlib.sha256(canonical).hexdigest()
 return body
def main():
 root=Path(__file__).resolve().parents[1]
 def load(p): return _expand_columnar(json.loads((root/p).read_text(encoding="utf-8")))
 data=build_development_control(load("data/property/saltwater-property-world-v1.json"),load("data/property/saltwater-property-tenure-v1.json"),load("data/property/saltwater-building-services-v1.json"),load("data/property/saltwater-property-maintenance-v1.json"),load("data/property/saltwater-property-value-risk-tax-v1.json"))
 out=root/"data/property/saltwater-property-development-control-v1.json"; doc=to_columnar_document(data); doc["schema"]="saltwater-property-development-control-columnar/1.0"
 out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps(data["summary"]|{"manifest_sha256":data["manifest_sha256"],"output_bytes":out.stat().st_size},indent=2,sort_keys=True))
if __name__=="__main__": main()
