import json, unittest
from pathlib import Path
from shapely.geometry import shape
from runtime.terrain_obstacle_detail_register import build_detail_register
class TerrainObstacleDetailRegisterTests(unittest.TestCase):
 def setUp(self):
  p=Path(__file__).resolve().parents[2]/"data/geography/saltwater-geography-v1.json"; self.source=json.loads(p.read_text())
 def test_current_terrain_geometry_detailed_without_elevation_inference(self):
  r=build_detail_register(self.source); self.assertEqual(len(r["terrain_records"]),1); t=r["terrain_records"][0]; g=shape(t["source_geometry"])
  self.assertAlmostEqual(t["planar_area_m2"],g.area,places=2); self.assertAlmostEqual(t["planar_perimeter_m"],g.length,places=2)
  self.assertEqual(t["exterior_vertex_count"],9); self.assertTrue(all(e["planar_length_m"]>0 for ring in t["boundary_rings"] for e in ring["edges"]))
  self.assertIsNone(t["elevation_m"]); self.assertIsNone(t["gradient_degrees"]); self.assertEqual(t["traversal_restriction"],"unknown")
 def test_neighbourhood_overlay_reconciles(self):
  t=build_detail_register(self.source)["terrain_records"][0]
  self.assertAlmostEqual(sum(x["intersection_area_m2"] for x in t["neighbourhood_intersections"]),t["planar_area_m2"],places=2)
 def test_obstacle_gaps_are_not_claimed_absent(self):
  r=build_detail_register(self.source); self.assertEqual(r["obstacle_records"],[])
  for k in ("wall","fence","gate","drainage_structure","retaining_structure"):
   self.assertEqual(r["source_coverage"][k]["source_record_count"],0); self.assertFalse(r["source_coverage"][k]["absence_claim"])
 def test_route_overlay_preserves_lineage(self):
  route={"candidate_route_corridor_id":"RC-1","source_connector_candidate_id":"C-1","centreline_geometry":{"type":"LineString","coordinates":[[3400,3000],[5900,6200]]}}
  hits=build_detail_register(self.source,[route])["terrain_records"][0]["route_corridor_intersections"]
  self.assertEqual(len(hits),1); self.assertEqual(hits[0]["candidate_route_corridor_id"],"RC-1")
 def test_duplicate_ids_rejected(self):
  f1={"id":"X","geometry":{"type":"Point","coordinates":[0,0]},"properties":{"entity_type":"wall"}}
  f2={"id":"X","geometry":{"type":"Point","coordinates":[1,1]},"properties":{"entity_type":"gate"}}
  with self.assertRaises(ValueError): build_detail_register({"dataset_id":"T","features":[f1,f2]})
if __name__=="__main__": unittest.main()
