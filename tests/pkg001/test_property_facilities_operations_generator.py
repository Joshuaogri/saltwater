import json,unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_facilities_operations_generator import build_facilities_operations
ROOT=Path(__file__).resolve().parents[2]
def load(path): return _expand_columnar(json.loads((ROOT/path).read_text()))
class FacilitiesOperationsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.world=load("data/property/saltwater-property-world-v1.json")
  cls.tenure=load("data/property/saltwater-property-tenure-v1.json")
  cls.services=load("data/property/saltwater-building-services-v1.json")
  cls.maintenance=load("data/property/saltwater-property-maintenance-v1.json")
  cls.data=build_facilities_operations(cls.world,cls.tenure,cls.services,cls.maintenance)
 def test_all_properties_have_facilities_contracts(self):
  expected={x["property_id"] for x in self.world["properties"]}
  actual={x["property_id"] for x in self.data["facilities_contracts"]}
  self.assertEqual(expected,actual)
 def test_schedules_resolve_to_existing_assets(self):
  bids={x["building_id"] for x in self.world["buildings"]}
  pids={x["premises_id"] for x in self.world["premises"]}
  for x in self.data["service_schedules"]:
   if x["building_id"]: self.assertIn(x["building_id"],bids)
   if x["premises_id"]: self.assertIn(x["premises_id"],pids)
   self.assertIn(x["service_type"],{s[0] for s in __import__("runtime.property_facilities_operations_generator",fromlist=["SERVICES"]).SERVICES})
 def test_contract_sla_and_schedule_links_resolve(self):
  c={x["facilities_contract_id"] for x in self.data["facilities_contracts"]}
  self.assertTrue(all(x["facilities_contract_id"] in c for x in self.data["service_level_agreements"]))
  self.assertTrue(all(x["service_contract_id"] in c for x in self.data["service_schedules"]))
 def test_unit_reconciliation_does_not_hide_mismatch(self):
  r=self.data["unit_count_reconciliation"]
  self.assertEqual(r["property_development_control_unit_count"],62585)
  self.assertIn(r["reconciliation_status"],("reconciled","mismatch_preserved_for_reconciliation"))
  self.assertEqual(r["world_vs_tenure_missing_unit_count"],len({x["unit_id"] for x in self.world["units"]}-{x["unit_id"] for x in self.tenure["unit_occupancy_states"]}))
 def test_no_fabricated_visits_requests_or_finance(self):
  d=self.data
  self.assertEqual(d["service_requests"],[])
  self.assertEqual(d["service_visits"],[])
  self.assertEqual(d["supplier_performance_actuals"],[])
  for key in ("service_request_count","completed_service_visit_count","measured_sla_actual_count","invoice_count","payment_count","financial_postings_created","person_records_created","population_records_created"):
   self.assertEqual(d["summary"][key],0)
 def test_deterministic(self):
  other=build_facilities_operations(self.world,self.tenure,self.services,self.maintenance)
  self.assertEqual(self.data["manifest_sha256"],other["manifest_sha256"])
if __name__=="__main__": unittest.main()
