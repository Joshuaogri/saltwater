import json, unittest
from pathlib import Path
from runtime.terrain_obstacle_source_model import build_source_inventory

class TerrainObstacleSourceModelTests(unittest.TestCase):
 def test_current_source_inventory(self):
  p=Path(__file__).resolve().parents[2]/"data/geography/saltwater-geography-v1.json"; raw=p.read_bytes()
  r=build_source_inventory(json.loads(raw),raw); s=r["summary"]
  self.assertEqual(s["terrain_features"],1); self.assertEqual(s["elevation_surfaces"],0)
  self.assertEqual(s["contour_lines"],0); self.assertEqual(s["walls"],0); self.assertEqual(s["fences"],0)
  self.assertEqual(s["gates"],0); self.assertEqual(s["drainage_structures"],0)
  self.assertEqual(s["gradient_assessed_count"],0); self.assertEqual(s["traversability_assessed_count"],0)
  self.assertTrue(all(r["checks"].values())); self.assertFalse(r["operational_seed_eligible"])
 def test_ridge_does_not_infer_elevation_or_slope(self):
  src={"dataset_id":"TEST-1","features":[{"id":"RIDGE-1","geometry":{"type":"Polygon","coordinates":[[[0,0],[2,0],[2,2],[0,2],[0,0]]]},"properties":{"entity_type":"terrain_feature","terrain":"low_ridge"}}]}
  row=build_source_inventory(src)["records"][0]
  self.assertIsNone(row["elevation_m"]); self.assertIsNone(row["gradient_degrees"]); self.assertEqual(row["traversal_restriction"],"unknown")
 def test_obstacle_keeps_missing_attributes_unknown(self):
  src={"dataset_id":"TEST-2","features":[{"id":"WALL-1","geometry":{"type":"LineString","coordinates":[[0,0],[1,1]]},"properties":{"entity_type":"wall"}}]}
  row=build_source_inventory(src)["records"][0]
  self.assertIsNone(row["height_m"]); self.assertIsNone(row["width_m"]); self.assertIsNone(row["material"])
  self.assertEqual(row["condition"],"not_assessed"); self.assertEqual(row["pedestrian_passability"],"not_assessed")
 def test_duplicate_ids_rejected(self):
  f={"id":"DUP","geometry":{"type":"Point","coordinates":[0,0]},"properties":{"entity_type":"gate"}}
  with self.assertRaises(ValueError): build_source_inventory({"dataset_id":"TEST-3","features":[f,f]})
if __name__=="__main__": unittest.main()
