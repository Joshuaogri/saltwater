import json
import unittest
from pathlib import Path

from runtime.road_corridor_audit import build_road_corridor_audit
from runtime.road_reserve_topology import build_road_reserve_topology

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class RoadReserveTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corridors = build_road_corridor_audit(SOURCE)
        cls.result = build_road_reserve_topology(SOURCE, cls.corridors)

    def test_dissolves_all_segment_corridors(self):
        summary = self.result["summary"]
        self.assertEqual(summary["segment_corridor_count"], 685)
        self.assertGreater(summary["dissolved_road_reserve_component_count"], 0)
        self.assertGreater(summary["dissolved_city_road_reserve_area_m2"], 0)

    def test_neighbourhoods_partition_the_city_without_gaps_or_overlaps(self):
        summary = self.result["summary"]
        self.assertEqual(summary["city_boundary_area_m2"], 108000000)
        self.assertEqual(summary["neighbourhood_count"], 24)
        self.assertEqual(summary["neighbourhood_union_area_m2"], 108000000)
        self.assertEqual(summary["neighbourhood_overlap_area_m2"], 0)
        self.assertEqual(summary["neighbourhood_gap_area_m2"], 0)
        self.assertEqual(summary["neighbourhood_outside_city_area_m2"], 0)
        self.assertEqual(summary["boundary_topology_status"], "PASS")

    def test_dissolved_road_reserve_allocates_once_to_neighbourhoods(self):
        summary = self.result["summary"]
        self.assertEqual(summary["road_reserve_allocation_status"], "PASS")
        self.assertEqual(summary["road_reserve_allocation_delta_m2"], 0)
        rows = self.result["coverage_by_neighbourhood"]
        self.assertEqual(len(rows), 24)
        self.assertTrue(all(row["road_reserve_area_m2"] >= 0 for row in rows))
        self.assertEqual(
            round(sum(row["road_reserve_area_m2"] for row in rows), 3),
            summary["dissolved_city_road_reserve_area_m2"],
        )

    def test_junction_overlaps_are_dissolved_before_area_accounting(self):
        summary = self.result["summary"]
        self.assertGreater(summary["junction_overlap_area_removed_by_dissolve_m2"], 0)
        self.assertGreaterEqual(
            summary["sum_of_segment_corridor_areas_m2"],
            summary["raw_road_reserve_area_before_city_clip_m2"],
        )
        self.assertIn("Dissolved once", self.result["method"]["junction_overlap"])

    def test_missing_design_standard_fails_closed(self):
        bad = dict(self.corridors)
        bad["road_reserve_width_source"] = None
        with self.assertRaisesRegex(ValueError, "does not use SW-RDS-V1"):
            build_road_reserve_topology(SOURCE, bad)


if __name__ == "__main__":
    unittest.main()
