import unittest

from runtime.bp02_bridge_connector_engineering_register import (
    ENGINEERING_EVIDENCE_FIELDS,
    build_bridge_connector_engineering_register,
)


class BP02BridgeConnectorEngineeringRegisterTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "source_connector_manifest_sha256": "source-digest",
            "manifest_sha256": "corridor-digest",
            "route_corridors": [
                {
                    "source_connector_candidate_id": f"PAC-{road}-{suffix}",
                    "candidate_access_point_id": f"AP-{road}-{suffix}",
                    "candidate_building_id": f"B-{road}-{suffix}",
                    "candidate_property_id": f"P-{road}",
                    "source_candidate_parcel_id": f"PARCEL-{road}",
                    "candidate_route_corridor_id": f"RC-{road}-{suffix}",
                    "road_id": road,
                    "centreline_length_m": 12.5,
                    "centreline_status": "UNREVIEWED_GEOMETRIC_CANDIDATE",
                }
                for road in ("SWR-B1", "SWR-B2")
                for suffix in ("A", "B")
            ],
        }

    def test_creates_four_site_specific_holds_without_inventing_engineering_values(self):
        result = build_bridge_connector_engineering_register(self.report)
        self.assertEqual(result["engineering_work_item_count"], 4)
        self.assertEqual(result["assessed_count"], 0)
        self.assertEqual(result["operationally_approved_count"], 0)
        self.assertTrue(result["all_candidate_identities_complete"])
        self.assertTrue(result["all_required_evidence_explicitly_unassessed"])
        self.assertTrue(result["all_operational_access_holds_preserved"])
        for row in result["records"]:
            self.assertEqual(set(row["evidence"]), set(ENGINEERING_EVIDENCE_FIELDS))
            self.assertTrue(all(value is None for value in row["evidence"].values()))
            self.assertFalse(row["operational_access_approved"])
            self.assertEqual(row["operational_access_status"], "HOLD_NOT_APPROVED")

    def test_missing_bridge_connector_fails_closed(self):
        self.report["route_corridors"].pop()
        with self.assertRaisesRegex(ValueError, "expected 2 connector candidates"):
            build_bridge_connector_engineering_register(self.report)

    def test_missing_identity_lineage_fails_closed(self):
        self.report["route_corridors"][0]["candidate_property_id"] = None
        with self.assertRaisesRegex(ValueError, "lacks identity lineage"):
            build_bridge_connector_engineering_register(self.report)


if __name__ == "__main__":
    unittest.main()
