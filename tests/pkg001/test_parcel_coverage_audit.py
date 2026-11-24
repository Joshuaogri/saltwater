import json
import unittest
from pathlib import Path

from runtime.parcel_coverage_audit import build_coverage_audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class ParcelCoverageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_coverage_audit(SOURCE)

    def test_source_grid_and_candidate_counts_reconcile(self):
        summary = self.result["summary"]
        self.assertEqual(summary["neighbourhood_count"], 24)
        self.assertEqual(summary["source_grid_cell_count"], 432)
        self.assertGreater(summary["candidate_parcel_count"], 0)
        self.assertEqual(summary["candidate_parcel_count"], summary["candidate_component_count"])
        self.assertGreater(summary["water_intersection_cell_count"], 0)

    def test_exact_geometry_area_balance(self):
        s = self.result["summary"]
        self.assertEqual(s["source_area_m2"], 108000000)
        self.assertGreater(s["dissolved_road_reserve_area_m2"], 0)
        self.assertGreater(s["candidate_land_area_m2"], 0)
        self.assertEqual(s["area_balance_delta_m2"], 0)
        self.assertEqual(s["area_balance_status"], "PASS")
        self.assertFalse(s["provisional_15m_inset_used"])
        self.assertFalse(s["whole_water_hit_cells_excluded"])

    def test_actual_road_and_water_areas_are_separately_accounted(self):
        s = self.result["summary"]
        self.assertGreater(s["water_area_outside_road_reserve_m2"], 0)
        self.assertAlmostEqual(
            s["source_area_m2"],
            s["dissolved_road_reserve_area_m2"] +
            s["water_area_outside_road_reserve_m2"] +
            s["candidate_land_area_m2"],
            places=3,
        )

    def test_all_neighbourhoods_have_zero_delta_area_records(self):
        rows = self.result["coverage_by_neighbourhood"]
        self.assertEqual(len(rows), 24)
        self.assertEqual(len({r["neighbourhood_id"] for r in rows}), 24)
        self.assertTrue(all(r["source_area_m2"] > 0 for r in rows))
        self.assertTrue(all(r["area_balance_delta_m2"] == 0 for r in rows))
        self.assertTrue(all(r["topology_status"] == "PASS" for r in rows))

    def test_overlapping_water_polygons_fail_closed(self):
        bad = json.loads(json.dumps(SOURCE))
        feature = next(f for f in bad["features"] if f.get("id") == "SW-WTR-002")
        feature["geometry"]["coordinates"][0] = [
            [10000, 3500], [11000, 3500], [11000, 4000], [10000, 4000], [10000, 3500]
        ]
        with self.assertRaisesRegex(ValueError, "Overlapping water polygons"):
            build_coverage_audit(bad)


if __name__ == "__main__":
    unittest.main()
