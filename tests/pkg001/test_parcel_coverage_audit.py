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
        self.assertEqual(summary["candidate_parcel_count"], 396)
        self.assertEqual(summary["water_hit_cell_count"], 36)
        self.assertEqual(
            summary["source_grid_cell_count"],
            summary["candidate_parcel_count"] + summary["water_hit_cell_count"],
        )

    def test_exact_area_balance(self):
        s = self.result["summary"]
        self.assertEqual(s["source_area_m2"], 108000000)
        self.assertEqual(s["candidate_cell_envelope_area_m2"], 99000000)
        self.assertEqual(s["candidate_parcel_area_m2"], 87476400)
        self.assertGreater(s["exact_water_intersection_area_m2"], 0)
        self.assertEqual(s["water_hit_cell_envelope_area_m2"], 9000000)
        self.assertEqual(s["provisional_inset_residual_m2"], 11523600)
        self.assertEqual(s["area_balance_delta_m2"], 0)
        self.assertEqual(s["area_balance_status"], "PASS")

    def test_residual_land_is_not_classified_as_road_or_developable(self):
        s = self.result["summary"]
        self.assertGreater(s["unresolved_nonwater_area_in_water_hit_cells_m2"], 0)
        self.assertGreater(s["unallocated_area_m2"], 0)
        self.assertFalse(self.result["operational_approval"])
        self.assertFalse(self.result["assumptions"]["inset_is_surveyed_or_approved_road_reserve"])

    def test_all_neighbourhoods_have_area_records(self):
        rows = self.result["coverage_by_neighbourhood"]
        self.assertEqual(len(rows), 24)
        self.assertEqual(len({r["neighbourhood_id"] for r in rows}), 24)
        self.assertTrue(all(r["source_area_m2"] > 0 for r in rows))

    def test_water_polygon_overlap_is_not_double_counted(self):
        bad = json.loads(json.dumps(SOURCE))
        feature = next(f for f in bad["features"] if f.get("id") == "SW-WTR-002")
        feature["geometry"]["coordinates"][0] = [
            [10000, 3500], [11000, 3500], [11000, 4000], [10000, 4000], [10000, 3500]
        ]
        with self.assertRaisesRegex(ValueError, "Overlapping water polygons"):
            build_coverage_audit(bad)


if __name__ == "__main__":
    unittest.main()
