import unittest

from runtime.bp02_address_access_reconciliation import reconcile_building_access_roads


class BP02AddressAccessReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.properties = [
            {"property_id": "P1", "source_candidate_parcel_id": "C1"},
            {"property_id": "P2", "source_candidate_parcel_id": "C2"},
            {"property_id": "P3", "source_candidate_parcel_id": "C3"},
        ]
        self.addresses = [
            {"address_id": "A1", "property_id": "P1", "road_id": "R1"},
            {"address_id": "A2", "property_id": "P2", "road_id": "R9"},
            {"address_id": "A3", "property_id": "P3", "road_id": "R3"},
        ]
        self.dossiers = {"parcels": [
            {"dossier": {"candidate_parcel_id": "C1"}, "access_candidates": [
                {"access_candidate_id": "AC1", "road_id": "R1", "candidate_type": "frontage", "contact_type": "line"},
                {"access_candidate_id": "AC2", "road_id": "R2", "candidate_type": "frontage", "contact_type": "line"},
            ]},
            {"dossier": {"candidate_parcel_id": "C2"}, "access_candidates": [
                {"access_candidate_id": "AC3", "road_id": "R2", "candidate_type": "proximity", "contact_type": "point"},
            ]},
            {"dossier": {"candidate_parcel_id": "C3"}, "access_candidates": []},
        ]}
        self.assets = {
            "buildings": [
                {"candidate_building_id": "B1", "source_candidate_parcel_id": "C1"},
                {"candidate_building_id": "B2", "source_candidate_parcel_id": "C2"},
            ],
            "access_points": [
                {"candidate_access_point_id": "X1", "building_id": "B1", "road_link_candidate_id": "AC1"},
                {"candidate_access_point_id": "X4", "building_id": "B1", "road_link_candidate_id": "AC2"},
                {"candidate_access_point_id": "X2", "building_id": "B2", "road_link_candidate_id": "AC3"},
            ],
        }

    def test_source_road_disambiguates_multiple_access_candidates(self):
        result = reconcile_building_access_roads(self.properties, self.addresses, self.dossiers, self.assets)
        row = result["address_access_road_results"][0]
        self.assertEqual(row["candidate_access_road_ids"], ["R1", "R2"])
        self.assertEqual(row["address_access_road_candidate_id"], "R1")
        self.assertEqual(row["status"], "SOURCE_ROAD_MATCHES_BUILDING_ACCESS_SET")

    def test_single_alternative_access_road_is_flagged_not_promoted(self):
        result = reconcile_building_access_roads(self.properties, self.addresses, self.dossiers, self.assets)
        row = result["address_access_road_results"][1]
        self.assertEqual(row["address_access_road_candidate_id"], "R2")
        self.assertEqual(row["status"], "SINGLE_ALTERNATIVE_BUILDING_ACCESS_ROAD_REQUIRES_REVIEW")
        self.assertFalse(result["operational_access_confirmed"])

    def test_no_building_access_candidate_remains_unresolved(self):
        result = reconcile_building_access_roads(self.properties, self.addresses, self.dossiers, self.assets)
        row = result["address_access_road_results"][2]
        self.assertIsNone(row["address_access_road_candidate_id"])
        self.assertEqual(row["status"], "NO_BUILDING_ON_PROPERTY_SITE")
        self.assertEqual(result["property_sites_without_buildings"], 1)

    def test_existing_building_without_road_candidate_is_distinguished(self):
        assets = {
            "buildings": self.assets["buildings"] + [
                {"candidate_building_id": "B3", "source_candidate_parcel_id": "C3"}
            ],
            "access_points": self.assets["access_points"] + [
                {"candidate_access_point_id": "X3", "building_id": "B3", "road_link_candidate_id": None}
            ],
        }
        result = reconcile_building_access_roads(self.properties, self.addresses, self.dossiers, assets)
        row = result["address_access_road_results"][2]
        self.assertEqual(row["status"], "BUILDING_ACCESS_ROAD_CANDIDATE_UNRESOLVED")
        self.assertEqual(result["unresolved_building_access_point_count"], 1)

    def test_missing_candidate_reference_fails_closed(self):
        broken = dict(self.assets)
        broken["access_points"] = [dict(self.assets["access_points"][0], road_link_candidate_id="MISSING")]
        with self.assertRaisesRegex(ValueError, "road connection candidate is unresolved"):
            reconcile_building_access_roads(self.properties, self.addresses, self.dossiers, broken)


if __name__ == "__main__":
    unittest.main()
