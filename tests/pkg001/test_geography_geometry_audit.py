import json
import tempfile
import unittest
from pathlib import Path

from runtime.geography_geometry_audit import audit_geometry

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/geography/saltwater-geography-v1.json"


class GeographyGeometryAuditTests(unittest.TestCase):
    def audit_mutation(self, mutate):
        data = json.loads(SOURCE.read_text(encoding="utf-8"))
        mutate(data)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geography.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return audit_geometry(path)

    def test_committed_geometry_baseline_passes_all_checks(self):
        report = audit_geometry(SOURCE)
        self.assertEqual(report["failed_checks"], [])
        self.assertEqual(report["passed_checks"], 10)
        self.assertEqual(report["measurements"]["city_area_m2"], 108000000.0)
        self.assertEqual(report["measurements"]["neighbourhood_area_sum_m2"], 108000000.0)
        self.assertEqual(report["measurements"]["network_component_sizes"], [367])

    def test_open_polygon_ring_fails(self):
        report = self.audit_mutation(lambda d: d["features"][0]["geometry"]["coordinates"][0].pop())
        self.assertIn("polygon_rings_valid_and_simple", report["failed_checks"])

    def test_point_outside_city_fails(self):
        def mutate(d):
            feature = next(f for f in d["features"] if f["geometry"]["type"] == "Point")
            feature["geometry"]["coordinates"] = [13000, 9500]
        report = self.audit_mutation(mutate)
        self.assertIn("point_features_inside_city_boundary", report["failed_checks"])

    def test_neighbourhood_wrong_parent_fails(self):
        report = self.audit_mutation(lambda d: d["neighbourhoods"][0].update({"district_id": "SW-D08"}))
        self.assertIn("neighbourhoods_contained_by_assigned_district", report["failed_checks"])

    def test_overlapping_neighbourhoods_fail(self):
        def mutate(d):
            d["neighbourhoods"][1]["geometry"] = json.loads(json.dumps(d["neighbourhoods"][0]["geometry"]))
        report = self.audit_mutation(mutate)
        self.assertIn("neighbourhood_interiors_do_not_overlap", report["failed_checks"])

    def test_segment_length_mismatch_fails(self):
        report = self.audit_mutation(lambda d: d["network"]["segments"][0].update({"length_m": 1}))
        self.assertIn("road_segment_geometry_matches_nodes_and_lengths", report["failed_checks"])

    def test_node_degree_mismatch_fails(self):
        report = self.audit_mutation(lambda d: d["network"]["nodes"][0].update({"degree": 99}))
        self.assertIn("node_degrees_match_segment_graph", report["failed_checks"])

    def test_broken_route_sequence_fails(self):
        report = self.audit_mutation(lambda d: d["network"]["routes"][0]["segment_ids"].__setitem__(0, "MISSING"))
        self.assertIn("route_segment_sequences_are_contiguous", report["failed_checks"])

    def test_geometry_audit_never_authorises_seed(self):
        report = audit_geometry(SOURCE)
        self.assertFalse(report["operational_seed_eligible"])
        self.assertFalse(report["geometry_import_performed"])
        self.assertFalse(report["database_write_performed"])


if __name__ == "__main__":
    unittest.main()
