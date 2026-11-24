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

    def test_bridge_lengths_are_reconciled_to_canonical_polyline_measurement(self):
        exceptions = self.result["length_exceptions"]
        self.assertEqual(exceptions, [])
        bridges = [s for s in self.result["segments"] if s["kind"] == "bridge"]
        self.assertEqual(len(bridges), 2)
        for item in bridges:
            self.assertAlmostEqual(item["declared_length_m"], 2019.804, places=3)
            self.assertAlmostEqual(item["measured_polyline_length_m"], 2019.803903, places=5)

    def test_fictional_reserve_width_standard_generates_all_corridors(self):
        self.assertEqual(self.result["road_reserve_polygon_generation"], "SEGMENT_POLYGONS_GENERATED")
        self.assertEqual(self.result["summary"]["reserve_polygons_created"], 685)
        self.assertEqual(self.result["summary"]["corridor_widths_unresolved"], 0)
        self.assertEqual(self.result["road_reserve_width_source"], "SW-RDS-V1")
        widths = {s["road_class"]: s["reserve_width_m"] for s in self.result["segments"]}
        self.assertEqual(widths, {
            "local_street": 18,
            "district_connector": 24,
            "primary_arterial": 30,
            "bridge": 24,
        })
        self.assertTrue(all(s["reserve_polygon"] and len(s["reserve_polygon"][0]) >= 5 for s in self.result["segments"]))
        self.assertTrue(all(s["reserve_geometry_status"] == "GENERATED_FROM_SW_RDS_V1_CENTRELINE_BUFFER" for s in self.result["segments"]))
        self.assertIn("DISSOLVE", self.result["summary"]["junction_overlap_policy"])

    def test_bridge_polyline_geometry_is_retained(self):
        bridges = [s for s in self.result["segments"] if s["kind"] == "bridge"]
        self.assertEqual(len(bridges), 2)
        self.assertTrue(all(len(s["centreline_geometry"]) == 5 for s in bridges))


if __name__ == "__main__":
    unittest.main()
