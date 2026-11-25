import json,unittest
from pathlib import Path
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.building_access_route_corridor_audit import build_route_corridor_candidates
from runtime.terrain_obstacle_survey_coverage_grid import build_coverage_grid
class TerrainObstacleSurveyGridTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=Path(__file__).resolve().parents[2]/"data/geography/saltwater-geography-v1.json"; cls.source=json.loads(p.read_text())
  cls.inventory=build_asset_inventory(cls.source); cls.routes=build_route_corridor_candidates(cls.source,inventory=cls.inventory)
  cls.report=build_coverage_grid(cls.source,cls.inventory["properties"],cls.inventory["buildings"],cls.routes["route_corridors"])
 def test_full_city_partition(self):
  r=self.report; self.assertEqual(r["summary"]["survey_cell_count"],432); self.assertTrue(r["checks"]["grid_area_reconciles_to_city"])
 def test_every_property_and_building_candidate_assigned_once(self):
  s=self.report["summary"]; self.assertEqual(s["property_candidates_assigned"],len(self.inventory["properties"])); self.assertEqual(s["building_candidates_assigned"],len(self.inventory["buildings"]))
 def test_all_assessments_remain_unassessed(self):
  for c in self.report["cells"]:
   self.assertTrue(all(v in ("not_assessed","not_assessed_no_source") for v in c["assessment_state"].values()))
 def test_no_source_is_not_claimed_as_absence_or_approval(self):
  self.assertEqual(self.report["summary"]["cells_with_elevation_source"],0); self.assertFalse(self.report["operational_seed_eligible"])
 def test_all_acceptance_checks_pass(self): self.assertTrue(all(self.report["checks"].values()),self.report["failed_checks"])
if __name__=="__main__": unittest.main()
