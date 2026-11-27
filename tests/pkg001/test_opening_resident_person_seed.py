import json
import unittest
import hashlib

from runtime.naming import normalize_name
from runtime.opening_police_person_seed import build_opening_police_person_seed
from runtime.opening_resident_person_seed import (
    POPULATION_CAP, TARGET_COUNT, TOTAL_OPENING_COUNT,
    build_opening_resident_person_seed,
)


class OpeningResidentPersonSeedTests(unittest.TestCase):
    def test_seed_is_deterministic_and_manifest_hash_matches(self):
        first = build_opening_resident_person_seed()
        second = build_opening_resident_person_seed()
        self.assertEqual(first, second)
        digest = first.pop("manifest_sha256")
        canonical = json.dumps(first, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(digest, hashlib.sha256(canonical).hexdigest())

    def test_exactly_9000_unique_candidates_and_stable_refs(self):
        rows = build_opening_resident_person_seed()["records"]
        self.assertEqual(len(rows), TARGET_COUNT)
        self.assertEqual(len({normalize_name(row["display_name"]) for row in rows}), TARGET_COUNT)
        self.assertEqual([r["candidate_ref"] for r in rows],
                         [f"SWCIV-{i:06d}" for i in range(1, TARGET_COUNT + 1)])
        self.assertEqual(len({r["source_ref"] for r in rows}), TARGET_COUNT)

    def test_resident_and_police_cohorts_are_disjoint(self):
        police = {normalize_name(r["display_name"]) for r in build_opening_police_person_seed()["records"]}
        residents = {normalize_name(r["display_name"]) for r in build_opening_resident_person_seed()["records"]}
        self.assertEqual(len(police), 500)
        self.assertEqual(len(residents), TARGET_COUNT)
        self.assertFalse(police & residents)

    def test_exact_opening_population_arithmetic_and_unused_headroom(self):
        payload = build_opening_resident_person_seed()
        self.assertEqual(payload["population_reconciliation"], {
            "civilian_usual_residents": 9000,
            "active_police_service_people": 500,
            "distinct_opening_people_target": TOTAL_OPENING_COUNT,
            "hard_population_cap": POPULATION_CAP,
            "unused_opening_headroom": 500,
        })

    def test_no_demographic_or_residence_facts_are_fabricated(self):
        payload = build_opening_resident_person_seed()
        self.assertEqual(payload["identity_materialisation_status"],
                         "CANDIDATES_ONLY_NO_BP03_PERSON_ROWS_CREATED")
        self.assertEqual(payload["residence_assignment_status"],
                         "NOT_ASSIGNED_TO_BP02_ADDRESS_OR_PARCEL")
        self.assertFalse(payload["production_import_authorized"])
        for row in payload["records"]:
            self.assertIsNone(row["person_id"])
            self.assertEqual(row["identity_status"], "UNMATERIALISED_CANDIDATE")
            self.assertEqual(row["name_reservation_status"],
                             "PENDING_AUTHORITATIVE_REGISTRY_CHECK")
            self.assertEqual(row["residence_assignment_status"], "NOT_ASSIGNED")
            self.assertEqual(set(row), {
                "candidate_ref", "source_ref", "given_name", "middle_name",
                "family_name", "display_name", "cohort", "identity_status",
                "name_reservation_status", "residence_assignment_status", "person_id",
            })


if __name__ == "__main__":
    unittest.main()
