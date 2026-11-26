import copy
import hashlib
import json
import unittest

from runtime.parcel_dossier_importer import validate_manifest
from bp04_03_stage_e_test_support import stage_e_parcel_inputs


class ParcelDossierImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.candidates, cls.manifest = stage_e_parcel_inputs()

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

    def test_point_contact_road_reserve_candidate_is_validated(self):
        proximity_rows = [
            access for row in self.manifest["parcels"] for access in row["access_candidates"]
            if access["candidate_type"] == "road_reserve_proximity_connection"
        ]
        self.assertEqual(len(proximity_rows), 2)
        self.assertTrue(all(
            access["contact_type"] == "POINT_CONTACT_ONLY"
            and access["frontage_candidate_id"] is None
            and access["road_connection_candidate_id"]
            and len(access["road_segment_ids"]) == 1
            for access in proximity_rows
        ))
        bad = copy.deepcopy(self.manifest)
        target = next(
            access for row in bad["parcels"] for access in row["access_candidates"]
            if access["candidate_type"] == "road_reserve_proximity_connection"
        )
        target["road_connection_candidate_id"] = None
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "proximity candidate is incomplete"):
            validate_manifest(bad, self.candidates)

    def test_operational_access_or_address_claims_are_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["summary"]["operational_access_points_created"] = 1
        self._rehash(bad)
        with self.assertRaisesRegex(ValueError, "operational access points"):
            validate_manifest(bad, self.candidates)


if __name__ == "__main__":
    unittest.main()
