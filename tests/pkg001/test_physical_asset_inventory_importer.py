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

    def test_geojson_payload_checksum_is_deterministic(self):
        payload = _geojson("Point", [10.5, 20.25])
        self.assertEqual(payload, {"type": "Point", "coordinates": [10.5, 20.25]})
        self.assertEqual(_geometry_hash(payload), _geometry_hash(copy.deepcopy(payload)))


if __name__ == "__main__":
    unittest.main()
