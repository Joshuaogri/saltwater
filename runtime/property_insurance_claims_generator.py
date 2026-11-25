"""Build property insurance exposure, loss-event and claims-control registers."""
from __future__ import annotations
import hashlib,json
from runtime.dataset_io import load_json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR="SW-PROPERTY-INSURANCE-CLAIMS-001"
def _key(v): return hashlib.sha256(str(v).encode()).hexdigest()[:14].upper()
def build_insurance_claims(world,insurance,services,maintenance,development,rights):
    props={x["property_id"]:x for x in world["properties"]}
    buildings={x["building_id"]:x for x in world["buildings"]}
    policies={x["property_id"]:x for x in insurance["insurance_policies"]}
    coverages={x["insurance_policy_id"]:[] for x in insurance["insurance_policies"]}
    for x in insurance["insurance_coverages"]: coverages.setdefault(x["insurance_policy_id"],[]).append(x)
    valuations={x["building_id"]:x for x in insurance["asset_valuations"] if x.get("building_id")}
    property_values={x["property_id"]:x for x in insurance["asset_valuations"] if x.get("building_id") is None}
    risks={x["property_id"]:x for x in insurance["property_risks"]}
    insurers={x["organisation_id"]:x for x in insurance["insurer_organisations"]}
    equipment={x["equipment_id"]:x for x in services["equipment_assets"]}
    defects=maintenance["defects"]
    defects_by_equipment={}
    for d in defects: defects_by_equipment.setdefault(d["equipment_id"],[]).append(d)
    systems={x["building_system_id"]:x for x in services["building_systems"]}
    development_by_building={x["building_id"]:x for x in development["completion_certificates"]}
    access_rights={x["property_id"]:x for x in rights["property_rights_schedules"]}
    policy_exposures=[]; building_schedules=[]; equipment_schedules=[]; defect_exposures=[]
    peril_assessments=[]; claims_register=[]; loss_events=[]; claim_processes=[]; claim_controls=[]
    peril_catalog=[
      ("coastal_flood_and_storm_surge","flood_storm_surge_and_coastal_perils","coastal_hazard"),
      ("extreme_rainfall_and_surface_water","property_damage_and_reinstatement","weather_and_drainage"),
      ("fire_and_smoke","property_damage_and_reinstatement","fire_and_life_safety"),
      ("electrical_and_power_failure","property_damage_and_reinstatement","critical_services"),
      ("water_ingress_and_pipe_failure","property_damage_and_reinstatement","building_services"),
      ("structural_or_envelope_failure","property_damage_and_reinstatement","building_fabric"),
      ("machinery_and_equipment_breakdown","property_damage_and_reinstatement","plant_and_equipment"),
      ("theft_vandalism_and_malicious_damage","property_damage_and_reinstatement","security"),
      ("business_interruption","business_interruption_and_rent_loss","continuity"),
      ("port_and_maritime_adjacent_loss","property_damage_and_reinstatement","port_and_trade")
    ]
    for pid,p in sorted(props.items()):
        policy=policies[pid]; pid_policy=policy["insurance_policy_id"]; risk=risks[pid]
        prop_value=property_values[pid]
        coverage_ids=[x["coverage_id"] for x in coverages[pid_policy]]
        policy_exposures.append({
          "policy_exposure_id":f"SWIPE-{_key(pid)}","property_id":pid,
          "insurance_policy_id":pid_policy,"policyholder_organisation_id":policy["policyholder_organisation_id"],
          "insurer_organisation_id":policy["insurer_organisation_id"],
          "insurer_name":insurers[policy["insurer_organisation_id"]]["display_name"],
          "policy_status":policy["policy_status"],"sum_insured_swc":policy["sum_insured_swc"],
          "deductible_band":policy["deductible_band"],"coverage_ids":coverage_ids,
          "property_asset_valuation_id":prop_value["asset_valuation_id"],
          "risk_profile_id":risk["property_risk_id"],
          "insurance_review_state":"baseline_policy_indexed_not_independently_underwritten",
          "policy_wording_and_exclusions":"not_modelled_full_wording_required_for_claim_adjudication",
          "premium_posted":False,"claim_created":False
        })
        for peril,coverage_type,domain in peril_catalog:
            matching=[x for x in coverages[pid_policy] if x["coverage_type"]==coverage_type]
            peril_assessments.append({
              "peril_assessment_id":f"SWPER-{_key(pid+peril)}","property_id":pid,
              "insurance_policy_id":pid_policy,"peril":peril,"risk_domain":domain,
              "risk_profile":risk["risk_profile"],"coverage_match_ids":[x["coverage_id"] for x in matching],
              "coverage_presence":"listed" if matching else "not_listed",
              "coverage_limit_swc":max([x["limit_swc"] for x in matching],default=0),
              "policy_exclusion_status":"unknown_until_wording_review",
              "site_specific_hazard_assessment":"not_yet_surveyed",
              "loss_event_recorded":False
            })
    for bid,b in sorted(buildings.items()):
        pid=b["property_id"]; val=valuations.get(bid)
        equipment_ids=[x["equipment_id"] for x in equipment.values() if x["building_id"]==bid]
        defects_for_building=[x for x in defects if x["building_id"]==bid]
        building_schedules.append({
          "building_insurance_schedule_id":f"SWBIS-{_key(bid)}","property_id":pid,
          "building_id":bid,"insurance_policy_id":policies[pid]["insurance_policy_id"],
          "asset_valuation_id":val["asset_valuation_id"] if val else None,
          "building_use":b.get("building_use"),"completion_certificate_id":development_by_building.get(bid,{}).get("completion_certificate_id"),
          "equipment_count":len(equipment_ids),"open_defect_count":sum(x["defect_status"]=="open" for x in defects_for_building),
          "critical_open_defect_count":sum(x["defect_status"]=="open" and x["severity"]=="critical" for x in defects_for_building),
          "schedule_status":"baseline_asset_schedule","reinstatement_value_basis":"existing_building_asset_valuation",
          "independent_reinstatement_survey":"not_completed"
        })
    for eid,e in sorted(equipment.items()):
        linked=defects_by_equipment.get(eid,[])
        equipment_schedules.append({
          "equipment_insurance_schedule_id":f"SWEIS-{_key(eid)}",
          "equipment_id":eid,"property_id":e["property_id"],"building_id":e["building_id"],
          "building_system_id":e["building_system_id"],
          "equipment_type":e["equipment_type"],"operational_state":e["operational_state"],
          "maintenance_class":e["maintenance_class"],"replacement_priority":e["replacement_priority"],
          "linked_defect_ids":[x["defect_id"] for x in linked],
          "open_defect_count":sum(x["defect_status"]=="open" for x in linked),
          "insurance_policy_id":policies[e["property_id"]]["insurance_policy_id"],
          "specific_equipment_sum_insured_swc":None,
          "valuation_state":"included_within_building_or_property_schedule_not_separately_valued"
        })
    for d in defects:
        defect_exposures.append({
          "insurance_defect_exposure_id":f"SWIDE-{_key(d['defect_id'])}",
          "defect_id":d["defect_id"],"equipment_id":d["equipment_id"],
          "property_id":d["property_id"],"building_id":d["building_id"],
          "insurance_policy_id":policies[d["property_id"]]["insurance_policy_id"],
          "severity":d["severity"],"defect_status":d["defect_status"],
          "operational_impact":d["operational_impact"],"repair_urgency":d["repair_urgency"],
          "risk_control_state":"maintenance_control_linked",
          "claim_causation":"not_assessed","insurable_loss":"not_asserted",
          "notification_required":"review_policy_conditions_if_loss_occurs"
        })
    # Empty operational registers: no fictional incident, claim, loss or settlement is fabricated.
    claim_processes=[
      ("first_notification","capture_event_time_location_cause_and_reporter_organisation"),
      ("coverage_triage","verify_policy_period_insured_interest_peril_limit_exclusions_and_deductible"),
      ("loss_mitigation","record_emergency_controls_protect_people_and_prevent_further_damage"),
      ("evidence_preservation","retain_photographs_reports_cctv_logs_maintenance_and_access_records"),
      ("adjuster_instruction","appoint_independent_loss_adjuster_or_specialist_surveyor"),
      ("quantum_assessment","separate_repair_reinstatement_business_interruption_and_salvage"),
      ("liability_and_recovery","assess_third_party_responsibility_subrogation_and_recovery"),
      ("coverage_decision","record_acceptance_reservation_of_rights_or_declination_with_reasons"),
      ("settlement_authorisation","refer approved settlement to finance authority BP-34"),
      ("closure_and_recovery","record reinstatement_verification_recovery_and_lessons")
    ]
    for seq,(stage,requirements) in enumerate(claim_processes,1):
        claim_controls.append({"claim_stage_order":seq,"claim_stage":stage,"minimum_record_requirements":requirements,"stage_owner":"insurer_or_authorised_claims_handler","financial_posting_authority":"BP-34_only"})
    event_types=[
      "coastal_flood","storm_surge","extreme_rainfall","fire","smoke_damage","electrical_fire_or_failure",
      "water_escape","structural_damage","machinery_breakdown","theft","vandalism","vehicle_impact",
      "port_cargo_adjacent_property_damage","business_interruption","public_utility_outage","environmental_contamination"
    ]
    event_catalog=[{"loss_event_type":x,"event_creation_policy":"create_only_from_simulated_incident_or_verified_source_event","required_links":["property_id","event_tick","event_location","cause_assessment","damage_assessment","evidence_register"],"may_generate_claim":"only_after_policy_and_insurable_interest_review"} for x in event_types]
    summary={
      "property_policy_exposure_count":len(policy_exposures),"building_insurance_schedule_count":len(building_schedules),
      "equipment_insurance_schedule_count":len(equipment_schedules),"defect_exposure_count":len(defect_exposures),
      "peril_assessment_count":len(peril_assessments),"loss_event_type_count":len(event_catalog),
      "claim_process_stage_count":len(claim_controls),"claims_register_count":0,"loss_event_register_count":0,
      "claim_reserve_count":0,"claim_payment_count":0,"settlement_count":0,
      "premium_posting_count":0,"financial_postings_created":0,"person_records_created":0,
      "population_records_created":0
    }
    body={
      "schema":"saltwater-property-insurance-claims/1.0","dataset_id":"SW-PROPERTY-INSURANCE-CLAIMS-V1",
      "canon_status":"CANONICAL_FICTIONAL_GAME_WORLD","generator":GENERATOR,
      "effective_tick":0,"city":"Saltwater","summary":summary,
      "policy_exposures":policy_exposures,"building_insurance_schedules":building_schedules,
      "equipment_insurance_schedules":equipment_schedules,"defect_exposure_register":defect_exposures,
      "peril_assessments":peril_assessments,"loss_event_register":loss_events,
      "claims_register":claims_register,"claim_process_controls":claim_controls,
      "loss_event_type_catalog":event_catalog,
      "lineage":{"property_world":"SW-PROPERTY-WORLD-V1","insurance_valuation":"SW-PROPERTY-VALUE-RISK-TAX-V1","building_services":"SW-BUILDING-SERVICES-V1","property_maintenance":"SW-PROPERTY-MAINTENANCE-V1","development_control":"SW-PROPERTY-DEVELOPMENT-CONTROL-V1","property_rights":"SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1"},
      "governance":{
       "insurance":"The existing 420 policy records are indexed, not independently underwritten; full policy wording, exclusions, endorsements and site-specific hazard surveys remain future evidence.",
       "claims":"No claims, loss events, reserves, adjuster decisions, settlements or payments are invented. Operational registers remain empty until a simulated or verified loss event occurs.",
       "assets":"Equipment is scheduled under its parent property policy; no separate equipment sum insured is invented.",
       "maintenance":"Known defects are linked as risk exposures, not asserted to have caused an insured loss.",
       "finance":"Premiums, reserves, settlements and payments are not posted; BP-34 remains the sole financial posting authority.",
       "people":"No person, resident, employee, claimant or adjuster-person records are created; organisational roles only."
      }
    }
    canonical=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    body["manifest_sha256"]=hashlib.sha256(canonical).hexdigest()
    return body
def main():
    root=Path(__file__).resolve().parents[1]
    def load(p): return _expand_columnar(load_json(root/p))
    data=build_insurance_claims(load("data/property/saltwater-property-world-v1.json"),load("data/property/saltwater-property-value-risk-tax-v1.json"),load("data/property/saltwater-building-services-v1.json"),load("data/property/saltwater-property-maintenance-v1.json"),load("data/property/saltwater-property-development-control-v1.json"),load("data/property/saltwater-property-rights-boundaries-v1.json"))
    out=root/"data/property/saltwater-property-insurance-claims-v1.json"
    doc=to_columnar_document(data);doc["schema"]="saltwater-property-insurance-claims-columnar/1.0"
    out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(data["summary"]|{"manifest_sha256":data["manifest_sha256"],"output_bytes":out.stat().st_size},indent=2,sort_keys=True))
if __name__=="__main__":main()
