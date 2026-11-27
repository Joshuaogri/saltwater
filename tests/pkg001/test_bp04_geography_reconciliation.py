import unittest
from unittest.mock import patch

from runtime.bp04_geography_reconciliation import (
    _resolve_geometry_manifests, reconcile_collections,
)


class BP04GeographyReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.properties = [
            {
                "property_id": "SWPROP-1", "source_candidate_parcel_id": "SWPAR-1",
                "address_id": "SWADDR-1", "source_district_id": "SW-D01",
                "source_neighbourhood_id": "SW-D01-N1",
            },
            {
                "property_id": "SWPROP-2", "source_candidate_parcel_id": "SWPAR-2",
                "address_id": "SWADDR-2", "source_district_id": "SW-D02",
                "source_neighbourhood_id": "SW-D02-N1",
            },
        ]
        self.addresses = [
            {
                "address_id": "SWADDR-1", "property_id": "SWPROP-1",
                "district_id": "SW-D01", "neighbourhood_id": "SW-D01-N1",
                "road_id": "SW-R01",
            },
            {
                "address_id": "SWADDR-2", "property_id": "SWPROP-2",
                "district_id": "SW-D02", "neighbourhood_id": "SW-D02-N1",
                "road_id": "SW-R02",
            },
        ]
        self.codes = {
            "SW-D01", "SW-D02", "SW-D01-N1", "SW-D02-N1", "SW-R01", "SW-R02",
        }

    def test_precomputed_geometry_manifests_are_reused_without_regeneration(self):
        geo = {}
        candidates = {"parcels": []}
        dossiers = {"parcels": []}
        assets = {"properties": [], "buildings": [], "access_points": []}
        with (
            patch("runtime.bp04_geography_reconciliation.build_candidates", side_effect=AssertionError("rebuilt candidates")),
            patch("runtime.bp04_geography_reconciliation.build_parcel_dossiers", side_effect=AssertionError("rebuilt dossiers")),
            patch("runtime.bp04_geography_reconciliation.build_asset_inventory", side_effect=AssertionError("rebuilt assets")),
        ):
            resolved = _resolve_geometry_manifests(geo, candidates, dossiers, assets)
        self.assertIs(resolved[0], candidates)
        self.assertIs(resolved[1], dossiers)
        self.assertIs(resolved[2], assets)

    def test_candidate_and_context_links_resolve_without_false_canonical_promotion(self):
        result = reconcile_collections(
            self.properties, self.addresses, {"SWPAR-1", "SWPAR-2"}, self.codes
        )
        self.assertEqual(result["generated_candidate_parcel_links_resolved"], 2)
        self.assertEqual(result["primary_property_address_links_resolved"], 2)
        self.assertEqual(result["district_entity_code_matches"], 2)
        self.assertEqual(result["neighbourhood_entity_code_matches"], 2)
        self.assertEqual(result["road_entity_code_matches"], 2)
        self.assertEqual(result["canonical_parcel_identity_matches"], 0)
        self.assertEqual(result["canonical_address_identity_matches"], 0)
        self.assertEqual(result["properties_still_awaiting_bp02_parcel_binding"], 2)
        self.assertEqual(result["addresses_still_awaiting_bp02_address_binding"], 2)
        self.assertEqual(result["canonical_binding_status"],
                         "BLOCKED_BP02_CANONICAL_PARCEL_AND_ADDRESS_IDENTITIES_ABSENT")
        self.assertFalse(result["address_promotion_performed"])
        self.assertFalse(result["database_write_performed"])

    def test_stable_design_ids_bind_without_claiming_operational_canonical_release(self):
        result = reconcile_collections(
            self.properties, self.addresses, {"SWPAR-1", "SWPAR-2"}, self.codes,
            canonical_parcel_by_candidate={"SWPAR-1": "SWP-A", "SWPAR-2": "SWP-B"},
            canonical_address_by_source={"SWADDR-1": "SWA-A", "SWADDR-2": "SWA-B"},
        )
        self.assertEqual(result["bp02_design_parcel_identity_matches"], 2)
        self.assertEqual(result["bp02_design_address_identity_matches"], 2)
        self.assertEqual(result["canonical_parcel_identity_matches"], 0)
        self.assertEqual(result["canonical_address_identity_matches"], 0)
        self.assertEqual(result["properties_still_awaiting_bp02_parcel_binding"], 2)
        self.assertEqual(result["addresses_still_awaiting_bp02_address_binding"], 2)
        self.assertEqual(result["canonical_binding_status"],
                         "DESIGN_IDENTITIES_BOUND_OPERATIONAL_RELEASE_BLOCKED")
        self.assertFalse(result["operational_approval"])
        self.assertFalse(result["database_write_performed"])

    def test_missing_candidate_parcel_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "source parcel candidate is unresolved"):
            reconcile_collections(
                self.properties, self.addresses, {"SWPAR-1"}, self.codes
            )

    def test_mismatched_property_address_relationship_fails_closed(self):
        broken = [dict(row) for row in self.addresses]
        broken[0]["property_id"] = "SWPROP-2"
        with self.assertRaisesRegex(ValueError, "primary BP04 address link"):
            reconcile_collections(
                self.properties, broken, {"SWPAR-1", "SWPAR-2"}, self.codes
            )

    def test_unknown_road_or_neighbourhood_entity_code_fails_closed(self):
        broken = [dict(row) for row in self.addresses]
        broken[0]["road_id"] = "UNMAPPED-ROAD"
        with self.assertRaisesRegex(ValueError, "road ID is not a BP-02 entity_code"):
            reconcile_collections(
                self.properties, broken, {"SWPAR-1", "SWPAR-2"}, self.codes
            )

    def test_duplicate_address_id_fails_closed(self):
        broken = [dict(row) for row in self.addresses]
        broken[1]["address_id"] = "SWADDR-1"
        with self.assertRaisesRegex(ValueError, "duplicate BP04 address ID"):
            reconcile_collections(
                self.properties, broken, {"SWPAR-1", "SWPAR-2"}, self.codes
            )


if __name__ == "__main__":
    unittest.main()
