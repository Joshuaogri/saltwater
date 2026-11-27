import copy
import gzip
import hashlib
import json
import unittest

from runtime.opening_resident_dwelling_allocation import (
    TARGET_COUNT,
    _stable_id,
    _load_sources,
    _sha256,
    build_opening_resident_dwelling_allocation,
)


class OpeningResidentDwellingAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build_opening_resident_dwelling_allocation()

    def test_allocation_is_deterministic_and_manifest_hash_matches(self):
        first = self.payload
        second = build_opening_resident_dwelling_allocation()
        self.assertEqual(first, second)
        without_hash = copy.deepcopy(first)
        digest = without_hash.pop("manifest_sha256")
        canonical = json.dumps(without_hash, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(digest, hashlib.sha256(canonical).hexdigest())

    def test_allocation_is_bound_to_current_resident_and_property_source_hashes(self):
        resident, resident_raw, _, property_raw = _load_sources()
        sources = self.payload["source_datasets"]
        self.assertEqual(
            sources["resident_candidates"]["manifest_sha256"],
            resident["manifest_sha256"],
        )
        self.assertEqual(
            sources["resident_candidates"]["compressed_sha256"],
            _sha256(resident_raw),
        )
        self.assertEqual(
            sources["property_world"]["compressed_sha256"],
            _sha256(property_raw),
        )

    def test_exact_candidate_and_eligible_dwelling_reconciliation(self):
        p = self.payload
        self.assertEqual(p["candidate_count"], TARGET_COUNT)
        self.assertEqual(p["allocated_candidate_count"], TARGET_COUNT)
        self.assertEqual(p["eligible_dwelling_count"], 55558)
        self.assertEqual(p["unallocated_eligible_dwelling_count"], 55558 - TARGET_COUNT)
        self.assertEqual(sum(x["candidate_allocation_count"] for x in p["neighbourhood_allocation"]), TARGET_COUNT)
        self.assertEqual(sum(x["eligible_dwelling_count"] for x in p["neighbourhood_allocation"]), 55558)

    def test_candidates_and_dwelling_units_are_one_to_one(self):
        rows = self.payload["records"]
        self.assertEqual(len(rows), TARGET_COUNT)
        self.assertEqual(len({r["candidate_ref"] for r in rows}), TARGET_COUNT)
        self.assertEqual(len({r["unit_id"] for r in rows}), TARGET_COUNT)
        self.assertTrue(all(r["person_id"] is None for r in rows))

    def test_bp02_identity_links_follow_released_hash_rules(self):
        for row in self.payload["records"]:
            self.assertEqual(row["bp02_parcel_source_id"], _stable_id("SWP", row["source_candidate_parcel_id"]))
            self.assertEqual(row["bp02_address_source_id"], _stable_id("SWA", row["bp04_address_id"]))
            self.assertEqual(row["bp04_address_source_ref"], f"SW-GEO-V1:{row['source_candidate_parcel_id']}")

    def test_neighbourhood_allocation_is_proportional_and_deterministic(self):
        rows = self.payload["neighbourhood_allocation"]
        self.assertGreaterEqual(len(rows), 1)
        for row in rows:
            self.assertGreaterEqual(row["candidate_allocation_count"], 0)
            self.assertLessEqual(row["candidate_allocation_count"], row["eligible_dwelling_count"])

    def test_no_population_household_or_production_records_are_created(self):
        p = self.payload
        self.assertEqual(p["materialisation_status"],
                         "CANDIDATE_DWELLING_MATCHES_ONLY_NO_CANONICAL_PERSON_RESIDENCE_OR_HOUSEHOLD_ROWS")
        self.assertEqual(p["person_records_created"], 0)
        self.assertEqual(p["residence_records_created"], 0)
        self.assertEqual(p["household_records_created"], 0)
        self.assertEqual(p["occupancy_capacity_status"], "NOT_ASSESSED")
        self.assertFalse(p["production_seed_authorized"])
        self.assertEqual(p["population_reconciliation"], {
            "civilian_usual_residents_target": 9000,
            "active_police_service_people_target": 500,
            "distinct_opening_people_target": 9500,
            "hard_population_cap": 10000,
            "unused_opening_headroom": 500,
        })


if __name__ == "__main__":
    unittest.main()
