import unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.dataset_io import load_json
from runtime.property_lifecycle_transactions_generator import build_property_lifecycle
ROOT = Path(__file__).resolve().parents[2]
def load(p): return _expand_columnar(load_json(ROOT / p))
class PropertyLifecycleTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.world=load("data/property/saltwater-property-world-v1.json")
  cls.tenure=load("data/property/saltwater-property-tenure-v1.json")
  cls.development=load("data/property/saltwater-property-development-control-v1.json")
  cls.data=build_property_lifecycle(cls.world,cls.tenure,cls.development)
 def test_complete_title_register(self):
  d=self.data
  self.assertEqual({x["property_id"] for x in self.world["properties"]},{x["property_id"] for x in d["title_register"]})
  self.assertEqual(len(d["title_register"]),len(self.world["properties"]))
 def test_transaction_index_exactly_references_ownership_source(self):
  d=self.data
  source={x["ownership_event_id"]:x for x in self.tenure["ownership_events"]}
  indexed={x["ownership_event_id"]:x for x in d["property_transactions"]}
  self.assertEqual(set(source),set(indexed))
  self.assertEqual(len(indexed),len(d["property_transactions"]))
  for key,row in indexed.items():
   self.assertEqual(row["transaction_type"],source[key]["event_type"])
   self.assertEqual(row["source_of_truth"],"SW-PROPERTY-TENURE-V1")
 def test_instrument_and_title_references_resolve(self):
  d=self.data
  titles={x["title_register_id"] for x in d["title_register"]}
  events={x["ownership_event_id"] for x in self.tenure["ownership_events"]}
  instruments={x["title_instrument_id"] for x in d["title_instruments"]}
  self.assertEqual(len(instruments),len(d["title_instruments"]))
  self.assertTrue(all(x["title_register_id"] in titles for x in d["title_instruments"]))
  self.assertTrue(all(x["ownership_event_id"] in events for x in d["title_instruments"]))
  self.assertTrue(all(x["title_instrument_id"] in instruments for x in d["property_transactions"]))
 def test_building_and_premises_lineage(self):
  d=self.data
  self.assertEqual({x["building_id"] for x in self.world["buildings"]},{x["building_id"] for x in d["building_lifecycle_events"]})
  self.assertEqual({x["premises_id"] for x in self.world["premises"]},{x["premises_id"] for x in d["premises_lifecycle_events"]})
  self.assertTrue(all(x["planning_permission_id"] for x in d["building_lifecycle_events"]))
  self.assertTrue(all(x["lawful_use_certificate_id"] for x in d["premises_lifecycle_events"]))
 def test_unknown_encumbrances_not_asserted_absent(self):
  self.assertEqual(len(self.data["encumbrance_register"]),len(self.world["properties"]))
  self.assertTrue(all(x["mortgage_or_charge_status"]=="not_asserted" for x in self.data["encumbrance_register"]))
 def test_future_actions_do_not_fabricate_physical_changes(self):
  s=self.data["summary"]
  for k in ("boundary_change_count","subdivision_count","consolidation_count","redevelopment_started_count","demolition_completed_count","change_of_use_completed_count"): self.assertEqual(s[k],0)
  self.assertTrue(all(x["mutates_canonical_baseline"] is False for x in self.data["future_lifecycle_action_rules"]))
 def test_no_financial_or_person_records(self):
  s=self.data["summary"]
  for k in ("financial_postings_created","payments_created","person_records_created","population_records_created"): self.assertEqual(s[k],0)

 def test_all_generated_identifiers_are_unique(self):
  d=self.data
  for collection, key in (
   ("title_register","title_register_id"),("property_interests","property_interest_record_id"),
   ("title_instruments","title_instrument_id"),("property_transactions","property_transaction_id"),
   ("property_lifecycle_events","lifecycle_event_id"),("building_lifecycle_events","lifecycle_event_id"),
   ("premises_lifecycle_events","lifecycle_event_id"),("encumbrance_register","encumbrance_register_id")
  ):
   values=[x[key] for x in d[collection]]
   self.assertEqual(len(values),len(set(values)),f"duplicate {key} in {collection}")
 def test_deterministic(self):
  again=build_property_lifecycle(self.world,self.tenure,self.development)
  self.assertEqual(self.data["manifest_sha256"],again["manifest_sha256"])
if __name__=="__main__": unittest.main()
