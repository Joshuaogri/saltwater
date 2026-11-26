import unittest

from runtime.bp02_fictional_geography_release import (
    build_fictional_bridge_assessments,
    build_canonical_geography_register,
)


class BP02FictionalGeographyReleaseTests(unittest.TestCase):
    def setUp(self):
        self.corridors = {
            "manifest_sha256": "corridor-digest",
            "route_corridors": [
                {
                    "source_connector_candidate_id": f"SWAC-{road}-{suffix}",
                    "candidate_route_corridor_id": f"SWRC-{road}-{suffix}",
                    "candidate_access_point_id": f"AP-{road}-{suffix}",
                    "candidate_building_id": f"BLD-{road}-{suffix}",
                    "candidate_property_id": f"PROP-{road}",
                    "source_candidate_parcel_id": f"PARCEL-{road}",
                    "road_id": road,
                    "centreline_length_m": 14.2,
                }
                for road in ("SWR-B1", "SWR-B2")
                for suffix in ("A", "B")
            ],
        }

    def test_four_fictional_bridge_connectors_are_assessed_and_approved(self):
        result = build_fictional_bridge_assessments(self.corridors)
        self.assertTrue(result["fictional_game_world_assessments"])
        self.assertEqual(result["assessment_count"], 4)
        self.assertEqual(result["assessed_count"], 4)
        self.assertEqual(result["operationally_approved_count"], 4)
        for row in result["records"]:
            self.assertTrue(row["fictional_assessment"])
            self.assertEqual(row["engineering_status"], "ASSESSED_PASS")
            self.assertTrue(row["operational_access_approved"])
            self.assertGreaterEqual(row["clear_width_m"], 4.0)
            self.assertGreaterEqual(row["vertical_clearance_m"], 4.5)
            self.assertTrue(row["step_free_access"])

    def test_missing_bridge_candidate_fails_closed(self):
        self.corridors["route_corridors"].pop()
        with self.assertRaisesRegex(ValueError, "expected two game connector candidates"):
            build_fictional_bridge_assessments(self.corridors)

    def test_canonical_release_promotes_420_addresses_and_all_five_access_decisions(self):
        identity = {
            "register_id": "SW-PARCEL-ADDRESS-IDENTITY-V1",
            "operational_approval": False,
            "property_primary_address_links": 420,
            "parcels": [
                {"parcel_id": f"SWP-{i:016X}", "source_candidate_parcel_id": f"PC-{i}"}
                for i in range(420)
            ],
            "addresses": [
                {
                    "address_id": f"SWA-{i:016X}",
                    "source_address_id": f"ADDR-{i}",
                    "property_id": "PROP-SWR-B1" if i == 0 else "PROP-SWR-B2" if i == 1 else f"PROP-{i}",
                    "parcel_id": f"SWP-{i:016X}",
                    "source_candidate_parcel_id": "PARCEL-SWR-B1" if i == 0 else "PARCEL-SWR-B2" if i == 1 else f"PC-{i}",
                    "road_id": "SWR-SOURCE",
                    "address_road_candidate_id": "SWR-01",
                }
                for i in range(420)
            ],
        }
        assets = {
            "access_points": [{"candidate_access_point_id": f"AP-{i}"} for i in range(420)],
            "access_connectors": [
                {
                    "candidate_connector_id": row["source_connector_candidate_id"],
                    "access_point_candidate_id": row["candidate_access_point_id"],
                }
                for row in self.corridors["route_corridors"]
            ],
        }
        engineering = build_fictional_bridge_assessments(self.corridors)
        dispositions = [
            {
                "source_address_id": f"ADDR-{i}",
                "property_id": "PROP-SWR-B1" if i == 0 else "PROP-SWR-B2" if i == 1 else f"PROP-{i}",
                "address_road_association_resolved": True,
                "resolved_access_road_id": "SWR-B1" if i == 0 else "SWR-B2" if i == 1 else "SWR-01",
                "geometry_disposition": "BRIDGE_ACCESS_CONNECTOR_CANDIDATE_TO_CONNECTED_PUBLIC_ROAD_NETWORK" if i < 2 else "UNIQUE_PARCEL_FRONTAGE_ROAD_ASSOCIATION_RESOLVED",
            }
            for i in range(5)
        ]
        exceptions = {
            "unresolved_exception_count": 0,
            "all_source_addresses_preserved": True,
            "records": dispositions,
        }
        result = build_canonical_geography_register(identity, assets, engineering, exceptions)
        self.assertEqual(result["parcel_count"], 420)
        self.assertEqual(result["address_count"], 420)
        self.assertEqual(result["property_primary_address_link_count"], 420)
        self.assertEqual(result["building_access_point_count"], 420)
        self.assertEqual(result["bridge_connector_count"], 4)
        self.assertEqual(result["resolved_address_exception_count"], 5)
        self.assertEqual(result["operational_release_status"], "RELEASED_FOR_GAMEPLAY")
        self.assertTrue(result["identity_register_operational_approval"])
        self.assertEqual(result["identity_register_release_status"], "RELEASED_FOR_GAMEPLAY")
        self.assertEqual(result["addresses"][0]["road_id"], "SWR-B1")
        self.assertEqual(result["addresses"][0]["source_road_id"], "SWR-SOURCE")
        self.assertEqual(len(result["addresses"][0]["access_connector_assessment_ids"]), 2)
        self.assertEqual(len(result["addresses"][1]["access_connector_assessment_ids"]), 2)
        self.assertTrue(all(row["canonical"] for row in result["parcels"]))
        self.assertTrue(all(row["canonical"] for row in result["addresses"]))

    def test_canonical_release_rejects_unresolved_address_exceptions(self):
        identity = {
            "register_id": "SW-PARCEL-ADDRESS-IDENTITY-V1",
            "property_primary_address_links": 420,
            "parcels": [{"parcel_id": f"P{i}"} for i in range(420)],
            "addresses": [
                {"address_id": f"A{i}", "source_address_id": f"ADDR-{i}", "parcel_id": f"P{i}"}
                for i in range(420)
            ],
        }
        assets = {"access_points": [{"candidate_access_point_id": "AP"}], "access_connectors": [
            {"candidate_connector_id": row["source_connector_candidate_id"]}
            for row in self.corridors["route_corridors"]
        ]}
        engineering = build_fictional_bridge_assessments(self.corridors)
        with self.assertRaisesRegex(ValueError, "exceptions must be resolved"):
            build_canonical_geography_register(
                identity, assets, engineering,
                {"unresolved_exception_count": 1, "all_source_addresses_preserved": True, "records": []},
            )


if __name__ == "__main__":
    unittest.main()
