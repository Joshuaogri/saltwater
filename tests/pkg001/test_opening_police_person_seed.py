import gzip
import json
import tempfile
import unittest
from pathlib import Path

from runtime.naming import normalize_name, pg_trgm_similarity
from runtime.opening_police_person_seed import (
    TARGET_COUNT,
    build_opening_police_person_seed,
)


class OpeningPolicePersonSeedTests(unittest.TestCase):
    def test_seed_is_deterministic_and_manifest_hash_matches(self):
        first = build_opening_police_person_seed()
        second = build_opening_police_person_seed()
        self.assertEqual(first, second)
        digest = first.pop("manifest_sha256")
        import hashlib
        canonical = json.dumps(first, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(digest, hashlib.sha256(canonical).hexdigest())

    def test_exactly_500_unique_full_names_and_stable_candidate_refs(self):
        payload = build_opening_police_person_seed()
        rows = payload["records"]
        self.assertEqual(len(rows), TARGET_COUNT)
        self.assertEqual(len({normalize_name(row["display_name"]) for row in rows}), TARGET_COUNT)
        self.assertEqual([row["candidate_ref"] for row in rows],
                         [f"SWPSEED-{i:06d}" for i in range(1, TARGET_COUNT + 1)])
        self.assertEqual(len({row["source_ref"] for row in rows}), TARGET_COUNT)

    def test_no_internal_near_duplicate_names_above_registry_threshold(self):
        names = [row["display_name"] for row in build_opening_police_person_seed()["records"]]
        for index, name in enumerate(names):
            for other in names[index + 1:]:
                self.assertLessEqual(pg_trgm_similarity(name, other), 0.90)

    def test_candidates_do_not_invent_personal_or_employment_facts(self):
        payload = build_opening_police_person_seed()
        self.assertEqual(payload["category_allocation_status"],
                         "NOT_ASSIGNED_PENDING_BP05_BP06_STAFFING_ALLOCATION")
        for row in payload["records"]:
            self.assertIsNone(row["person_id"])
            self.assertIsNone(row["personnel_category"])
            self.assertEqual(row["identity_status"], "UNMATERIALISED_CANDIDATE")
            self.assertEqual(row["name_reservation_status"],
                             "PENDING_AUTHORITATIVE_REGISTRY_CHECK")
            self.assertEqual(set(row), {
                "candidate_ref", "source_ref", "given_name", "middle_name",
                "family_name", "display_name", "identity_status",
                "name_reservation_status", "personnel_category", "person_id",
            })

    def test_seed_is_not_marked_as_production_import_authority(self):
        payload = build_opening_police_person_seed()
        self.assertFalse(payload["production_import_authorized"])
        self.assertEqual(payload["identity_materialisation_status"],
                         "CANDIDATES_ONLY_NO_BP03_PERSON_ROWS_CREATED")


if __name__ == "__main__":
    unittest.main()
