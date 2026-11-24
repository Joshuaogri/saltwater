import json
import unittest
from pathlib import Path
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union

from runtime.parcel_candidate_generator import build_candidates

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class ParcelCandidateGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_candidates(SOURCE)

    def test_deterministic_manifest_and_candidate_ids(self):
        second = build_candidates(SOURCE)
        self.assertEqual(self.result["manifest_sha256"], second["manifest_sha256"])
        self.assertEqual(
            [p["candidate_parcel_id"] for p in self.result["parcels"]],
            [p["candidate_parcel_id"] for p in second["parcels"]],
        )

    def test_candidates_use_actual_dissolved_road_and_water_geometry(self):
        generation = self.result["generation"]
        self.assertEqual(generation["road_reserve_design_standard"], "SW-RDS-V1")
        self.assertEqual(generation["road_reserve_geometry_source"], "DISSOLVED_685_SEGMENT_CORRIDORS")
        self.assertEqual(generation["topology_validation"], "PASS")
        self.assertEqual(generation["area_balance_delta_m2"], 0)
        self.assertEqual(generation["unresolved_source_spatial_mappings"], 100)
        self.assertGreater(generation["water_intersection_cell_count"], 0)
        self.assertGreater(generation["road_reserve_area_m2"], 0)

    def test_every_parcel_is_valid_and_has_cell_lineage(self):
        ids = [p["candidate_parcel_id"] for p in self.result["parcels"]]
        self.assertEqual(len(ids), len(set(ids)))
        for parcel in self.result["parcels"]:
            polygon = Polygon(parcel["geometry"][0], parcel["geometry"][1:])
            self.assertTrue(polygon.is_valid)
            self.assertGreater(polygon.area, 0)
            self.assertAlmostEqual(parcel["area_m2"], round(polygon.area, 3), places=3)
            self.assertIn(":500m-cell:", parcel["source_ref"])
            self.assertIsNone(parcel["candidate_spatial_id"])
            self.assertIsNone(parcel["canonical_address_id"])

    def test_candidates_tile_each_neighbourhood_land_once(self):
        for row in self.result["coverage_by_neighbourhood"]:
            self.assertEqual(row["topology_status"], "PASS")
            self.assertEqual(row["area_balance_delta_m2"], 0)
            self.assertGreater(row["candidate_land_area_m2"], 0)

    def test_water_intersection_removes_only_water_geometry_not_entire_grid_cell(self):
        self.assertEqual(self.result["excluded_cells"], [])
        self.assertGreater(self.result["generation"]["water_intersection_cell_count"], 0)
        self.assertTrue(all(p["geometry_quality"] == "candidate_unreviewed" for p in self.result["parcels"]))

    def test_frontage_is_supported_only_by_actual_road_reserve_boundary_contact(self):
        frontage = [p for p in self.result["parcels"] if p["road_frontage_segment_ids"]]
        self.assertGreater(len(frontage), 0)
        self.assertTrue(all(p["frontage_status"] == "ROAD_RESERVE_EDGE_CONTACT_CANDIDATE" for p in frontage))

    def test_no_operational_ids_or_addresses_are_created(self):
        self.assertFalse(self.result["operational_approval"])
        self.assertEqual(self.result["generation"]["spatial_ids_assigned"], 0)
        self.assertEqual(self.result["generation"]["canonical_addresses_created"], 0)
        self.assertEqual(self.result["address_generation"]["records_created"], 0)


if __name__ == "__main__":
    unittest.main()
