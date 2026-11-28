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
        with gzip.open(ROOT / "data/property/saltwater-property-world-v1.json.gz", "rt", encoding="utf-8") as handle:
            cls.property_world_document = json.load(handle)
        cls.geography = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
        cls.audit = audit_business_registry(
            cls.registry,
            property_world_document=cls.property_world_document,
            geography=cls.geography,
        )

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

    def test_business_establishments_resolve_through_canonical_property_and_geography(self):
        lineage = self.audit["spatial_lineage"]
        self.assertEqual(lineage["businesses_checked"], 10000)
        self.assertEqual(lineage["establishments_checked"], 10000)
        self.assertEqual(lineage["exception_count"], 0)
        self.assertEqual(lineage["validation_status"], "PASS")
        self.assertGreater(lineage["canonical_units_checked"], 0)
        self.assertGreater(lineage["districts_referenced"], 0)
        self.assertGreater(lineage["neighbourhoods_referenced"], 0)

    def test_unknown_address_and_off_map_references_fail_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["businesses"][0]["registered_address_id"] = "SWADDR-MISSING"
        registry["establishments"][0]["address_id"] = "SWADDR-MISSING"
        with self.assertRaisesRegex(ValueError, "unknown canonical address"):
            audit_business_registry(
                registry,
                property_world_document=self.property_world_document,
                geography=self.geography,
            )

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
        used_units = {row["unit_id"] for row in registry["establishments"]}
        unit_table = self.property_world_document["tables"]["units"]
        unit_columns = {name: index for index, name in enumerate(unit_table["columns"])}
        address_table = self.property_world_document["tables"]["addresses"]
        address_columns = {name: index for index, name in enumerate(address_table["columns"])}
        addresses = {
            row[address_columns["address_id"]]: (
                row[address_columns["district_id"]],
                row[address_columns["neighbourhood_id"]],
            )
            for row in address_table["rows"]
        }
        branch_unit = None
        for values in unit_table["rows"]:
            unit_id = values[unit_columns["unit_id"]]
            unit_class = values[unit_columns["unit_class"]]
            if unit_id in used_units or unit_class in {"dwelling", "residential"}:
                continue
            address_id = values[unit_columns["address_id"]]
            district_id, neighbourhood_id = addresses[address_id]
            branch_unit = {
                "unit_id": unit_id,
                "property_id": values[unit_columns["property_id"]],
                "building_id": values[unit_columns["building_id"]],
                "premises_id": values[unit_columns["premises_id"]],
                "address_id": address_id,
                "district_id": district_id,
                "neighbourhood_id": neighbourhood_id,
            }
            break
        self.assertIsNotNone(branch_unit, "a valid unused commercial property-world unit is required")

        branch = copy.deepcopy(primary)
        branch.update({
            "establishment_id": "SWEST-BRANCH-ANTI-INFLATION-TEST",
            **branch_unit,
            "establishment_type": "branch",
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

        report = audit_business_registry(
            registry,
            property_world_document=self.property_world_document,
            geography=self.geography,
        )
        self.assertEqual(report["business_count"], 10000)
        self.assertEqual(report["distinct_business_ids"], 10000)
        self.assertEqual(report["establishment_count"], 10001)
        self.assertEqual(report["business_unit_link_count"], 10001)
        self.assertEqual(report["multi_establishment_businesses"], 1)
        self.assertEqual(report["spatial_lineage"]["establishments_checked"], 10001)
        self.assertEqual(report["spatial_lineage"]["exception_count"], 0)

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

    def test_distinct_businesses_can_share_building_without_sharing_units(self):
        registry = copy.deepcopy(self.registry)
        used_units = {row["unit_id"] for row in registry["establishments"]}
        existing_by_building = {}
        for row in registry["establishments"]:
            existing_by_building.setdefault(row["building_id"], row)

        unit_table = self.property_world_document["tables"]["units"]
        unit_columns = {name: index for index, name in enumerate(unit_table["columns"])}
        address_table = self.property_world_document["tables"]["addresses"]
        address_columns = {name: index for index, name in enumerate(address_table["columns"])}
        addresses = {
            row[address_columns["address_id"]]: (
                row[address_columns["district_id"]],
                row[address_columns["neighbourhood_id"]],
            )
            for row in address_table["rows"]
        }
        shared_unit = None
        shared_existing = None
        for values in unit_table["rows"]:
            unit_id = values[unit_columns["unit_id"]]
            building_id = values[unit_columns["building_id"]]
            unit_class = values[unit_columns["unit_class"]]
            if unit_id in used_units or building_id not in existing_by_building:
                continue
            if unit_class in {"dwelling", "residential"}:
                continue
            address_id = values[unit_columns["address_id"]]
            if address_id not in addresses:
                continue
            district_id, neighbourhood_id = addresses[address_id]
            shared_unit = {
                "unit_id": unit_id,
                "property_id": values[unit_columns["property_id"]],
                "building_id": building_id,
                "premises_id": values[unit_columns["premises_id"]],
                "address_id": address_id,
                "district_id": district_id,
                "neighbourhood_id": neighbourhood_id,
                "unit_class": unit_class,
            }
            shared_existing = existing_by_building[building_id]
            break
        self.assertIsNotNone(shared_unit, "a second unused non-residential unit in an occupied building is required")

        template_business = registry["businesses"][0]
        new_business = copy.deepcopy(template_business)
        new_business.update({
            "business_id": "SWBIZ-99999999",
            "registered_name": "Quillstone Meridian Holdings Limited",
            "trading_name": "Quillstone Meridian",
            "registered_address_id": shared_unit["address_id"],
            "primary_establishment_id": "SWEST-99999999",
            "status": "active",
            "source_generator": registry["generator"],
            "registered_city": "Saltwater",
            "fictional_entity": True,
            "person_records_created": 0,
        })

        template_establishment = next(
            row for row in registry["establishments"]
            if row["establishment_id"] == template_business["primary_establishment_id"]
        )
        new_establishment = copy.deepcopy(template_establishment)
        new_establishment.update({
            "establishment_id": "SWEST-99999999",
            "business_id": new_business["business_id"],
            **shared_unit,
            "status": "active",
            "establishment_type": "primary",
            "source_generator": registry["generator"],
        })

        template_link = next(
            row for row in registry["business_unit_links"]
            if row["establishment_id"] == template_establishment["establishment_id"]
        )
        new_link = copy.deepcopy(template_link)
        new_link.update({
            "business_unit_link_id": "SWBUL-99999999",
            "business_id": new_business["business_id"],
            "establishment_id": new_establishment["establishment_id"],
            "unit_id": shared_unit["unit_id"],
            "premises_id": shared_unit["premises_id"],
            "occupancy_status": "occupied",
        })

        registry["businesses"].append(new_business)
        registry["establishments"].append(new_establishment)
        registry["business_unit_links"].append(new_link)
        summary = registry["summary"]
        summary["distinct_business_count"] += 1
        summary["establishment_count"] += 1
        summary["business_unit_link_count"] += 1
        summary["active_businesses"] += 1
        summary["businesses_by_sector"][new_business["sector"]] += 1

        report = audit_business_registry(
            registry,
            property_world_document=self.property_world_document,
            geography=self.geography,
        )
        self.assertEqual(report["business_count"], 10001)
        self.assertEqual(report["distinct_business_ids"], 10001)
        self.assertEqual(report["spatial_lineage"]["establishments_checked"], 10001)
        self.assertEqual(new_establishment["building_id"], shared_existing["building_id"])
        self.assertNotEqual(new_establishment["unit_id"], shared_existing["unit_id"])
        self.assertNotEqual(new_establishment["business_id"], shared_existing["business_id"])

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

    def test_zero_count_lifecycle_classes_reconcile(self):
        registry = copy.deepcopy(self.registry)
        for business in registry["businesses"]:
            business["status"] = "active"
        for establishment in registry["establishments"]:
            establishment["operating_status"] = "active"
        for link in registry["business_unit_links"]:
            if link.get("valid_to_tick") is None:
                link["occupancy_status"] = "active"
        registry["summary"]["active_businesses"] = len(registry["businesses"])
        registry["summary"]["seasonal_businesses"] = 0
        registry["summary"]["temporarily_inactive_businesses"] = 0

        report = audit_business_registry(registry)
        self.assertEqual(report["businesses_by_lifecycle_status"], {"active": 10000})
        self.assertEqual(report["seasonal_businesses"], 0)
        self.assertEqual(report["temporarily_inactive_businesses"], 0)

    def test_boolean_values_are_not_accepted_as_ticks_or_counts(self):
        registry = copy.deepcopy(self.registry)
        registry["business_unit_links"][0]["valid_from_tick"] = True
        with self.assertRaisesRegex(ValueError, "invalid start tick"):
            audit_business_registry(registry)

        registry = copy.deepcopy(self.registry)
        registry["summary"]["active_businesses"] = True
        with self.assertRaisesRegex(ValueError, "summary counts are incomplete"):
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
        registry["businesses"][0]["employee_band"] = "INVALID-BAND"
        with self.assertRaisesRegex(ValueError, "employee band inconsistent"):
            audit_business_registry(registry)


if __name__ == "__main__":
    unittest.main()
