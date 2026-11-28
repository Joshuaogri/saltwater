import unittest
from unittest.mock import patch

from runtime.bp04_geography_reconciliation import (
    _resolve_geometry_manifests, reconcile_collections,
    reconcile_canonical_property_bindings,
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


class BP04CanonicalSpatialBindingTests(unittest.TestCase):
    def setUp(self):
        self.properties = []
        self.addresses = []
        self.parcels = []
        self.canonical_addresses = []
        for index in range(420):
            property_id = f"SWPROP-{index:03d}"
            address_id = f"SWADDR-{index:03d}"
            candidate_id = f"BPC-{index:03d}"
            parcel_id = f"SWP-{index:016X}"
            bp02_address_id = f"SWA-{index:016X}"
            self.properties.append({
                "property_id": property_id,
                "address_id": address_id,
                "source_candidate_parcel_id": candidate_id,
                "bp02_parcel_id": parcel_id,
                "bp02_address_id": bp02_address_id,
            })
            self.addresses.append({
                "address_id": address_id, "property_id": property_id,
                "bp02_parcel_id": parcel_id, "bp02_address_id": bp02_address_id,
            })
            self.parcels.append({
                "source_candidate_parcel_id": candidate_id, "parcel_id": parcel_id,
            })
            self.canonical_addresses.append({
                "source_address_id": address_id, "address_id": bp02_address_id,
                "parcel_id": parcel_id,
            })
        self.buildings = [{"building_id": "SWBLD-001", "property_id": "SWPROP-000"}]
        common = {
            "point_m": [10.0, 20.0],
            "bp02_coordinate_reference": "SW-LOCAL-METRE-GRID-V1",
            "effective_from_tick": 0, "effective_to_tick": None,
            "canonical_status": "active",
            "point_status": "CANONICAL_FICTIONAL_ACCESS_POINT",
        }
        self.access_points = [
            {
                **common, "access_point_id": "SWACC-001",
                "bp02_access_point_id": "SWACC-001",
                "bp02_locator_status": "BOUND_TO_BP02_ACCESS_POINT",
                "property_id": "SWPROP-000", "building_id": "SWBLD-001",
            },
            {
                **common, "access_point_id": "SWACC-SITE-001",
                "bp02_access_point_id": None,
                "bp02_locator_status": "BP04_SITE_LOCATOR_IN_BP02_LOCAL_CRS",
                "property_id": "SWPROP-001", "building_id": None,
            },
        ]
        self.canonical = {
            "parcels": self.parcels,
            "addresses": self.canonical_addresses,
            "access_points": [{
                "candidate_access_point_id": "SWACC-001",
                "building_id": "SWBLD-001", "point_m": [10.0, 20.0],
            }],
        }

    def _document(self):
        return {
            "tables": {
                "properties": {
                    "columns": list(self.properties[0]),
                    "rows": [[row.get(key) for key in self.properties[0]] for row in self.properties],
                },
                "addresses": {
                    "columns": list(self.addresses[0]),
                    "rows": [[row.get(key) for key in self.addresses[0]] for row in self.addresses],
                },
                "buildings": {
                    "columns": list(self.buildings[0]),
                    "rows": [[row.get(key) for key in self.buildings[0]] for row in self.buildings],
                },
                "access_points": {
                    "columns": list(self.access_points[0]),
                    "rows": [[row.get(key) for key in self.access_points[0]] for row in self.access_points],
                },
            }
        }

    def test_all_properties_addresses_and_access_locators_bind(self):
        result = reconcile_canonical_property_bindings(self._document(), self.canonical)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["bp02_parcel_bindings"], 420)
        self.assertEqual(result["bp02_address_bindings"], 420)
        self.assertEqual(result["bp02_building_access_point_bindings"], 1)
        self.assertEqual(result["bp04_site_access_locators"], 1)
        self.assertEqual(result["effective_dated_access_points"], 2)

    def test_missing_or_mismatched_parcel_binding_fails(self):
        self.properties[0]["bp02_parcel_id"] = "SWP-WRONG"
        with self.assertRaisesRegex(ValueError, "BP02 parcel ID is absent or mismatched"):
            reconcile_canonical_property_bindings(self._document(), self.canonical)

    def test_access_point_must_match_bp02_spatial_locator(self):
        self.access_points[0]["point_m"] = [11.0, 20.0]
        with self.assertRaisesRegex(ValueError, "BP02 access-point identity or spatial locator"):
            reconcile_canonical_property_bindings(self._document(), self.canonical)

    def test_access_point_effective_interval_must_be_valid(self):
        self.access_points[1]["effective_to_tick"] = 0
        with self.assertRaisesRegex(ValueError, "effective access-point interval is invalid"):
            reconcile_canonical_property_bindings(self._document(), self.canonical)



if __name__ == "__main__":
    unittest.main()
