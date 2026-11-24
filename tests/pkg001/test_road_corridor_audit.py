import json
import unittest
from pathlib import Path

from runtime.road_corridor_audit import build_road_corridor_audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class RoadCorridorAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_road_corridor_audit(SOURCE)

    def test_network_identity_and_connectivity(self):
        summary = self.result["summary"]
        self.assertEqual(summary["road_count"], 42)
        self.assertEqual(summary["segment_count"], 685)
        self.assertEqual(summary["node_count"], 367)
        self.assertEqual(summary["connected_network_components"], 1)
        self.assertEqual(summary["node_degree_mismatch_count"], 0)
        self.assertEqual(summary["road_membership_errors"], 0)
        self.assertEqual(summary["endpoint_geometry_errors"], 0)

    def test_class_counts_reconcile(self):
        self.assertEqual(
            self.result["class_summary"],
            {"bridge": 2, "district_connector": 84, "local_street": 482, "primary_arterial": 117},
        )
        self.assertEqual(sum(self.result["class_summary"].values()), 685)

    def test_bridge_length_exceptions_are_preserved(self):
        exceptions = self.result["length_exceptions"]
        self.assertEqual({item["segment_id"] for item in exceptions}, {"SWS-0684", "SWS-0685"})
        for item in exceptions:
            self.assertEqual(item["declared_length_m"], 2000)
            self.assertAlmostEqual(item["measured_polyline_length_m"], 2019.803903, places=5)

    def test_no_road_reserve_width_or_polygon_is_invented(self):
        self.assertFalse(self.result["operational_approval"])
        self.assertEqual(self.result["road_reserve_polygon_generation"], "BLOCKED")
        self.assertEqual(self.result["summary"]["reserve_polygons_created"], 0)
        self.assertEqual(self.result["summary"]["reserve_area_assigned_m2"], 0)
        self.assertEqual(self.result["summary"]["corridor_widths_unresolved"], 685)
        self.assertTrue(all(s["reserve_width_m"] is None for s in self.result["segments"]))
        self.assertTrue(all(s["reserve_polygon"] is None for s in self.result["segments"]))

    def test_bridge_polyline_geometry_is_retained(self):
        bridges = [s for s in self.result["segments"] if s["kind"] == "bridge"]
        self.assertEqual(len(bridges), 2)
        self.assertTrue(all(len(s["centreline_geometry"]) == 5 for s in bridges))


if __name__ == "__main__":
    unittest.main()
