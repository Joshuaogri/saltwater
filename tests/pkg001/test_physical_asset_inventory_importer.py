import copy
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from bp04_03_stage_e_test_support import stage_e_parcel_inputs, stage_e_asset_inventory
from runtime.physical_asset_inventory_importer import validate_manifests, _geometry_hash, _geojson, _report_progress


class PhysicalAssetInventoryImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.candidates, cls.dossiers = stage_e_parcel_inputs()
        cls.inventory = stage_e_asset_inventory()

    def test_progress_diagnostics_do_not_pollute_json_stdout(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            _report_progress("test_phase", 12.5)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(json.loads(stderr.getvalue()), {
            "stage_e_import_progress": "test_phase",
            "elapsed_ms": 12.5,
        })

    def test_valid_candidate_manifests_are_accepted(self):
        manifest_sha, candidate_set_id = validate_manifests(
            self.inventory, self.candidates, self.dossiers
        )
        self.assertEqual(manifest_sha, self.inventory["manifest_sha256"])
        self.assertEqual(candidate_set_id, self.candidates["candidate_set_id"])

    def test_tampered_inventory_is_rejected(self):
        tampered = copy.deepcopy(self.inventory)
        tampered["properties"][0]["display_name"] = "Tampered"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validate_manifests(tampered, self.candidates, self.dossiers)

    def test_mismatched_parcel_source_is_rejected(self):
        tampered = copy.deepcopy(self.dossiers)
        tampered["candidate_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "candidate manifest reference"):
            validate_manifests(self.inventory, self.candidates, tampered)

    def test_wrong_parent_identity_is_rejected(self):
        tampered = copy.deepcopy(self.inventory)
        tampered["premises"][0]["property_id"] = tampered["premises"][0]["building_id"]
        tampered["manifest_sha256"] = __import__(
            "runtime.physical_asset_inventory_importer", fromlist=["_sha"]
        )._sha(tampered)
        with self.assertRaisesRegex(ValueError, "single-parent"):
            validate_manifests(tampered, self.candidates, self.dossiers)

    def test_generated_access_locations_cannot_become_operational(self):
        tampered = copy.deepcopy(self.inventory)
        tampered["generation"]["operational_access_points_created"] = 1
        tampered["manifest_sha256"] = __import__(
            "runtime.physical_asset_inventory_importer", fromlist=["_sha"]
        )._sha(tampered)
        with self.assertRaisesRegex(ValueError, "operational access"):
            validate_manifests(tampered, self.candidates, self.dossiers)

    def test_source_entity_code_reconciliation_must_be_complete(self):
        self.assertEqual(self.inventory["generation"]["resolved_source_entity_code_mappings"], 100)
        self.assertEqual(self.inventory["generation"]["unresolved_source_entity_code_mappings"], 0)
        self.assertEqual(self.inventory["generation"]["unresolved_source_spatial_mappings"], 0)
        tampered = copy.deepcopy(self.inventory)
        tampered["generation"]["unresolved_source_entity_code_mappings"] = 1
        tampered["manifest_sha256"] = __import__(
            "runtime.physical_asset_inventory_importer", fromlist=["_sha"]
        )._sha(tampered)
        with self.assertRaisesRegex(ValueError, "100 source entity_code mappings"):
            validate_manifests(tampered, self.candidates, self.dossiers)

    def test_connector_candidates_are_complete_and_non_operational(self):
        connectors = self.inventory["access_connectors"]
        self.assertEqual(len(connectors), 2948)
        validate_manifests(self.inventory, self.candidates, self.dossiers)
        proximity = [row for row in connectors
                     if row["connector_type"] == "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE"]
        self.assertEqual(len(proximity), 4)
        self.assertTrue(all(row["frontage_candidate_id"] is None
                            and row["road_connection_candidate_id"]
                            and row["contact_type"] == "POINT_CONTACT_ONLY"
                            for row in proximity))

    def test_connector_candidates_include_multi_segment_geometry(self):
        connectors = self.inventory["access_connectors"]
        multi_segment = [row for row in connectors
                         if len(row["geometry_coordinates"]) > 2]
        self.assertTrue(multi_segment, "visibility routing must retain multi-segment paths")
        for row in connectors:
            coordinates = row["geometry_coordinates"]
            self.assertGreaterEqual(len(coordinates), 2)
            self.assertNotEqual(coordinates[0], coordinates[-1])
            self.assertTrue(all(isinstance(point, list) and len(point) == 2
                                for point in coordinates))

    def test_connector_candidates_cannot_claim_construction_or_access_rights(self):
        for field, value in (("constructed_state", "constructed"),
                             ("surface_code", "asphalt"),
                             ("legal_access_state", "confirmed"),
                             ("emergency_egress_state", "available")):
            tampered = copy.deepcopy(self.inventory)
            tampered["access_connectors"][0][field] = value
            tampered["manifest_sha256"] = __import__(
                "runtime.physical_asset_inventory_importer", fromlist=["_sha"]
            )._sha(tampered)
            with self.assertRaisesRegex(ValueError, "unknown|not_assessed|Unassessed"):
                validate_manifests(tampered, self.candidates, self.dossiers)

    def test_connector_candidate_must_retain_road_segment_lineage(self):
        tampered = copy.deepcopy(self.inventory)
        tampered["access_connectors"][0]["road_segment_ids"] = []
        tampered["manifest_sha256"] = __import__(
            "runtime.physical_asset_inventory_importer", fromlist=["_sha"]
        )._sha(tampered)
        with self.assertRaisesRegex(ValueError, "road-segment lineage"):
            validate_manifests(tampered, self.candidates, self.dossiers)

    def test_connector_candidate_must_reference_existing_access_point(self):
        tampered = copy.deepcopy(self.inventory)
        tampered["access_connectors"][0]["access_point_candidate_id"] = "MISSING"
        tampered["manifest_sha256"] = __import__(
            "runtime.physical_asset_inventory_importer", fromlist=["_sha"]
        )._sha(tampered)
        with self.assertRaisesRegex(ValueError, "missing access-point"):
            validate_manifests(tampered, self.candidates, self.dossiers)

    def test_geojson_payload_checksum_is_deterministic(self):
        payload = _geojson("Point", [10.5, 20.25])
        self.assertEqual(payload, {"type": "Point", "coordinates": [10.5, 20.25]})
        self.assertEqual(_geometry_hash(payload), _geometry_hash(copy.deepcopy(payload)))


if __name__ == "__main__":
    unittest.main()
