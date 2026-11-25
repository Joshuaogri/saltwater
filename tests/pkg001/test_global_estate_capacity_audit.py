import json,unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.global_estate_capacity_audit import build_estate_capacity_audit
ROOT=Path(__file__).resolve().parents[2]
def load(path): return _expand_columnar(json.loads((ROOT/path).read_text()))
class GlobalEstateCapacityAuditTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.geo=json.loads((ROOT/"data/geography/saltwater-geography-v1.json").read_text())
  cls.world=load("data/property/saltwater-property-world-v1.json")
  cls.businesses=load("data/business/saltwater-business-registry-v1.json")
  cls.data=build_estate_capacity_audit(cls.geo,cls.world,cls.businesses)
 def test_source_totals_reconcile(self):
  s=self.data["summary"]
  self.assertEqual(s["property_site_count"],len(self.world["properties"]))
  self.assertEqual(s["building_count"],len(self.world["buildings"]))
  self.assertEqual(s["premises_count"],len(self.world["premises"]))
  self.assertEqual(s["unit_count"],len(self.world["units"]))
  self.assertEqual(s["business_count"],len(self.businesses["businesses"]))
  self.assertEqual(s["establishment_count"],len(self.businesses["establishments"]))
 def test_floor_area_and_height_are_source_derived(self):
  s=self.data["summary"]
  self.assertEqual(s["maximum_storeys_above"],max(x["storeys_above"] for x in self.world["buildings"]))
  self.assertEqual(s["gross_floor_area_m2"],round(sum(x["gross_floor_area_m2"] for x in self.world["buildings"]),3))
  self.assertGreater(s["gross_floor_area_m2"],0)
 def test_district_asset_totals_reconcile(self):
  rows=self.data["summary"]["district_asset_registers"]
  self.assertEqual(sum(x["properties"] for x in rows),len(self.world["properties"]))
  self.assertEqual(sum(x["buildings"] for x in rows),len(self.world["buildings"]))
  self.assertEqual(sum(x["units"] for x in rows),len(self.world["units"]))
  self.assertEqual(sum(x["establishments"] for x in rows),len(self.businesses["establishments"]))
 def test_global_hub_scale_gap_is_explicit(self):
  findings={x["finding_id"]:x for x in self.data["capacity_findings"]}
  self.assertEqual(findings["ESTATE-001"]["severity"],"high")
  self.assertEqual(findings["ESTATE-002"]["severity"],"high")
  self.assertEqual(findings["ESTATE-003"]["severity"],"high")
  self.assertEqual(self.data["design_constraints"]["population_cap"],10000)
  self.assertGreaterEqual(self.data["summary"]["buildings_at_least_20_storeys"],1)
  self.assertEqual(self.data["summary"]["vertical_profile_code"],"GLOBAL-ESTATE-VERTICAL-V1")
  self.assertTrue(self.data["design_constraints"]["one_city_only"])
 def test_audit_does_not_create_people_or_change_world(self):
  self.assertEqual(self.data["summary"]["people_records_created"],0)
  self.assertEqual(self.data["summary"]["population_records_created"],0)
  self.assertTrue(self.data["design_constraints"]["no_geometry_mutated"])
  self.assertTrue(self.data["design_constraints"]["no_operational_property_records_created"])
 def test_deterministic(self):
  other=build_estate_capacity_audit(self.geo,self.world,self.businesses)
  self.assertEqual(self.data["manifest_sha256"],other["manifest_sha256"])
if __name__=="__main__": unittest.main()
