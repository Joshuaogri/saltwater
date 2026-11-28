import gzip,json,unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_insurance_claims_generator import build_insurance_claims
ROOT=Path(__file__).resolve().parents[2]
def load(path):
 p=ROOT/path
 if p.exists():
  document=json.loads(p.read_text(encoding="utf-8"))
 else:
  compressed=p.with_suffix(p.suffix+".gz")
  with gzip.open(compressed,"rt",encoding="utf-8") as handle:
   document=json.load(handle)
 return _expand_columnar(document)
class PropertyInsuranceClaimsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.world=load("data/property/saltwater-property-world-v1.json")
  cls.insurance=load("data/property/saltwater-property-value-risk-tax-v1.json")
  cls.services=load("data/property/saltwater-building-services-v1.json")
  cls.maintenance=load("data/property/saltwater-property-maintenance-v1.json")
  cls.development=load("data/property/saltwater-property-development-control-v1.json")
  cls.rights=load("data/property/saltwater-property-rights-boundaries-v1.json")
  cls.data=build_insurance_claims(cls.world,cls.insurance,cls.services,cls.maintenance,cls.development,cls.rights)
 def test_all_policies_are_indexed_once(self):
  d=self.data; src={x["property_id"]:x for x in self.insurance["insurance_policies"]}
  out={x["property_id"]:x for x in d["policy_exposures"]}
  self.assertEqual(set(src),set(out));self.assertEqual(len(out),len(d["policy_exposures"]))
  for pid,row in out.items(): self.assertEqual(row["insurance_policy_id"],src[pid]["insurance_policy_id"])
 def test_building_and_equipment_schedules_cover_all_assets(self):
  self.assertEqual({x["building_id"] for x in self.world["buildings"]},{x["building_id"] for x in self.data["building_insurance_schedules"]})
  self.assertEqual({x["equipment_id"] for x in self.services["equipment_assets"]},{x["equipment_id"] for x in self.data["equipment_insurance_schedules"]})
 def test_defects_link_without_asserting_claim_causation(self):
  source={x["defect_id"] for x in self.maintenance["defects"]}
  output={x["defect_id"] for x in self.data["defect_exposure_register"]}
  self.assertEqual(source,output)
  self.assertTrue(all(x["claim_causation"]=="not_assessed" and x["insurable_loss"]=="not_asserted" for x in self.data["defect_exposure_register"]))
 def test_perils_resolve_to_policy_and_property(self):
  policies={x["insurance_policy_id"] for x in self.insurance["insurance_policies"]}
  self.assertTrue(self.data["peril_assessments"])
  self.assertTrue(all(x["insurance_policy_id"] in policies for x in self.data["peril_assessments"]))
  self.assertTrue(all(x["policy_exclusion_status"]=="unknown_until_wording_review" for x in self.data["peril_assessments"]))
 def test_no_fabricated_losses_claims_or_financial_activity(self):
  s=self.data["summary"]
  for k in ("claims_register_count","loss_event_register_count","claim_reserve_count","claim_payment_count","settlement_count","premium_posting_count","financial_postings_created","person_records_created","population_records_created"):self.assertEqual(s[k],0)
  self.assertEqual(self.data["claims_register"],[]);self.assertEqual(self.data["loss_event_register"],[])
 def test_claim_process_and_event_catalog_are_operationally_defined(self):
  self.assertEqual(len(self.data["claim_process_controls"]),10)
  self.assertGreaterEqual(len(self.data["loss_event_type_catalog"]),12)
  self.assertTrue(all(x["required_links"] for x in self.data["loss_event_type_catalog"]))
 def test_equipment_is_not_double_insured(self):
  self.assertTrue(all(x["specific_equipment_sum_insured_swc"] is None for x in self.data["equipment_insurance_schedules"]))
  self.assertTrue(all(x["valuation_state"]=="included_within_building_or_property_schedule_not_separately_valued" for x in self.data["equipment_insurance_schedules"]))
 def test_deterministic(self):
  other=build_insurance_claims(self.world,self.insurance,self.services,self.maintenance,self.development,self.rights)
  self.assertEqual(self.data["manifest_sha256"],other["manifest_sha256"])
if __name__=="__main__":unittest.main()
