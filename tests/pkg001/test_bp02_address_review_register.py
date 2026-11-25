import unittest

from runtime.bp02_address_review_register import build_address_review_register


class BP02AddressReviewRegisterTests(unittest.TestCase):
    def setUp(self):
        self.identity = {
            "register_id": "SW-PARCEL-ADDRESS-IDENTITY-V1",
            "parcel_identity_count": 2,
            "address_identity_count": 3,
            "parcels": [
                {"source_candidate_parcel_id": "C1", "parcel_id": "SWP-1"},
                {"source_candidate_parcel_id": "C2", "parcel_id": "SWP-2"},
            ],
            "addresses": [
                {
                    "source_address_id": "A1", "address_id": "SWA-1",
                    "property_id": "P1", "parcel_id": "SWP-1",
                    "source_candidate_parcel_id": "C1", "road_id": "R1",
                    "candidate_frontage_road_ids": ["R1"],
                    "address_road_candidate_id": "R1",
                    "road_frontage_match_status": "ROAD_MATCHES_PARCEL_FRONTAGE_CANDIDATE",
                },
                {
                    "source_address_id": "A2", "address_id": "SWA-2",
                    "property_id": "P2", "parcel_id": "SWP-2",
                    "source_candidate_parcel_id": "C2", "road_id": "R9",
                    "candidate_frontage_road_ids": ["R2"],
                    "address_road_candidate_id": "R2",
                    "road_frontage_match_status": "ADDRESS_ROAD_DIFFERS_FROM_PARCEL_FRONTAGE_CANDIDATE",
                },
                {
                    "source_address_id": "A3", "address_id": "SWA-3",
                    "property_id": "P2", "parcel_id": "SWP-2",
                    "source_candidate_parcel_id": "C2", "road_id": "R3",
                    "candidate_frontage_road_ids": [],
                    "address_road_candidate_id": None,
                    "road_frontage_match_status": "NO_PARCEL_FRONTAGE_CANDIDATE",
                },
            ],
        }
        self.access = {
            "address_count": 3,
            "address_access_road_results": [
                {
                    "source_address_id": "A1",
                    "candidate_access_road_ids": ["R1"],
                    "address_access_road_candidate_id": "R1",
                    "status": "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET",
                },
                {
                    "source_address_id": "A2",
                    "candidate_access_road_ids": [],
                    "address_access_road_candidate_id": None,
                    "status": "NO_BUILDING_ON_PROPERTY_SITE",
                },
                {
                    "source_address_id": "A3",
                    "candidate_access_road_ids": [],
                    "address_access_road_candidate_id": None,
                    "status": "NO_BUILDING_ON_PROPERTY_SITE",
                },
            ],
        }

    def build(self):
        return build_address_review_register(self.identity, self.access)

    def test_builds_complete_review_queue_and_preserves_source_roads(self):
        result = self.build()
        self.assertEqual(result["address_count"], 3)
        self.assertEqual(len(result["records"]), 3)
        self.assertTrue(result["all_source_roads_preserved"])
        self.assertEqual([row["source_road_id"] for row in result["records"]], ["R1", "R9", "R3"])

    def test_prioritizes_frontage_conflicts_and_missing_frontage(self):
        result = self.build()
        by_id = {row["source_address_id"]: row for row in result["records"]}
        self.assertEqual(by_id["A2"]["review_class"], "ROAD_REFERENCE_CONFLICT")
        self.assertEqual(by_id["A2"]["review_priority"], "P1")
        self.assertEqual(by_id["A3"]["review_class"], "NO_PARCEL_FRONTAGE_EVIDENCE")
        self.assertEqual(by_id["A3"]["review_priority"], "P1")
        self.assertEqual(result["priority_1_review_count"], 2)

    def test_source_coherent_record_is_still_not_operationally_approved(self):
        row = self.build()["records"][0]
        self.assertEqual(row["review_class"], "SOURCE_CONTEXT_COHERENT_CANDIDATE")
        self.assertFalse(row["operational_address_approved"])
        self.assertFalse(row["operational_access_confirmed"])

    def test_missing_building_is_separate_from_frontage_conflict(self):
        result = self.build()
        row = next(row for row in result["records"] if row["source_address_id"] == "A2")
        self.assertEqual(row["review_class"], "ROAD_REFERENCE_CONFLICT")
        self.assertEqual(row["building_access_status"], "NO_BUILDING_ON_PROPERTY_SITE")

    def test_duplicate_or_missing_access_evidence_fails_closed(self):
        broken = dict(self.access)
        broken["address_access_road_results"] = self.access["address_access_road_results"][:2]
        with self.assertRaisesRegex(ValueError, "incomplete or duplicated"):
            build_address_review_register(self.identity, broken)

    def test_duplicate_source_address_fails_closed(self):
        broken = dict(self.identity)
        broken["addresses"] = self.identity["addresses"] + [dict(self.identity["addresses"][0])]
        broken["address_identity_count"] = 4
        with self.assertRaisesRegex(ValueError, "Duplicate source address"):
            build_address_review_register(broken, self.access)

    def test_repeat_build_is_deterministic_and_read_only(self):
        first, second = self.build(), self.build()
        self.assertEqual(first, second)
        self.assertFalse(first["database_write_performed"])
        self.assertEqual(first["operational_addresses_approved"], 0)


if __name__ == "__main__":
    unittest.main()
