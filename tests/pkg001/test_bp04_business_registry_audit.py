import copy
import gzip
import json
import unittest
from pathlib import Path

from runtime.bp04_business_registry_audit import audit_business_registry
from runtime.property_tenure_generator import _expand_columnar


ROOT = Path(__file__).resolve().parents[2]


class BP04BusinessRegistryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with gzip.open(ROOT / "data/business/saltwater-business-registry-v1.json.gz", "rt", encoding="utf-8") as handle:
            cls.registry = _expand_columnar(json.load(handle))
        cls.audit = audit_business_registry(cls.registry)

    def test_full_ten_thousand_local_business_population_and_lifecycle_counts(self):
        report = self.audit
        self.assertTrue(report["valid_10k_business_minimum"])
        self.assertEqual(report["business_count"], 10000)
        self.assertEqual(report["distinct_business_ids"], 10000)
        self.assertEqual(report["establishment_count"], 10000)
        self.assertEqual(report["business_unit_link_count"], 10000)
        self.assertEqual(report["public_name_count"], 20000)
        self.assertEqual(report["local_saltwater_businesses"], 10000)
        self.assertEqual(sum(report["businesses_by_lifecycle_status"].values()), 10000)
        self.assertEqual(report["person_records_created"], 0)
        self.assertFalse(report["persistent_name_reservations_performed"])

    def test_duplicate_business_identity_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][1]["business_id"] = registry["businesses"][0]["business_id"]
        with self.assertRaisesRegex(ValueError, "duplicate business identity"):
            audit_business_registry(registry)

    def test_duplicate_public_name_across_businesses_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][1]["trading_name"] = registry["businesses"][0]["trading_name"]
        with self.assertRaisesRegex(ValueError, "global public-name collision"):
            audit_business_registry(registry)

    def test_nonlocal_business_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][0]["registered_city"] = "Elsewhere"
        with self.assertRaisesRegex(ValueError, "not explicitly local"):
            audit_business_registry(registry)

    def test_orphan_establishment_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["establishments"][0]["business_id"] = "SWBIZ-MISSING"
        with self.assertRaisesRegex(ValueError, "orphan establishment"):
            audit_business_registry(registry)

    def test_primary_establishment_and_address_mismatch_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["establishments"][0]["address_id"] = "SWADDR-MISMATCH"
        with self.assertRaisesRegex(ValueError, "registered address differs"):
            audit_business_registry(registry)

    def test_numeric_placeholder_name_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][0]["trading_name"] = "Example Trading 123"
        with self.assertRaisesRegex(ValueError, "numeric placeholder"):
            audit_business_registry(registry)


if __name__ == "__main__":
    unittest.main()
