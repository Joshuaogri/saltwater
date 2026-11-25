import json
import unittest
from pathlib import Path

from shapely.geometry import Point, Polygon

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory


class PhysicalAssetInventoryGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
        cls.source = source
        cls.candidates = build_candidates(source)
        cls.dossiers = build_parcel_dossiers(source, cls.candidates)
        cls.manifest = build_asset_inventory(source, cls.candidates, cls.dossiers)

    def test_all_parcel_candidates_have_a_property_site(self):
        self.assertEqual(self.manifest["generation"]["property_count"], 420)
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
                            for row in profiles["access_points"]))

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
            self.assertEqual(len(row["geometry_coordinates"]), 2)
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
        self.assertEqual(len(proximity), 4)
        self.assertTrue(all(row["contact_type"] == "POINT_CONTACT_ONLY"
                            for row in proximity))

    def test_geometry_audit_matches_generated_buildings(self):
        audit = [row for row in self.manifest["geometry_audit"] if "building" in row]
        self.assertEqual(len(audit), self.manifest["generation"]["building_count"])
        self.assertTrue(all(row["footprint_inside_property"] for row in audit))


if __name__ == "__main__":
    unittest.main()
