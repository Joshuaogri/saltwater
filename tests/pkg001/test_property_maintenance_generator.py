import json, unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_maintenance_generator import build_property_maintenance
ROOT=Path(__file__).resolve().parents[2]
def load(p): return _expand_columnar(json.loads((ROOT/p).read_text()))
class PropertyMaintenanceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.world=load("data/property/saltwater-property-world-v1.json")
  cls.tenure=load("data/property/saltwater-property-tenure-v1.json")
  cls.services=load("data/property/saltwater-building-services-v1.json")
  cls.data=build_property_maintenance(cls.world,cls.tenure,cls.services)
 def test_every_building_has_plan_and_five_cycles(self):
  d=self.data
  self.assertEqual(len(d["maintenance_plans"]),len(self.world["buildings"]))
  self.assertEqual(len(d["maintenance_cycles"]),len(self.world["buildings"])*5)
  self.assertEqual({x["building_id"] for x in d["maintenance_plans"]},{x["building_id"] for x in self.world["buildings"]})
 def test_inspections_cover_every_system_and_site(self):
  d=self.data
  system_ids={x["building_system_id"] for x in self.services["building_systems"]}
  inspected={x["building_system_id"] for x in d["inspections"] if x["building_system_id"]}
  site_ids={x["property_id"] for x in d["inspections"] if x["inspection_type"].startswith("site_")}
  self.assertEqual(system_ids,inspected)
  self.assertEqual(site_ids,{x["property_id"] for x in self.world["properties"]})
 def test_defects_and_work_orders_resolve(self):
  d=self.data
  eq={x["equipment_id"] for x in self.services["equipment_assets"]}
  defects={x["defect_id"] for x in d["defects"]}
  requests={x["work_request_id"] for x in d["work_requests"]}
  orders={x["work_order_id"] for x in d["work_orders"]}
  self.assertTrue(all(x["equipment_id"] in eq for x in d["defects"]))
  self.assertTrue(all(x["equipment_id"] in eq for x in d["warranties"]+d["replacement_forecasts"]))
  self.assertTrue(all(x["defect_id"] in defects for x in d["work_requests"]))
  self.assertTrue(all(x["work_request_id"] in requests for x in d["work_orders"]))
  self.assertTrue(all(x["work_order_id"] in orders for x in d["work_order_lines"]+d["material_issues"]))
 def test_organisations_and_property_foreign_keys_resolve(self):
  d=self.data
  orgs={x["organisation_id"] for x in d["maintenance_contractors"]}|{x["organisation_id"] for x in self.tenure["organisations"]}
  pids={x["property_id"] for x in self.world["properties"]}
  self.assertTrue(all(x["property_id"] in pids for x in d["maintenance_plans"]+d["inspections"]+d["defects"]))
  self.assertTrue(all(x["responsible_contractor_organisation_id"] in orgs for x in d["work_orders"]))
 def test_all_generated_register_identifiers_are_unique(self):
  keys={
   "maintenance_contractors":"organisation_id","maintenance_plans":"maintenance_plan_id",
   "maintenance_cycles":"maintenance_cycle_id","inspections":"inspection_id","defects":"defect_id",
   "work_requests":"work_request_id","work_orders":"work_order_id","work_order_lines":"work_order_line_id",
   "material_issues":"material_issue_id","maintenance_events":"maintenance_event_id","warranties":"warranty_id",
   "replacement_forecasts":"replacement_plan_id","emergency_procedures":"procedure_id"
  }
  for collection, key in keys.items():
   values=[row[key] for row in self.data[collection]]
   self.assertEqual(len(values),len(set(values)),f"{collection} contains duplicate {key}")
   self.assertTrue(all(values),f"{collection} contains an empty {key}")
 def test_no_people_finance_or_population_writes(self):
  s=self.data["summary"]
  self.assertEqual(s["person_records_created"],0); self.assertEqual(s["population_records_created"],0); self.assertEqual(s["financial_postings_created"],0)
  self.assertTrue(all(x["financial_posting_created"] is False for x in self.data["material_issues"]))
 def test_deterministic_manifest(self):
  again=build_property_maintenance(self.world,self.tenure,self.services)
  self.assertEqual(self.data["manifest_sha256"],again["manifest_sha256"])
 def test_columnar_round_trip_counts(self):
  from runtime.property_world_generator import to_columnar_document
  doc=to_columnar_document(self.data)
  self.assertEqual(doc["metadata"]["summary"],self.data["summary"])
if __name__=="__main__": unittest.main()
