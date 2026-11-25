import json,unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_value_risk_tax_generator import build_property_value_risk
ROOT=Path(__file__).resolve().parents[2]
def load(p): return _expand_columnar(json.loads((ROOT/p).read_text()))
class PropertyValueRiskTaxTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  def get(p): return load(p)
  cls.world=get("data/property/saltwater-property-world-v1.json")
  cls.tenure=get("data/property/saltwater-property-tenure-v1.json")
  cls.services=get("data/property/saltwater-building-services-v1.json")
  cls.maintenance=get("data/property/saltwater-property-maintenance-v1.json")
  cls.security=get("data/property/saltwater-property-security-access-v1.json")
  cls.data=build_property_value_risk(cls.world,cls.tenure,cls.services,cls.maintenance,cls.security)
 def test_every_property_assessed_and_insured(self):
  ids={x["property_id"] for x in self.world["properties"]}
  self.assertEqual(ids,{x["property_id"] for x in self.data["land_valuations"]})
  self.assertEqual(ids,{x["property_id"] for x in self.data["insurance_policies"]})
  self.assertEqual(ids,{x["property_id"] for x in self.data["property_tax_assessments"]})
 def test_building_and_premises_valuation_links(self):
  d=self.data
  self.assertEqual({x["building_id"] for x in self.world["buildings"]},{x["building_id"] for x in d["improvement_valuations"]})
  self.assertEqual({x["premises_id"] for x in self.world["premises"]},{x["premises_id"] for x in d["premises_valuations"]})
  self.assertTrue(all(x["land_valuation_id"] in {v["land_valuation_id"] for v in d["land_valuations"]} for x in d["asset_valuations"]))
 def test_condition_uses_existing_defect_and_system_baseline(self):
  d=self.data
  self.assertEqual(len(d["condition_assessments"]),len(self.world["properties"])+len(self.world["buildings"]))
  self.assertTrue(all(x["assessment_tick"]==0 for x in d["condition_assessments"]))
 def test_tax_is_assessed_not_billed(self):
  self.assertTrue(all(x["assessment_status"]=="assessed_not_billed" for x in self.data["property_tax_assessments"]))
  self.assertEqual(self.data["summary"]["invoices_created"],0)
  self.assertEqual(self.data["summary"]["payments_created"],0)
 def test_insurance_links_and_coverage(self):
  policies={x["insurance_policy_id"] for x in self.data["insurance_policies"]}
  self.assertTrue(all(x["insurance_policy_id"] in policies for x in self.data["insurance_coverages"]))
  self.assertEqual(len(self.data["insurance_coverages"]),3*len(policies))
 def test_no_person_or_financial_transactions(self):
  s=self.data["summary"]
  for key in ("person_records_created","population_records_created","claims_created","financial_postings_created","invoices_created","payments_created"): self.assertEqual(s[key],0)
 def test_deterministic(self):
  again=build_property_value_risk(self.world,self.tenure,self.services,self.maintenance,self.security)
  self.assertEqual(self.data["manifest_sha256"],again["manifest_sha256"])
if __name__=="__main__": unittest.main()
