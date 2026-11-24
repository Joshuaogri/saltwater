import copy
import hashlib
import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_candidate_importer import validate_manifest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class ParcelCandidateImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_candidates(SOURCE)

    def setUp(self):
        self.manifest = self.__class__.manifest

    def _rehash(self, data):
        canonical = dict(data)
        canonical.pop("manifest_sha256", None)
        data["manifest_sha256"] = hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()

    def test_manifest_checksum_and_dynamic_count_validate(self):
        self.assertEqual(validate_manifest(self.manifest), self.manifest["manifest_sha256"])
        self.assertEqual(len(self.manifest["parcels"]), self.manifest["generation"]["parcel_candidate_count"])

    def test_tampered_manifest_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["parcels"][0]["area_m2"] += 1
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validate_manifest(bad)

    def test_operational_manifest_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["operational_approval"] = True
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "Operationally approved"):
            validate_manifest(bad)

    def test_duplicate_ids_and_allocated_ids_are_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["parcels"].append(copy.deepcopy(bad["parcels"][0]))
        bad["generation"]["parcel_candidate_count"] += 1
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_manifest(bad)
        bad = copy.deepcopy(self.manifest)
        bad["parcels"][0]["candidate_spatial_id"] = 123
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "operational identifiers"):
            validate_manifest(bad)

    def test_every_polygon_ring_must_be_closed_and_valid(self):
        bad = copy.deepcopy(self.manifest)
        bad["parcels"][0]["geometry"][0][-1] = [0, 0]
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "closed polygon"):
            validate_manifest(bad)


if __name__ == "__main__":
    unittest.main()
