import copy
import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.physical_asset_inventory_importer import validate_manifests, _geometry_hash, _geojson


class PhysicalAssetInventoryImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
        cls.candidates = build_candidates(source)
        cls.dossiers = build_parcel_dossiers(source, cls.candidates)
        cls.inventory = build_asset_inventory(source, cls.candidates, cls.dossiers)

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
        self.assertEqual(len(connectors), 768)
        validate_manifests(self.inventory, self.candidates, self.dossiers)
        proximity = [row for row in connectors
                     if row["connector_type"] == "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE"]
        self.assertEqual(len(proximity), 4)
        self.assertTrue(all(row["frontage_candidate_id"] is None
                            and row["road_connection_candidate_id"]
                            and row["contact_type"] == "POINT_CONTACT_ONLY"
                            for row in proximity))

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
