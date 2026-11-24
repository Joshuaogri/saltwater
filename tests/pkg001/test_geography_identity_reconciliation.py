import json
import unittest
from pathlib import Path

from runtime.geography_identity_reconciliation import validate_identity_map


class GeographyIdentityReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.geo = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text())
        cls.identity_map = json.loads((root / "data/geography/saltwater-geography-v1-identity-map.json").read_text())

    def test_all_100_source_records_map_exactly_to_stable_entity_codes(self):
        result = validate_identity_map(self.geo, self.identity_map)
        self.assertEqual(result["source_records"], 100)
        self.assertEqual(result["resolved"], 100)
        self.assertEqual(result["unresolved"], 0)
        self.assertEqual(result["stable_source_to_entity_code_mappings"], 100)

    def test_duplicate_source_mapping_is_rejected(self):
        tampered = json.loads(json.dumps(self.identity_map))
        tampered["entries"][1]["source_id"] = tampered["entries"][0]["source_id"]
        with self.assertRaisesRegex(ValueError, "duplicate source_id"):
            validate_identity_map(self.geo, tampered)

    def test_wrong_parent_mapping_is_rejected(self):
        tampered = json.loads(json.dumps(self.identity_map))
        neighbourhood = next(x for x in tampered["entries"] if x["entity_type"] == "NEIGHBOURHOOD")
        neighbourhood["parent_entity_code"] = "saltwater-city"
        with self.assertRaisesRegex(ValueError, "parent_entity_code mismatch"):
            validate_identity_map(self.geo, tampered)

    def test_unmapped_source_feature_is_rejected(self):
        tampered = json.loads(json.dumps(self.identity_map))
        tampered["entries"].pop()
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            validate_identity_map(self.geo, tampered)

    def test_database_surrogate_ids_are_not_hardcoded(self):
        for entry in self.identity_map["entries"]:
            self.assertIsNone(entry["spatial_id"])


if __name__ == "__main__":
    unittest.main()
