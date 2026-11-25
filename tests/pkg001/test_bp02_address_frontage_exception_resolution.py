import unittest

from runtime.bp02_address_frontage_exception_resolution import resolve_address_frontage_exceptions


class BP02AddressFrontageExceptionResolutionTests(unittest.TestCase):
    def setUp(self):
        self.geo = {"roads": [
            {"id": "R-SRC", "name": "Original Street", "class": "local_street"},
            {"id": "R-ALT", "name": "Alternative Avenue", "class": "local_street"},
            {"id": "R-BRIDGE", "name": "Harbour Bridge", "class": "bridge"},
        ]}
        self.reconciliation = {"address_frontage_exceptions_building_access_crosscheck": [
            {
                "source_address_id": "A1", "source_candidate_parcel_id": "P1",
                "source_road_id": "R-SRC", "candidate_frontage_road_ids": ["R-ALT"],
                "building_access_road_candidate_status": "NO_BUILDING_ON_PROPERTY_SITE",
                "building_access_road_candidate_ids": [],
                "building_access_road_candidate_details": {},
                "status": "ADDRESS_ROAD_DIFFERS_FROM_PARCEL_FRONTAGE_CANDIDATE",
            },
            {
                "source_address_id": "A2", "source_candidate_parcel_id": "P2",
                "source_road_id": "R-BRIDGE", "candidate_frontage_road_ids": [],
                "building_access_road_candidate_status": "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET",
                "building_access_road_candidate_ids": ["R-BRIDGE"],
                "building_access_road_candidate_details": {"R-BRIDGE": {
                    "candidate_type": "road_reserve_proximity_connection",
                    "contact_type": "POINT_CONTACT_ONLY",
                }},
                "status": "NO_PARCEL_FRONTAGE_CANDIDATE",
            },
        ]}

    def test_unique_frontage_is_identified_without_rewriting_source_address(self):
        result = resolve_address_frontage_exceptions(self.reconciliation, self.geo)
        row = result["records"][0]
        self.assertEqual(row["proposed_frontage_road_id"], "R-ALT")
        self.assertEqual(row["geometry_disposition"],
                         "UNIQUE_PARCEL_FRONTAGE_IDENTIFIED_SOURCE_ADDRESS_NOT_CONFIRMED")
        self.assertEqual(row["source_road_id"], "R-SRC")
        self.assertFalse(row["canonical_address_corrected"])

    def test_bridge_point_contact_is_not_promoted_to_frontage(self):
        result = resolve_address_frontage_exceptions(self.reconciliation, self.geo)
        row = result["records"][1]
        self.assertEqual(row["geometry_disposition"],
                         "BRIDGE_POINT_CONTACT_ONLY_NOT_STREET_FRONTAGE")
        self.assertIsNone(row["proposed_frontage_road_id"])
        self.assertFalse(row["operational_access_approved"])

    def test_duplicate_exception_fails_closed(self):
        broken = {"address_frontage_exceptions_building_access_crosscheck":
                  self.reconciliation["address_frontage_exceptions_building_access_crosscheck"] * 2}
        with self.assertRaisesRegex(ValueError, "Duplicate frontage exception"):
            resolve_address_frontage_exceptions(broken, self.geo)

    def test_missing_source_road_fails_closed(self):
        broken = {"address_frontage_exceptions_building_access_crosscheck": [
            dict(self.reconciliation["address_frontage_exceptions_building_access_crosscheck"][0],
                 source_road_id="MISSING")
        ]}
        with self.assertRaisesRegex(ValueError, "source road is missing"):
            resolve_address_frontage_exceptions(broken, self.geo)


if __name__ == "__main__":
    unittest.main()
