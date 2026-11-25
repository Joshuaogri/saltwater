import copy
import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.building_access_connector_audit import audit_direct_access_connectors

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class DirectAccessConnectorAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = build_candidates(SOURCE)
        cls.dossiers = build_parcel_dossiers(SOURCE, cls.candidates)
        cls.assets = build_asset_inventory(SOURCE, cls.candidates, cls.dossiers)
        cls.report = audit_direct_access_connectors(
            SOURCE, cls.candidates, cls.dossiers, cls.assets
        )

    def test_all_building_boundary_candidates_are_accounted_for(self):
        counts = self.report["counts"]
        self.assertEqual(counts["building_boundary_access_candidates"], 768)
        self.assertEqual(counts["direct_connector_candidates_tested"], 768)
        self.assertEqual(counts["unlinked_road_connection_candidate"], 0)
        self.assertEqual(counts["point_contact_road_reserve_candidates"], 4)
        self.assertEqual(counts["point_contact_only_road_reserve_connections"], 4)
        point_contacts = [
            row for row in self.report["connector_candidates"]
            if row["road_connection_contact_type"] == "POINT_CONTACT_ONLY"
        ]
        self.assertEqual(len(point_contacts), 4)
        self.assertTrue(all(
            row["road_connection_type"] == "road_reserve_proximity_connection"
            for row in point_contacts
        ))
        self.assertTrue(all(
            row["road_connection_contact_type"] != "FRONTAGE"
            for row in point_contacts
        ))

    def test_each_linked_connector_is_classified(self):
        counts = self.report["counts"]
        self.assertEqual(
            counts["direct_geometry_feasible_unreviewed"]
            + counts["direct_geometry_blocked_unreviewed"],
            counts["direct_connector_candidates_tested"],
        )

    def test_no_candidate_marked_feasible_crosses_a_building_or_water(self):
        self.assertTrue(
            self.report["checks"]["no_feasible_connector_crosses_its_origin_building_interior"],
            self.report["exceptions"]["crosses_origin_building"][:10],
        )
        self.assertTrue(
            self.report["checks"]["no_feasible_connector_crosses_another_building_interior"],
            self.report["exceptions"]["crosses_other_building"][:10],
        )
        self.assertTrue(
            self.report["checks"]["no_feasible_connector_crosses_mapped_water"],
            self.report["exceptions"]["crosses_water"][:10],
        )
        for row in self.report["connector_candidates"]:
            if row["geometry_status"] == "DIRECT_GEOMETRY_FEASIBLE_UNREVIEWED":
                self.assertTrue(row["property_contains_connector"])
                self.assertFalse(row["crosses_origin_building"])
                self.assertFalse(row["crosses_other_building"])
                self.assertFalse(row["crosses_water"])

    def test_connectors_never_become_operational_access(self):
        self.assertEqual(self.report["operational_access_points_created"], 0)
        self.assertEqual(self.report["canonical_addresses_created"], 0)
        self.assertFalse(self.report["operational_seed_eligible"])
        self.assertFalse(self.report["database_write_performed"])
        self.assertTrue(all(
            row["review_status"] == "UNREVIEWED_GEOMETRIC_LINE_ONLY"
            for row in self.report["connector_candidates"]
        ))

    def test_operational_asset_manifest_is_rejected(self):
        bad = copy.deepcopy(self.assets)
        bad["operational_approval"] = True
        with self.assertRaisesRegex(ValueError, "Operational asset"):
            audit_direct_access_connectors(SOURCE, self.candidates, self.dossiers, bad)

    def test_manifest_lineage_mismatch_is_rejected(self):
        bad = copy.deepcopy(self.assets)
        bad["parcel_dossier_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "lineage mismatch"):
            audit_direct_access_connectors(SOURCE, self.candidates, self.dossiers, bad)


if __name__ == "__main__":
    unittest.main()
