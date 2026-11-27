"""Regression tests for the no-write BP02 operational release packager."""
import gzip
import hashlib
import json
import unittest

from runtime.bp02_operational_geography_package import build_release


class BP02OperationalPackageTests(unittest.TestCase):
    def test_package_is_deterministic_and_source_pinned(self):
        first, manifest_a = build_release()
        second, manifest_b = build_release()
        self.assertEqual(first, second)
        self.assertEqual(manifest_a, manifest_b)
        self.assertEqual(hashlib.sha256(first).hexdigest(), manifest_a["package_sha256"])
        self.assertEqual(manifest_a["record_counts"]["parcels"], 420)
        self.assertEqual(manifest_a["record_counts"]["addresses"], 420)
        self.assertEqual(manifest_a["record_counts"]["access_points"], 2948)
        self.assertEqual(manifest_a["record_counts"]["bridge_connectors"], 4)
        payload = json.loads(gzip.decompress(first))
        self.assertTrue(payload["gameplay_release_accepted"])
        self.assertFalse(payload["production_seed_approved"])
        self.assertFalse(payload["database_write_performed"])
        self.assertFalse(payload["neon_write_performed"])
        self.assertEqual(payload["acceptance"]["overall_status"], "PASS")
        self.assertEqual(payload["acceptance"]["operational_release_status"], "PASS")
        self.assertFalse(payload["identity_map"]["operational_seed_approved"])
        self.assertEqual(len(payload["identity_map"]["entries"]), 100)
        self.assertEqual(
            payload["identity_map"]["counts"]["unresolved_source_to_entity_code_mappings"], 0
        )
        self.assertTrue(all(
            row["operational_status"] == "ACTIVE_IN_GAME"
            for row in payload["canonical_geography"]["access_points"]
        ))
        self.assertTrue(all(
            row["operational_status"] == "ACTIVE_IN_GAME"
            for row in payload["canonical_geography"]["bridge_connectors"]
        ))


if __name__ == "__main__":
    unittest.main()
