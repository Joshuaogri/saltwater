import unittest

from runtime.bp02_parcel_address_identity import build_identity_register


class BP02ParcelAddressIdentityTests(unittest.TestCase):
    def setUp(self):
        self.candidates = {
            "candidate_set_id": "fixture-v1",
            "parcels": [
                {
                    "candidate_parcel_id": "BPC-001",
                    "source_dataset": "SW-GEO-V1",
                    "source_district_id": "SW-D01",
                    "source_neighbourhood_id": "SW-D01-N1",
                    "geometry": [[[0, 0], [10, 0], [10, 10], [0, 0]]],
                    "area_m2": 50,
                    "geometry_quality": "candidate_unreviewed",
                    "road_frontage_segment_ids": ["SW-RSEG-1"],
                    "source_ref": "fixture:parcel:1",
                },
                {
                    "candidate_parcel_id": "BPC-002",
                    "source_dataset": "SW-GEO-V1",
                    "source_district_id": "SW-D02",
                    "source_neighbourhood_id": "SW-D02-N1",
                    "geometry": [[[10, 0], [20, 0], [20, 10], [10, 0]]],
                    "area_m2": 50,
                    "geometry_quality": "candidate_unreviewed",
                    "road_frontage_segment_ids": [],
                    "source_ref": "fixture:parcel:2",
                },
            ],
        }
        self.properties = [
            {"property_id": "SWPROP-1", "source_candidate_parcel_id": "BPC-001", "address_id": "SWADDR-1", "source_district_id": "SW-D01", "source_neighbourhood_id": "SW-D01-N1"},
            {"property_id": "SWPROP-2", "source_candidate_parcel_id": "BPC-002", "address_id": "SWADDR-2", "source_district_id": "SW-D02", "source_neighbourhood_id": "SW-D02-N1"},
        ]
        self.addresses = [
            {"address_id": "SWADDR-1", "property_id": "SWPROP-1", "district_id": "SW-D01", "neighbourhood_id": "SW-D01-N1", "road_id": "SW-R01", "building_number": "12"},
            {"address_id": "SWADDR-2", "property_id": "SWPROP-2", "district_id": "SW-D02", "neighbourhood_id": "SW-D02-N1", "road_id": "SW-R02", "building_number": None},
        ]
        self.codes = {"SW-D01", "SW-D02", "SW-D01-N1", "SW-D02-N1", "SW-R01", "SW-R02"}

    def build(self):
        return build_identity_register(self.candidates, self.properties, self.addresses, self.codes, {"SW-RSEG-1": "SW-R01"})

    def test_stable_ids_and_complete_design_linkage(self):
        result = self.build()
        self.assertEqual(result["parcel_identity_count"], 2)
        self.assertEqual(result["address_identity_count"], 2)
        self.assertEqual(result["property_primary_address_links"], 2)
        self.assertTrue(all(row["parcel_id"].startswith("SWP-") for row in result["parcels"]))
        self.assertTrue(all(row["address_id"].startswith("SWA-") for row in result["addresses"]))
        self.assertFalse(result["operational_approval"])
        self.assertTrue(all(row["operational_status"] == "NOT_APPROVED_FOR_OPERATIONAL_SEED" for row in result["addresses"]))
        self.assertEqual(result["addresses"][1]["source_address_attributes"]["building_number"], None)
        self.assertEqual(result["addresses"][0]["road_frontage_match_status"], "ROAD_MATCHES_PARCEL_FRONTAGE_CANDIDATE")
        self.assertEqual(result["addresses"][1]["road_frontage_match_status"], "NO_PARCEL_FRONTAGE_CANDIDATE")
        self.assertEqual(result["addresses"][0]["address_road_candidate_id"], "SW-R01")
        self.assertIsNone(result["addresses"][1]["address_road_candidate_id"])

    def test_duplicate_parcel_candidate_assignment_fails_closed(self):
        properties = [dict(row) for row in self.properties]
        properties[1]["source_candidate_parcel_id"] = "BPC-001"
        with self.assertRaisesRegex(ValueError, "one-to-one to properties"):
            build_identity_register(
                self.candidates, properties, self.addresses, self.codes,
                {"SW-RSEG-1": "SW-R01"},
            )

    def test_rebuild_is_deterministic(self):
        self.assertEqual(self.build(), self.build())

    def test_missing_frontage_is_not_fabricated(self):
        result = self.build()
        second = next(row for row in result["parcels"] if row["source_candidate_parcel_id"] == "BPC-002")
        self.assertEqual(second["frontage_segment_ids"], [])

    def test_multiple_frontage_roads_are_not_arbitrarily_selected(self):
        candidates = {
            "candidate_set_id": self.candidates["candidate_set_id"],
            "parcels": [dict(row) for row in self.candidates["parcels"]],
        }
        candidates["parcels"][0]["road_frontage_segment_ids"] = ["SW-RSEG-1", "SW-RSEG-2"]
        result = build_identity_register(
            candidates, self.properties, self.addresses, self.codes,
            {"SW-RSEG-1": "SW-R01", "SW-RSEG-2": "SW-R02"},
        )
        first = next(row for row in result["addresses"] if row["source_address_id"] == "SWADDR-1")
        self.assertEqual(first["address_road_candidate_status"], "SOURCE_ROAD_MATCHES_FRONTAGE_SET")
        self.assertEqual(first["address_road_candidate_id"], "SW-R01")
        self.assertEqual(first["candidate_frontage_road_ids"], ["SW-R01", "SW-R02"])

    def test_single_alternative_frontage_road_is_proposed_but_flagged_for_review(self):
        addresses = [dict(row) for row in self.addresses]
        addresses[0]["road_id"] = "SW-R02"
        result = build_identity_register(
            self.candidates, self.properties, addresses, self.codes,
            {"SW-RSEG-1": "SW-R01"},
        )
        first = next(row for row in result["addresses"] if row["source_address_id"] == "SWADDR-1")
        self.assertEqual(first["address_road_candidate_id"], "SW-R01")
        self.assertEqual(first["address_road_candidate_status"], "SINGLE_ALTERNATIVE_FRONTAGE_ROAD_REQUIRES_REVIEW")
        self.assertEqual(first["road_id"], "SW-R02")

    def test_unresolved_road_fails_closed(self):
        broken = [dict(row) for row in self.addresses]
        broken[0]["road_id"] = "NO-SUCH-ROAD"
        with self.assertRaisesRegex(ValueError, "road reference"):
            build_identity_register(self.candidates, self.properties, broken, self.codes)

    def test_duplicate_source_address_fails_closed(self):
        broken = [dict(row) for row in self.addresses]
        broken[1]["address_id"] = "SWADDR-1"
        with self.assertRaisesRegex(ValueError, "duplicate source address"):
            build_identity_register(self.candidates, self.properties, broken, self.codes)

    def test_orphan_property_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "one-to-one to properties"):
            build_identity_register(self.candidates, self.properties[:1], self.addresses, self.codes)


if __name__ == "__main__":
    unittest.main()
