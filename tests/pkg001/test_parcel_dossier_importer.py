import copy
import hashlib
import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.parcel_dossier_importer import validate_manifest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class ParcelDossierImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = build_candidates(SOURCE)
        cls.manifest = build_parcel_dossiers(SOURCE, cls.candidates)

    def _rehash(self, data):
        canonical = dict(data)
        canonical.pop("manifest_sha256", None)
        data["manifest_sha256"] = hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()

    def test_manifest_and_candidate_lineage_validate(self):
        self.assertEqual(validate_manifest(self.manifest, self.candidates), self.manifest["manifest_sha256"])

    def test_tampered_dossier_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["parcels"][0]["dossier"]["perimeter_m"] += 1
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "perimeter does not match"):
            validate_manifest(bad, self.candidates)

    def test_mismatched_candidate_manifest_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["candidate_manifest_sha256"] = "0" * 64
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "candidate manifest reference"):
            validate_manifest(bad, self.candidates)

    def test_missing_or_duplicate_parcel_identity_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["parcels"].pop()
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "do not match"):
            validate_manifest(bad, self.candidates)
        bad = copy.deepcopy(self.manifest)
        bad["parcels"].append(copy.deepcopy(bad["parcels"][0]))
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_manifest(bad, self.candidates)

    def test_operational_access_or_address_claims_are_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["summary"]["operational_access_points_created"] = 1
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "operational access points"):
            validate_manifest(bad, self.candidates)


if __name__ == "__main__":
    unittest.main()
