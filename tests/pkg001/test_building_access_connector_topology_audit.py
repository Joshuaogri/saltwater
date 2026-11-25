import copy
import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.building_access_connector_topology_audit import audit_connector_topology

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class BuildingAccessConnectorTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = build_candidates(SOURCE)
        cls.dossiers = build_parcel_dossiers(SOURCE, cls.candidates)
        cls.inventory = build_asset_inventory(SOURCE, cls.candidates, cls.dossiers)
        cls.report = audit_connector_topology(
            SOURCE, cls.candidates, cls.dossiers, cls.inventory
        )

    def test_every_connector_is_topologically_accounted_for(self):
        self.assertEqual(self.report["counts"]["connector_candidates"], 768)
        self.assertEqual(self.report["counts"]["frontage_connector_candidates"], 764)
        self.assertEqual(self.report["counts"]["road_reserve_proximity_connector_candidates"], 4)
        self.assertEqual(self.report["counts"]["unlinked_connector_candidates"], 0)

    def test_all_independent_topology_checks_pass(self):
        self.assertEqual(self.report["passed_checks"], 9, self.report["exceptions"])
        self.assertEqual(self.report["failed_checks"], [])

    def test_four_point_contacts_remain_distinct_from_frontage(self):
        proximity = [
            row for row in self.inventory["access_connectors"]
            if row["connector_type"] == "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE"
        ]
        self.assertEqual(len(proximity), 4)
        self.assertTrue(all(row["frontage_candidate_id"] is None
                            and row["road_connection_candidate_id"]
                            and row["contact_type"] == "POINT_CONTACT_ONLY"
                            for row in proximity))

    def test_operational_facts_are_never_created(self):
        self.assertEqual(self.report["operational_access_points_created"], 0)
        self.assertEqual(self.report["canonical_addresses_created"], 0)
        self.assertFalse(self.report["operational_seed_eligible"])
        self.assertFalse(self.report["database_write_performed"])

    def test_operational_manifests_are_rejected(self):
        bad = copy.deepcopy(self.inventory)
        bad["operational_approval"] = True
        with self.assertRaisesRegex(ValueError, "non-operational"):
            audit_connector_topology(SOURCE, self.candidates, self.dossiers, bad)

    def test_dossier_lineage_mismatch_is_rejected(self):
        bad = copy.deepcopy(self.inventory)
        bad["parcel_dossier_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "lineage mismatch"):
            audit_connector_topology(SOURCE, self.candidates, self.dossiers, bad)


if __name__ == "__main__":
    unittest.main()
