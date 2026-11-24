import json
import tempfile
import unittest
from pathlib import Path

from runtime.geography_readiness import audit_geography

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/geography/saltwater-geography-v1.json"


class GeographyReadinessTests(unittest.TestCase):
    def test_committed_baseline_counts_and_integrity(self):
        report = audit_geography(SOURCE)
        self.assertEqual(report["counts"], {
            "districts": 8, "neighbourhoods": 24, "roads": 42,
            "nodes": 367, "segments": 685, "routes": 5,
        })
        self.assertEqual(report["failed_checks"], [])
        self.assertEqual(report["passed_checks"], len(report["checks"]))

    def test_unresolved_mapping_and_operational_gate_remain_explicit(self):
        report = audit_geography(SOURCE)
        self.assertEqual(report["unresolved_source_to_spatial_id_mappings"], 100)
        self.assertFalse(report["operational_seed_eligible"])
        self.assertFalse(report["geometry_import_performed"])
        self.assertFalse(report["database_write_performed"])

    def test_duplicate_road_name_fails_audit(self):
        data = json.loads(SOURCE.read_text(encoding="utf-8"))
        data["roads"][1]["name"] = data["roads"][0]["name"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geo.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            report = audit_geography(path)
        self.assertIn("road_names_unique", report["failed_checks"])
        self.assertFalse(report["operational_seed_eligible"])

    def test_broken_segment_endpoint_fails_audit(self):
        data = json.loads(SOURCE.read_text(encoding="utf-8"))
        data["network"]["segments"][0]["to_node_id"] = "MISSING-NODE"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geo.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            report = audit_geography(path)
        self.assertIn("segment_endpoints_resolve", report["failed_checks"])


if __name__ == "__main__":
    unittest.main()
