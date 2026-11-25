"""Generate property condition, valuation, insurance and tax assessment records."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR="SW-PROPERTY-VALUATION-RISK-TAX-001"
def _n(k,lo,hi):
 d=hashlib.sha256(k.encode()).digest()
 return lo+int.from_bytes(d[:4],"big")%(hi-lo+1)
def _slug(v): return "".join(c for c in str(v).upper() if c.isalnum())[:24]
def _pick(v,k): return v[_n(k,0,len(v)-1)]
def _band(v):
 if v<5_000_000:return "under_5m"
 if v<20_000_000:return "5m_to_20m"
 if v<100_000_000:return "20m_to_100m"
 if v<500_000_000:return "100m_to_500m"
 if v<2_000_000_000:return "500m_to_2bn"
 return "2bn_plus"
def build_property_value_risk(world,tenure,services,maintenance,security):
 props={x["property_id"]:x for x in world["properties"]}
 buildings={x["building_id"]:x for x in world["buildings"]}
 premises={x["premises_id"]:x for x in world["premises"]}
 units={x["unit_id"]:x for x in world["units"]}
 owners={x["property_id"]:x["owner_organisation_id"] for x in tenure["current_ownership_interests"]}
 managers={x["property_id"]:x["manager_organisation_id"] for x in tenure["management_appointments"]}
 equipment=services["equipment_assets"]
 defects=maintenance["defects"]
 defects_by_building={}
 for d in defects: defects_by_building.setdefault(d["building_id"],[]).append(d)
 systems_by_building={}
 for s in services["building_systems"]: systems_by_building.setdefault(s["building_id"],[]).append(s)
 access_by_property={}
 for d in security["doors"]: access_by_property.setdefault(d["property_id"],[]).append(d)
 building_by_property={}
 for b in buildings.values(): building_by_property.setdefault(b["property_id"],[]).append(b)
 # Fictional currency is a simulation unit, not a real-world market quote.
 currency="SWC"
 condition=[]; land_values=[]; improvements=[]; valuations=[]; premises_values=[]
 policies=[]; coverages=[]; risks=[]; assessments=[]; tax_rules=[]; exemptions=[]
 use_multipliers={"port_maritime":18,"warehouse":8,"industrial":12,"healthcare":14,"transport":16,"data_centre":20,"financial":22,"commercial":10,"residential":3,"office":9,"hospitality":11}
 for pid,p in sorted(props.items()):
  bs=building_by_property.get(pid,[])
  area=max(1,int(p.get("site_area_sqm") or p.get("area_sqm") or 800))
  site_grade=_pick(["prime_harbour","central_commercial","institutional","mixed_use","residential","industrial_estate"],pid+"land")
  land_rate={"prime_harbour":180000,"central_commercial":145000,"institutional":70000,"mixed_use":85000,"residential":42000,"industrial_estate":55000}[site_grade]
  land_value=area*land_rate*_n(pid+"landfactor",85,125)//100
  land_values.append({"land_valuation_id":f"SWLANDVAL-{_slug(pid)}","property_id":pid,"valuation_basis":"fictional_capital_city_mass_appraisal","land_use_profile":site_grade,"site_area_sqm":area,"rate_per_sqm_swc":land_rate,"assessed_land_value_swc":land_value,"valuation_tick":0,"valuation_status":"baseline_assessed"})
  prop_condition=_pick(["excellent","good","serviceable","fair","poor"],pid+"condition")
  condition.append({"condition_assessment_id":f"SWPCOND-{_slug(pid)}","property_id":pid,"building_id":None,"assessment_scope":"site_boundary_access_drainage_external_areas","condition_grade":prop_condition,"observed_risk_profiles":["coastal_salt_exposure","intense_rainfall_drainage","high_urban_utilisation"],"assessment_tick":0,"evidence_basis":"deterministic_baseline_asset_profile","follow_up_required":prop_condition in ("poor","fair")})
  total_improvement=0
  for b in sorted(bs,key=lambda x:x["building_id"]):
   bid=b["building_id"]; use=b.get("building_use","commercial")
   multiplier=use_multipliers.get(use,7)
   floors=max(1,int(b.get("floor_count") or b.get("storeys") or 3))
   footprint=max(100,area//max(1,len(bs)))
   gross=footprint*floors
   base= gross*multiplier*125000
   value=base*_n(bid+"quality",82,128)//100
   total_improvement+=value
   bd=_pick(["excellent","good","serviceable","fair","poor"],bid+"condition")
   linked=defects_by_building.get(bid,[])
   condition.append({"condition_assessment_id":f"SWBCOND-{_slug(bid)}","property_id":pid,"building_id":bid,"assessment_scope":"structure_envelope_services_fire_security_vertical_transport_and_access","condition_grade":bd,"gross_floor_area_sqm":gross,"system_count":len(systems_by_building.get(bid,[])),"open_defect_count":sum(x["defect_status"]=="open" for x in linked),"critical_defect_count":sum(x["severity"]=="critical" and x["defect_status"]=="open" for x in linked),"assessment_tick":0,"evidence_basis":"building_system_and_maintenance_baseline","follow_up_required":bd in ("poor","fair") or any(x["severity"]=="critical" and x["defect_status"]=="open" for x in linked)})
   improvements.append({"improvement_valuation_id":f"SWIMPRVAL-{_slug(bid)}","property_id":pid,"building_id":bid,"building_use":use,"gross_floor_area_sqm":gross,"construction_quality_profile":_pick(["standard","enhanced","premium","critical_infrastructure"],bid+"build"),"replacement_value_swc":value,"depreciation_profile":_pick(["newer","midlife","mature","older"],bid+"age"),"valuation_tick":0})
   valuations.append({"asset_valuation_id":f"SWASSETVAL-{_slug(bid)}","property_id":pid,"building_id":bid,"land_valuation_id":f"SWLANDVAL-{_slug(pid)}","improvement_valuation_id":f"SWIMPRVAL-{_slug(bid)}","valuation_purpose":"insurance_reinstatement_and_asset_register","currency":currency,"assessed_value_swc":value,"value_band":_band(value),"valuation_method":"replacement_cost_less_condition_and_obsolescence_adjustment","valuation_tick":0,"valuation_status":"baseline_assessed"})
   for pr in [x for x in premises.values() if x.get("building_id")==bid]:
    pid2=pr["premises_id"]; pv=max(250000,value//max(1,sum(1 for z in premises.values() if z.get("building_id")==bid)))
    premises_values.append({"premises_valuation_id":f"SWPREMVAL-{_slug(pid2)}","property_id":pid,"building_id":bid,"premises_id":pid2,"valuation_basis":"allocated_building_improvement_value","assessed_value_swc":pv,"value_band":_band(pv),"valuation_tick":0})
  total=land_value+total_improvement
  valuations.append({"asset_valuation_id":f"SWPROPVAL-{_slug(pid)}","property_id":pid,"building_id":None,"land_valuation_id":f"SWLANDVAL-{_slug(pid)}","improvement_valuation_id":None,"valuation_purpose":"whole_property_capital_asset_register","currency":currency,"assessed_value_swc":total,"value_band":_band(total),"valuation_method":"land_plus_aggregated_improvement_replacement_value","valuation_tick":0,"valuation_status":"baseline_assessed"})
  risk=_pick(["standard_commercial","high_value_corporate","port_and_marine_adjacent","industrial_specialist","critical_infrastructure","residential_multiperil"],pid+"risk")
  insurer=f"SWORG-INS-{_n(pid+'insurer',1,5):02d}"
  policy_id=f"SWPOL-{_slug(pid)}"
  policies.append({"insurance_policy_id":policy_id,"property_id":pid,"policyholder_organisation_id":owners[pid],"insured_property_manager_organisation_id":managers[pid],"insurer_organisation_id":insurer,"policy_type":"commercial_property_all_risks_with_specialist_extensions","policy_status":"in_force","effective_tick":0,"renewal_interval_days":365,"currency":currency,"sum_insured_swc":total,"deductible_band":_pick(["standard","elevated","high"],pid+"deductible"),"premium_calculation":"rated_by_risk_profile_and_sum_insured_not_posted","claim_history":"no_historical_claims_fabricated"})
  coverages.append({"coverage_id":f"SWCOV-{_slug(pid)}-01","insurance_policy_id":policy_id,"coverage_type":"property_damage_and_reinstatement","limit_swc":total,"coverage_state":"included"})
  coverages.append({"coverage_id":f"SWCOV-{_slug(pid)}-02","insurance_policy_id":policy_id,"coverage_type":"business_interruption_and_rent_loss","limit_swc":total//2,"coverage_state":"included"})
  coverages.append({"coverage_id":f"SWCOV-{_slug(pid)}-03","insurance_policy_id":policy_id,"coverage_type":"flood_storm_surge_and_coastal_perils","limit_swc":total//2,"coverage_state":"subject_to_location_specific_sub_limit"})
  risks.append({"property_risk_id":f"SWRISK-{_slug(pid)}","property_id":pid,"insurance_policy_id":policy_id,"risk_profile":risk,"risk_factors":["coastal_weather","fire_and_electrical","water_ingress","business_interruption","security_and_access"],"mitigation_links":["SW-PROPERTY-MAINTENANCE-V1","SW-PROPERTY-SECURITY-ACCESS-V1"],"risk_review_interval_days":365,"review_status":"baseline_profile"})
  tax_base=total
  tax_rate_bp={"prime_harbour":125,"central_commercial":110,"institutional":55,"mixed_use":85,"residential":65,"industrial_estate":95}[site_grade]
  annual=tax_base*tax_rate_bp//10000
  assessments.append({"property_tax_assessment_id":f"SWTAX-{_slug(pid)}-2026","property_id":pid,"liable_organisation_id":owners[pid],"tax_year":2026,"tax_base_swc":tax_base,"tax_rate_basis_points":tax_rate_bp,"assessed_annual_tax_swc":annual,"assessment_status":"assessed_not_billed","appeal_status":"not_lodged","assessment_tick":0,"currency":currency})
  exemptions.append({"tax_exemption_review_id":f"SWTEX-{_slug(pid)}","property_id":pid,"review_state":"screened_no_exemption_assumed","exemption_reason":None,"effective_tax_year":2026})
 insurers=[{"organisation_id":f"SWORG-INS-{i:02d}","display_name":name,"organisation_type":"property_insurer","status":"active","fictional_entity":True} for i,name in enumerate(["Saltwater Mutual Assurance","Meridian Global Property Underwriters","Harbour and Trade Risk Corporation","Continental Commercial Indemnity","Civic Infrastructure Assurance"],1)]
 tax_rules=[{"tax_rule_id":"SWTAX-RULE-2026","tax_year":2026,"rule_type":"annual_ad_valorem_property_assessment","currency":currency,"collection_cycle":"annual","billing_and_payment_authority":"BP-34","effective_tick":0,"fictional_rule":True}]
 body={"schema":"saltwater-property-value-risk-tax/1.0","dataset_id":"SW-PROPERTY-VALUE-RISK-TAX-V1","canon_status":"CANONICAL_FICTIONAL_GAME_WORLD","generator":GENERATOR,"effective_tick":0,"city":"Saltwater","summary":{"property_count":len(props),"building_count":len(buildings),"condition_assessment_count":len(condition),"land_valuation_count":len(land_values),"improvement_valuation_count":len(improvements),"asset_valuation_count":len(valuations),"premises_valuation_count":len(premises_values),"insurance_policy_count":len(policies),"coverage_count":len(coverages),"property_risk_profile_count":len(risks),"property_tax_assessment_count":len(assessments),"tax_exemption_review_count":len(exemptions),"insurer_organisation_count":len(insurers),"tax_rule_count":len(tax_rules),"person_records_created":0,"population_records_created":0,"claims_created":0,"financial_postings_created":0,"invoices_created":0,"payments_created":0},"condition_assessments":condition,"land_valuations":land_values,"improvement_valuations":improvements,"asset_valuations":valuations,"premises_valuations":premises_values,"insurance_policies":policies,"insurance_coverages":coverages,"property_risks":risks,"insurer_organisations":insurers,"property_tax_assessments":assessments,"tax_exemption_reviews":exemptions,"tax_rules":tax_rules,"lineage":{"property_world_dataset":"SW-PROPERTY-WORLD-V1","property_tenure_dataset":"SW-PROPERTY-TENURE-V1","building_services_dataset":"SW-BUILDING-SERVICES-V1","property_maintenance_dataset":"SW-PROPERTY-MAINTENANCE-V1","property_security_dataset":"SW-PROPERTY-SECURITY-ACCESS-V1"},"gameplay":{"valuation":"Land, building improvements, whole-property assets and individual premises receive linked fictional SWC valuations.","condition":"Site and building condition assessments use the persisted system and defect baseline; first gameplay inspections remain future events.","insurance":"Policies cover reinstatement, interruption and coastal perils; no fabricated claims or premiums are posted.","taxation":"Annual 2026 assessments are calculated but remain assessed-not-billed; exemptions are explicitly reviewed without inventing entitlement.","finance_boundary":"No invoices, premiums, tax bills, receivables, payments, claims settlements, journal entries or financial postings are created; BP-34 owns transactions.","population":"No people, residents, employees or population records are created."}}
 canonical=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(); body["manifest_sha256"]=hashlib.sha256(canonical).hexdigest()
 return body
def main():
 root=Path(__file__).resolve().parents[1]
 def load(p): return _expand_columnar(json.loads((root/p).read_text(encoding="utf-8")))
 data=build_property_value_risk(load("data/property/saltwater-property-world-v1.json"),load("data/property/saltwater-property-tenure-v1.json"),load("data/property/saltwater-building-services-v1.json"),load("data/property/saltwater-property-maintenance-v1.json"),load("data/property/saltwater-property-security-access-v1.json"))
 out=root/"data/property/saltwater-property-value-risk-tax-v1.json"; doc=to_columnar_document(data); doc["schema"]="saltwater-property-value-risk-tax-columnar/1.0"
 out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps(data["summary"]|{"manifest_sha256":data["manifest_sha256"],"output_bytes":out.stat().st_size},indent=2,sort_keys=True))
if __name__=="__main__": main()
