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


    def test_additional_branch_establishment_does_not_inflate_business_count(self):
        registry = copy.deepcopy(self.registry)
        business = registry["businesses"][0]
        primary = next(
            row for row in registry["establishments"]
            if row["establishment_id"] == business["primary_establishment_id"]
        )
        branch = copy.deepcopy(primary)
        branch.update({
            "establishment_id": "SWEST-BRANCH-ANTI-INFLATION-TEST",
            "address_id": "SWADDR-BRANCH-TEST",
            "property_id": "SWPROP-BRANCH-TEST",
            "building_id": "SWBLDG-BRANCH-TEST",
            "premises_id": "SWPREM-BRANCH-TEST",
            "unit_id": "SWUNIT-BRANCH-TEST",
            "district_id": "SWDIST-BRANCH-TEST",
            "neighbourhood_id": "SWNEIGH-BRANCH-TEST",
        })
        registry["establishments"].append(branch)
        primary_link = next(
            row for row in registry["business_unit_links"]
            if row["establishment_id"] == primary["establishment_id"]
        )
        branch_link = copy.deepcopy(primary_link)
        branch_link.update({
            "business_unit_link_id": "SWBUL-BRANCH-ANTI-INFLATION-TEST",
            "establishment_id": branch["establishment_id"],
            "unit_id": branch["unit_id"],
            "premises_id": branch["premises_id"],
        })
        registry["business_unit_links"].append(branch_link)

        report = audit_business_registry(registry)
        self.assertEqual(report["business_count"], 10000)
        self.assertEqual(report["distinct_business_ids"], 10000)
        self.assertEqual(report["establishment_count"], 10001)
        self.assertEqual(report["business_unit_link_count"], 10001)
        self.assertEqual(report["multi_establishment_businesses"], 1)
        self.assertTrue(report["valid_10k_business_minimum"])

    def test_brand_and_alias_records_never_inflate_business_count(self):
        registry = copy.deepcopy(self.registry)
        owner = registry["businesses"][0]["business_id"]
        registry["brands"] = [{
            "brand_id": "SWBRAND-ANTI-INFLATION-TEST",
            "owner_business_id": owner,
        }]
        registry["business_aliases"] = [{
            "alias_id": "SWALIAS-ANTI-INFLATION-TEST",
            "business_id": owner,
            "alias": "Alternate public-facing name",
        }]

        report = audit_business_registry(registry)
        self.assertEqual(report["business_count"], 10000)
        self.assertEqual(report["distinct_business_ids"], 10000)
        self.assertEqual(report["brand_records_not_counted_as_businesses"], 1)
        self.assertEqual(report["alias_records_not_counted_as_businesses"], 1)

    def test_branch_primary_establishment_must_belong_to_same_business(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][0]["primary_establishment_id"] = (
            registry["establishments"][-1]["establishment_id"]
        )
        with self.assertRaisesRegex(ValueError, "owned primary establishment"):
            audit_business_registry(registry)


    def test_generator_provenance_mismatch_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][0]["source_generator"] = "untrusted-generator"
        with self.assertRaisesRegex(ValueError, "mismatched generator provenance"):
            audit_business_registry(registry)

    def test_current_occupancy_status_must_match_business_lifecycle(self):
        registry = copy.deepcopy(self.registry)
        registry["business_unit_links"][0]["occupancy_status"] = "seasonal"
        with self.assertRaisesRegex(ValueError, "current occupancy lifecycle status mismatch"):
            audit_business_registry(registry)

    def test_current_exclusive_business_occupancy_cannot_overlap_on_one_unit(self):
        registry = copy.deepcopy(self.registry)
        first_unit = registry["establishments"][0]["unit_id"]
        registry["establishments"][1]["unit_id"] = first_unit
        registry["business_unit_links"][1]["unit_id"] = first_unit
        with self.assertRaisesRegex(ValueError, "overlapping exclusive business occupancy"):
            audit_business_registry(registry)

    def test_occupancy_link_temporal_order_must_be_valid(self):
        registry = copy.deepcopy(self.registry)
        registry["business_unit_links"][0]["valid_from_tick"] = -1
        with self.assertRaisesRegex(ValueError, "invalid start tick"):
            audit_business_registry(registry)

    def test_registry_must_be_marked_as_fictional_canon(self):
        registry = copy.deepcopy(self.registry)
        registry["canon_status"] = "UNVERIFIED"
        with self.assertRaisesRegex(ValueError, "not marked as fictional"):
            audit_business_registry(registry)


    def test_lifecycle_counts_reconcile_to_embedded_registry_summary(self):
        report = self.audit
        self.assertEqual(
            report["lifecycle_count_total"],
            report["business_count"],
        )
        self.assertEqual(
            report["active_businesses"]
            + report["seasonal_businesses"]
            + report["temporarily_inactive_businesses"],
            10000,
        )

    def test_lifecycle_summary_drift_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["summary"]["active_businesses"] += 1
        with self.assertRaisesRegex(ValueError, "lifecycle class counts do not match"):
            audit_business_registry(registry)

    def test_unknown_business_lifecycle_status_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][0]["status"] = "unknown"
        with self.assertRaisesRegex(ValueError, "unknown lifecycle status"):
            audit_business_registry(registry)

    def test_employee_band_must_match_business_size(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][0]["employee_band"] = "100-499"
        with self.assertRaisesRegex(ValueError, "employee band inconsistent"):
            audit_business_registry(registry)


if __name__ == "__main__":
    unittest.main()
