import unittest

from runtime.bp02_address_frontage_exception_resolution import resolve_address_frontage_exceptions


class BP02AddressFrontageExceptionResolutionTests(unittest.TestCase):
    def setUp(self):
        self.geo = {
            "roads": [
                {"id": "R-SRC", "name": "Original Street", "class": "local_street"},
                {"id": "R-ALT", "name": "Alternative Avenue", "class": "local_street"},
                {"id": "R-BRIDGE", "name": "Harbour Bridge", "class": "bridge"},
                {"id": "R-LEFT", "name": "West Street", "class": "local_street"},
                {"id": "R-RIGHT", "name": "East Street", "class": "local_street"},
            ],
            "network": {"segments": [
                {"id": "BSEG", "road_id": "R-BRIDGE", "from_node_id": "N1", "to_node_id": "N2",
                 "access": "public", "modes": ["motor_vehicle", "emergency"]},
                {"id": "LSEG", "road_id": "R-LEFT", "from_node_id": "N1", "to_node_id": "N0",
                 "access": "public", "modes": ["motor_vehicle", "emergency"]},
                {"id": "RSEG", "road_id": "R-RIGHT", "from_node_id": "N2", "to_node_id": "N3",
                 "access": "public", "modes": ["motor_vehicle", "emergency"]},
            ]},
        }
        self.reconciliation = {"address_frontage_exceptions_building_access_crosscheck": [
            {
                "source_address_id": "A1", "property_id": "PROP-ALPHA", "source_candidate_parcel_id": "P1",
                "source_road_id": "R-SRC", "candidate_frontage_road_ids": ["R-ALT"],
                "building_access_road_candidate_status": "NO_BUILDING_ON_PROPERTY_SITE",
                "building_access_road_candidate_ids": [],
                "building_access_road_candidate_details": {},
                "status": "ADDRESS_ROAD_DIFFERS_FROM_PARCEL_FRONTAGE_CANDIDATE",
            },
            {
                "source_address_id": "A2", "property_id": "PROPERTY-EXPLICIT-42", "source_candidate_parcel_id": "P2",
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

    def _connector_report(self):
        return {"connector_candidates": [
            {
                "property_id": "PROPERTY-EXPLICIT-42",
                "candidate_access_point_id": "AP-P2-A",
                "candidate_road_connection_id": "PAC-P2-A-BSEG",
                "road_connection_type": "road_reserve_proximity_connection",
                "road_connection_contact_type": "POINT_CONTACT_ONLY",
                "geometry_status": "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED",
                "property_contains_connector": True,
                "crosses_origin_building": False,
                "crosses_other_building": False,
                "crosses_water": False,
            },
            {
                "property_id": "PROPERTY-EXPLICIT-42",
                "candidate_access_point_id": "AP-P2-B",
                "candidate_road_connection_id": "PAC-P2-B-BSEG",
                "road_connection_type": "road_reserve_proximity_connection",
                "road_connection_contact_type": "POINT_CONTACT_ONLY",
                "geometry_status": "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED",
                "property_contains_connector": True,
                "crosses_origin_building": False,
                "crosses_other_building": False,
                "crosses_water": False,
            },
        ]}

    def test_unique_frontage_resolves_road_association_without_rewriting_source(self):
        result = resolve_address_frontage_exceptions(self.reconciliation, self.geo)
        row = result["records"][0]
        self.assertEqual(row["proposed_frontage_road_id"], "R-ALT")
        self.assertEqual(row["resolved_access_road_id"], "R-ALT")
        self.assertEqual(row["geometry_disposition"], "UNIQUE_PARCEL_FRONTAGE_ROAD_ASSOCIATION_RESOLVED")
        self.assertTrue(row["address_road_association_resolved"])
        self.assertEqual(row["source_road_id"], "R-SRC")
        self.assertFalse(row["canonical_address_corrected"])
        self.assertFalse(row["operational_access_approved"])

    def test_bridge_connector_and_connected_public_streets_resolve_road_association_only(self):
        result = resolve_address_frontage_exceptions(
            self.reconciliation, self.geo, self._connector_report()
        )
        row = result["records"][1]
        self.assertEqual(
            row["geometry_disposition"],
            "BRIDGE_ACCESS_CONNECTOR_CANDIDATE_TO_CONNECTED_PUBLIC_ROAD_NETWORK",
        )
        self.assertEqual(row["resolved_access_road_id"], "R-BRIDGE")
        self.assertTrue(row["address_road_association_resolved"])
        self.assertEqual(row["verified_geometric_connector_candidate_count"], 2)
        self.assertEqual(
            row["verified_geometric_connector_candidates"],
            [
                {"candidate_access_point_id": "AP-P2-A", "road_access_candidate_id": "PAC-P2-A-BSEG"},
                {"candidate_access_point_id": "AP-P2-B", "road_access_candidate_id": "PAC-P2-B-BSEG"},
            ],
        )
        self.assertFalse(row["operational_access_approved"])

    def test_bridge_resolution_uses_explicit_property_link_not_address_id_pattern(self):
        result = resolve_address_frontage_exceptions(
            self.reconciliation, self.geo, self._connector_report()
        )
        self.assertEqual(
            result["records"][1]["geometry_disposition"],
            "BRIDGE_ACCESS_CONNECTOR_CANDIDATE_TO_CONNECTED_PUBLIC_ROAD_NETWORK",
        )
        self.assertEqual(result["records"][1]["verified_geometric_connector_candidate_count"], 2)
        report = self._connector_report()
        report["connector_candidates"].append(dict(
            report["connector_candidates"][0], property_id="UNRELATED-PROPERTY"
        ))
        filtered = resolve_address_frontage_exceptions(
            self.reconciliation, self.geo, report
        )
        self.assertEqual(
            filtered["records"][1]["verified_geometric_connector_candidate_count"], 2
        )
        broken = {"address_frontage_exceptions_building_access_crosscheck": [
            dict(self.reconciliation["address_frontage_exceptions_building_access_crosscheck"][1],
                 property_id=None)
        ]}
        result = resolve_address_frontage_exceptions(broken, self.geo, self._connector_report())
        self.assertFalse(result["records"][0]["address_road_association_resolved"])

    def test_duplicate_connector_identity_fails_closed(self):
        report = self._connector_report()
        report["connector_candidates"][1]["candidate_road_connection_id"] = report["connector_candidates"][0]["candidate_road_connection_id"]
        result = resolve_address_frontage_exceptions(self.reconciliation, self.geo, report)
        row = result["records"][1]
        self.assertFalse(row["address_road_association_resolved"])
        self.assertEqual(row["verified_geometric_connector_candidate_count"], 0)

    def test_bridge_point_contact_without_connector_evidence_remains_unresolved(self):
        result = resolve_address_frontage_exceptions(self.reconciliation, self.geo)
        row = result["records"][1]
        self.assertEqual(row["geometry_disposition"], "BRIDGE_POINT_CONTACT_ONLY_NOT_STREET_FRONTAGE")
        self.assertFalse(row["address_road_association_resolved"])

    def test_bridge_requires_public_motor_vehicle_emergency_connections_at_both_ends(self):
        broken_geo = dict(self.geo)
        broken_geo["network"] = {"segments": self.geo["network"]["segments"][:2]}
        result = resolve_address_frontage_exceptions(
            self.reconciliation, broken_geo, self._connector_report()
        )
        self.assertFalse(result["records"][1]["address_road_association_resolved"])

    def test_connector_crossing_water_fails_closed(self):
        report = self._connector_report()
        report["connector_candidates"][0]["crosses_water"] = True
        result = resolve_address_frontage_exceptions(self.reconciliation, self.geo, report)
        self.assertFalse(result["records"][1]["address_road_association_resolved"])

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
