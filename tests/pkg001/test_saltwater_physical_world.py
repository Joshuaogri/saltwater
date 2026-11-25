import json
import unittest
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, shape


ROOT = Path(__file__).resolve().parents[2]


class SaltwaterPhysicalWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = json.loads((ROOT / "data/geography/saltwater-physical-world-v1.json").read_text())
        cls.geography = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())
        cls.neighbourhoods = {
            n["id"]: shape(n["geometry"]) for n in cls.geography["neighbourhoods"]
        }

    def test_world_is_canonical_fictional_dataset(self):
        self.assertEqual(self.world["dataset_id"], "SW-PHYS-V1")
        self.assertEqual(self.world["canon_status"], "CANONICAL_FICTIONAL_GAME_WORLD")
        self.assertFalse(self.world["coordinate_reference"]["real_world_coordinates"])

    def test_terrain_zone_ids_unique_and_geometries_valid(self):
        rows = self.world["terrain_zones"]
        ids = [r["terrain_zone_id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        for row in rows:
            geom = shape(row["geometry"])
            self.assertTrue(geom.is_valid)
            self.assertGreater(geom.area, 0)
            self.assertLessEqual(row["elevation"]["minimum_m"], row["elevation"]["maximum_m"])
            self.assertEqual(row["elevation"]["vertical_datum"], "SW-VERT-01")

    def test_physical_feature_ids_unique_and_parent_neighbourhoods_exist(self):
        rows = self.world["physical_features"]
        ids = [r["physical_feature_id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        for row in rows:
            self.assertIn(row["neighbourhood_id"], self.neighbourhoods)

    def test_physical_feature_geometry_within_parent_neighbourhood(self):
        for row in self.world["physical_features"]:
            geom = shape(row["geometry"])
            parent = self.neighbourhoods[row["neighbourhood_id"]]
            self.assertTrue(geom.is_valid, row["physical_feature_id"])
            self.assertTrue(parent.buffer(0.01).covers(geom), row["physical_feature_id"])

    def test_physical_dimensions_and_materials_present(self):
        for row in self.world["physical_features"]:
            self.assertGreater(row["dimensions"]["height_m"], 0)
            self.assertGreater(row["dimensions"]["width_m"], 0)
            self.assertTrue(row["construction"]["material"])
            self.assertTrue(row["construction"]["condition"])

    def test_required_obstacle_categories_present(self):
        types = {r["feature_type"] for r in self.world["physical_features"]}
        self.assertTrue({"retaining_wall", "wall", "fence", "gate", "drainage_structure"} <= types)
        self.assertIn("seawall", types)
        self.assertIn("embankment", types)

    def test_all_geometries_within_city_extent(self):
        for row in self.world["terrain_zones"]:
            geom = shape(row["geometry"])
            minx, miny, maxx, maxy = geom.bounds
            self.assertGreaterEqual(minx, 0)
            self.assertGreaterEqual(miny, 0)
            self.assertLessEqual(maxx, 12000)
            self.assertLessEqual(maxy, 9000)
        for row in self.world["physical_features"]:
            geom = shape(row["geometry"])
            minx, miny, maxx, maxy = geom.bounds
            self.assertGreaterEqual(minx, 0)
            self.assertGreaterEqual(miny, 0)
            self.assertLessEqual(maxx, 12000)
            self.assertLessEqual(maxy, 9000)

    def test_gate_and_barrier_gameplay_rules_defined(self):
        rules = self.world["gameplay_rules"]
        self.assertTrue(rules["gates"])
        self.assertTrue(rules["walls_and_fences"])
        self.assertTrue(rules["drainage"])
        self.assertTrue(rules["retaining_structures"])

    def test_vertical_datum_is_explicit_and_fictional(self):
        datum = self.world["vertical_datum"]
        self.assertEqual(datum["id"], "SW-VERT-01")
        self.assertIn("fictional", datum["zero_reference"])


if __name__ == "__main__":
    unittest.main()
