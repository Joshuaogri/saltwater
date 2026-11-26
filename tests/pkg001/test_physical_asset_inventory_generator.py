import unittest

from shapely.geometry import Point, Polygon

from bp04_03_stage_e_test_support import stage_e_parcel_inputs, stage_e_asset_inventory
from runtime.physical_asset_inventory_generator import build_asset_inventory


class PhysicalAssetInventoryGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.candidates, cls.dossiers = stage_e_parcel_inputs()
        cls.manifest = stage_e_asset_inventory()

    def test_global_hub_vertical_profiles_are_deterministic_and_use_sensitive(self):
        from runtime.physical_asset_inventory_generator import _storey_count
        for parcel in self.candidates["parcels"]:
            first = _storey_count(parcel["land_use_code"], parcel["source_district_id"], parcel["candidate_parcel_id"])
            second = _storey_count(parcel["land_use_code"], parcel["source_district_id"], parcel["candidate_parcel_id"])
            self.assertEqual(first, second)
            self.assertGreaterEqual(first, 1)
            self.assertLessEqual(first, 58)
        commercial = [row for row in self.manifest["buildings"] if row["building_use"] == "office"]
        self.assertTrue(commercial)
        self.assertGreaterEqual(max(row["storeys_above"] for row in commercial), 42)
        self.assertTrue(all(row["height_profile_code"] == "GLOBAL-ESTATE-VERTICAL-V1" for row in self.manifest["buildings"]))

    def test_all_parcel_candidates_have_a_property_site(self):
        self.assertEqual(self.manifest["generation"]["property_count"], 420)
        self.assertGreater(self.manifest["generation"]["building_count"], 420)
        buildings_by_property = {x["property_id"] for x in self.manifest["buildings"]}
        expected_without_buildings = sum(
            1 for x in self.manifest["properties"]
            if x["candidate_property_id"] not in buildings_by_property
        )
        self.assertEqual(
            self.manifest["generation"]["properties_without_buildings"],
            expected_without_buildings,
        )
        self.assertEqual(
            {p["source_candidate_parcel_id"] for p in self.manifest["properties"]},
            {p["candidate_parcel_id"] for p in self.candidates["parcels"]},
        )

    def test_nested_physical_asset_types_are_populated(self):
        counts = self.manifest["generation"]
        self.assertGreater(counts["building_count"], 0)
        self.assertGreater(counts["premises_count"], counts["building_count"])
        self.assertGreater(counts["unit_count"], counts["premises_count"])
        self.assertEqual(counts["access_point_candidate_count"], counts["building_count"] * 2)

    def test_candidate_geometry_is_valid_and_contained(self):
        properties = {
            row["candidate_property_id"]: Polygon(row["geometry"][0], row["geometry"][1:])
            for row in self.manifest["properties"]
        }
        for row in self.manifest["buildings"]:
            footprint = Polygon(row["geometry"][0], row["geometry"][1:])
            self.assertTrue(footprint.is_valid)
            self.assertGreater(footprint.area, 0)
            self.assertTrue(properties[row["property_id"]].covers(footprint))
        building_geometry = {
            row["candidate_building_id"]: Polygon(row["geometry"][0], row["geometry"][1:])
            for row in self.manifest["buildings"]
        }
        for row in self.manifest["access_points"]:
            point = Point(row["point_m"])
            self.assertTrue(building_geometry[row["building_id"]].boundary.distance(point) <= 0.00001)

    def test_every_record_has_provenance_and_explicit_unknown_states(self):
        groups = ("properties", "buildings", "premises", "units", "access_points")
        for group in groups:
            self.assertTrue(self.manifest[group])
            for row in self.manifest[group]:
                self.assertTrue(row["source_ref"])
                self.assertTrue(row["actor_ref"])
                self.assertEqual(row["confidence_code"], "estimated")
                self.assertEqual(row["effective_from_tick"], 0)
        self.assertTrue(all(row["capacity_knowledge_state"] == "not_assessed"
                            for row in self.manifest["units"]))
        self.assertTrue(all(row["emergency_egress_state"] == "not_assessed"
                            and row["loading_capability_state"] == "not_assessed"
                            for row in self.manifest["access_points"]))

    def test_bp04_02_profiles_and_typed_child_detail_are_complete(self):
        profiles = self.manifest["profiles"]
        self.assertEqual(len(profiles["properties"]), len(self.manifest["properties"]))
        self.assertEqual(len(profiles["buildings"]), len(self.manifest["buildings"]))
        self.assertEqual(len(profiles["premises"]), len(self.manifest["premises"]))
        self.assertEqual(len(profiles["units"]), len(self.manifest["units"]))
        self.assertEqual(len(profiles["access_points"]), len(self.manifest["access_points"]))
        details = self.manifest["details"]
        for key in ("measurements", "building_levels", "building_components",
                    "premises_rooms", "utility_systems", "physical_features",
                    "condition_assessments", "asset_assertions"):
            self.assertGreater(len(details[key]), 0, key)
        self.assertEqual(details["physical_defects"], [])
        self.assertTrue(all(row["material_code"] == "unknown"
                            and row["condition_code"] == "not_assessed"
                            for row in details["building_components"]))
        self.assertTrue(all(row["condition_code"] == "not_assessed"
                            for row in details["condition_assessments"]))
        self.assertTrue(all(row["knowledge_state"] == "not_assessed"
                            for row in details["asset_assertions"]))
        self.assertTrue(all(row["emergency_egress"] is None
                            and row["loading_capable"] is None
                            and row["emergency_egress_state"] == "not_assessed"
                            and row["loading_capability_state"] == "not_assessed"
                            for row in profiles["access_points"]))

    def test_building_profile_values_match_database_check_constraints(self):
        allowed_forms = {"detached", "semi_detached", "terraced", "tower", "slab",
                         "courtyard", "shed", "pavilion", "underground", "other", "unknown"}
        allowed_classes = {"low_rise", "mid_rise", "high_rise", "industrial_span",
                           "lightweight", "civil_engineering", "other", "unknown"}
        profiles = {row["candidate_building_id"]: row for row in self.manifest["profiles"]["buildings"]}
        for building in self.manifest["buildings"]:
            self.assertIn(building["building_form"], allowed_forms)
            self.assertIn(building["structure_class"], allowed_classes)
            self.assertEqual(profiles[building["candidate_building_id"]]["building_form"],
                             building["building_form"])
            self.assertEqual(profiles[building["candidate_building_id"]]["structure_class"],
                             building["structure_class"])
            expected_class = ("high_rise" if building["storeys_above"] >= 20 else
                              "mid_rise" if building["storeys_above"] >= 8 else "low_rise")
            self.assertEqual(building["structure_class"], expected_class)

    def test_parent_relationships_match_bp04_identity_constraints(self):
        self.assertTrue(all(row["building_id"] and "property_id" not in row
                            for row in self.manifest["premises"]))
        self.assertTrue(all(row["premises_id"] and "building_id" not in row
                            for row in self.manifest["units"]))
        self.assertTrue(all(row["building_id"] and "premises_id" not in row
                            and "property_id" not in row
                            for row in self.manifest["access_points"]))

    def test_candidate_names_and_identity_codes_are_unique(self):
        groups = ("properties", "buildings", "premises", "units", "access_points")
        names = [row["display_name"] for group in groups for row in self.manifest[group]]
        self.assertEqual(len(names), len(set(name.casefold() for name in names)))
        for group, key in (
            ("properties", "candidate_property_id"),
            ("buildings", "candidate_building_id"),
            ("premises", "candidate_premises_id"),
            ("units", "candidate_unit_id"),
            ("access_points", "candidate_access_point_id"),
        ):
            values = [row[key] for row in self.manifest[group]]
            self.assertEqual(len(values), len(set(values)))


    def test_large_property_sites_receive_non_overlapping_building_campuses(self):
        grouped = {}
        for row in self.manifest["buildings"]:
            grouped.setdefault(row["property_id"], []).append(row)
        campuses = {pid: rows for pid, rows in grouped.items() if len(rows) > 1}
        self.assertGreater(len(campuses), 0)
        for pid, rows in campuses.items():
            footprints = [Polygon(x["geometry"][0], x["geometry"][1:]) for x in rows]
            for i, first in enumerate(footprints):
                for second in footprints[i+1:]:
                    self.assertFalse(first.intersects(second))
                    self.assertGreaterEqual(first.distance(second), 3.9)
            suffixes = [x["candidate_building_id"].rsplit("-", 1)[-1] for x in rows]
            self.assertEqual(len(suffixes), len(set(suffixes)))

    def test_manifest_is_deterministic_and_non_operational(self):
        second = build_asset_inventory(self.source, self.candidates, self.dossiers)
        self.assertEqual(self.manifest["manifest_sha256"], second["manifest_sha256"])
        self.assertFalse(self.manifest["operational_approval"])
        generation = self.manifest["generation"]
        self.assertEqual(generation["operational_spatial_ids_assigned"], 0)
        self.assertEqual(generation["canonical_addresses_created"], 0)
        self.assertEqual(generation["operational_access_points_created"], 0)
        self.assertEqual(generation["ownership_records_created"], 0)
        self.assertEqual(generation["tenancy_records_created"], 0)
        self.assertEqual(generation["occupancy_records_created"], 0)
        self.assertEqual(generation["business_assignments_created"], 0)
        self.assertEqual(generation["resolved_source_entity_code_mappings"], 100)
        self.assertEqual(generation["unresolved_source_entity_code_mappings"], 0)
        self.assertEqual(generation["unresolved_source_spatial_mappings"], 0)

    def test_access_connector_candidates_are_complete_and_fully_unverified(self):
        connectors = self.manifest["access_connectors"]
        self.assertEqual(len(connectors), self.manifest["generation"]["access_connector_candidate_count"])
        self.assertEqual(len(connectors), len(self.manifest["access_points"]))
        self.assertEqual(len({row["candidate_connector_id"] for row in connectors}), len(connectors))
        access_ids = {row["candidate_access_point_id"] for row in self.manifest["access_points"]}
        for row in connectors:
            self.assertIn(row["access_point_candidate_id"], access_ids)
            self.assertEqual(row["geometry_type"], "LineString")
            self.assertGreaterEqual(len(row["geometry_coordinates"]), 2)
            self.assertNotEqual(row["geometry_coordinates"][0], row["geometry_coordinates"][-1])
            self.assertGreaterEqual(row["length_m"], 0)
            self.assertEqual(row["geometry_status"], "UNREVIEWED_GEOMETRIC_LINE_ONLY")
            self.assertEqual(row["review_status"], "unreviewed_candidate")
            for field in ("constructed_state", "surface_code"):
                self.assertEqual(row[field], "unknown")
            for field in ("slope_state", "barrier_state", "pedestrian_suitability",
                          "vehicle_suitability", "accessibility_state", "legal_access_state",
                          "public_access_state", "emergency_egress_state"):
                self.assertEqual(row[field], "not_assessed")
            self.assertTrue(row["source_ref"])
            self.assertTrue(row["actor_ref"])
        proximity = [row for row in connectors
                     if row["connector_type"] == "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE"]
        self.assertGreaterEqual(len(proximity), 4)
        self.assertTrue(all(row["contact_type"] == "POINT_CONTACT_ONLY"
                            for row in proximity))

    def test_geometry_audit_matches_generated_buildings(self):
        audit = [row for row in self.manifest["geometry_audit"] if "building" in row]
        self.assertEqual(len(audit), self.manifest["generation"]["building_count"])
        self.assertTrue(all(row["footprint_inside_property"] for row in audit))


if __name__ == "__main__":
    unittest.main()
