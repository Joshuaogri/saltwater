import json,unittest
from pathlib import Path
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_security_access_generator import build_property_security
ROOT=Path(__file__).resolve().parents[2]
def load(p): return _expand_columnar(json.loads((ROOT/p).read_text()))
class PropertySecurityAccessTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.world=load("data/property/saltwater-property-world-v1.json"); cls.tenure=load("data/property/saltwater-property-tenure-v1.json"); cls.services=load("data/property/saltwater-building-services-v1.json")
  cls.data=build_property_security(cls.world,cls.tenure,cls.services)
 def test_every_access_point_has_door_and_lock(self):
  d=self.data; aids={x["access_point_id"] for x in self.world["access_points"]}
  self.assertEqual(aids,{x["access_point_id"] for x in d["doors"]}); self.assertEqual(aids,{x["access_point_id"] for x in d["locks"]})
  self.assertEqual(len(d["doors"]),len(aids)); self.assertEqual(len(d["locks"]),len(aids))
 def test_lock_hardware_and_keys_resolve(self):
  d=self.data; locks={x["lock_id"] for x in d["locks"]}
  self.assertTrue(all(x["lock_id"] in locks for x in d["key_cylinders"]))
  cylinders={x["cylinder_id"] for x in d["key_cylinders"]}
  self.assertTrue(all(x["cylinder_id"] in cylinders for x in d["physical_keys"]))
  self.assertTrue(all(x["lock_id"] in locks for x in d["security_devices"]))
 def test_zone_hierarchy_covers_buildings_premises_and_units(self):
  d=self.data; zones={x["access_zone_id"] for x in d["access_zones"]}
  self.assertTrue(all(f"SWZ-{''.join(c for c in x['building_id'].upper() if c.isalnum())[:24]}-ENTRY" in zones for x in self.world["buildings"]))
  self.assertEqual({x["premises_id"] for x in d["access_zones"] if x["zone_type"]=="premises_occupancy"},{x["premises_id"] for x in self.world["premises"]})
  self.assertEqual({x["unit_id"] for x in d["access_zones"] if x["zone_type"]=="individual_unit"},{x["unit_id"] for x in self.world["units"]})
 def test_business_assignments_follow_current_occupancy(self):
  d=self.data; occ={x["occupancy_id"] for x in self.tenure["occupancies"]}
  self.assertEqual(len(d["organisation_access_assignments"]),len(self.tenure["occupancies"]))
  self.assertTrue(all(x["occupancy_id"] in occ for x in d["organisation_access_assignments"]))
  self.assertTrue(all(not x["member_person_ids"] for x in d["access_groups"]))
 def test_door_routes_and_maintenance_linkage(self):
  d=self.data; route_ids={x["route_id"] for x in self.world["access_routes"]}
  self.assertTrue(all(x["route_id"] in route_ids for x in d["doors"] if x["route_id"]))
  self.assertTrue(all(x["access_point_id"] in {a["access_point_id"] for a in self.world["access_points"]} for x in d["access_policies"] if x.get("access_point_id")))
 def test_no_person_finance_or_population_records(self):
  s=self.data["summary"]
  self.assertEqual(s["person_credentials_created"],0); self.assertEqual(s["person_records_created"],0); self.assertEqual(s["population_records_created"],0); self.assertEqual(s["financial_postings_created"],0)
  self.assertTrue(all(x.get("issue_to_person_id") is None for x in self.data["physical_keys"]))
 def test_deterministic_output(self):
  again=build_property_security(self.world,self.tenure,self.services)
  self.assertEqual(self.data["manifest_sha256"],again["manifest_sha256"])
if __name__=="__main__":unittest.main()
