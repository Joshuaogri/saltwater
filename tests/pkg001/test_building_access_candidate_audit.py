import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.building_access_candidate_audit import audit_building_access_candidates

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class BuildingAccessCandidateAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = build_candidates(SOURCE)
        cls.dossiers = build_parcel_dossiers(SOURCE, cls.candidates)
        cls.assets = build_asset_inventory(SOURCE, cls.candidates, cls.dossiers)
        cls.report = audit_building_access_candidates(cls.candidates, cls.dossiers, cls.assets)

    def test_building_and_access_candidate_hierarchy_counts(self):
        self.assertEqual(self.report["counts"]["property_site_candidates"], 420)
        self.assertEqual(self.report["counts"]["building_candidates"], 384)
        self.assertEqual(self.report["counts"]["building_boundary_access_candidates"], 768)

    def test_access_candidates_are_geometrically_valid(self):
        self.assertTrue(self.report["checks"]["building_access_points_are_on_building_boundaries_and_inside_property"])
        self.assertTrue(self.report["checks"]["building_footprints_remain_inside_their_parcel_property"])

    def test_frontage_links_resolve_to_same_parcel(self):
        self.assertTrue(self.report["checks"]["road_link_candidates_resolve_to_the_same_parcel_frontage"])

    def test_access_facts_are_not_fabricated(self):
        self.assertTrue(self.report["checks"]["access_facts_remain_unknown_or_not_assessed"])
        self.assertEqual(self.report["operational_access_points_created"], 0)
        self.assertEqual(self.report["canonical_addresses_created"], 0)

    def test_each_access_candidate_uses_nearest_frontage(self):
        self.assertTrue(
            self.report["checks"]["each_building_access_candidate_links_to_its_nearest_geometric_frontage"],
            self.report["exceptions"]["assigned_link_not_nearest"][:10],
        )

    def test_a_wrong_parcel_frontage_link_fails(self):
        bad = json.loads(json.dumps(self.assets))
        bad["access_points"][0]["road_link_candidate_id"] = "PAC-NOT-A-REAL-FRONTAGE"
        report = audit_building_access_candidates(self.candidates, self.dossiers, bad)
        self.assertFalse(report["checks"]["road_link_candidates_resolve_to_the_same_parcel_frontage"])

    def test_no_database_write_or_operational_seed(self):
        self.assertFalse(self.report["database_write_performed"])
        self.assertFalse(self.report["operational_seed_eligible"])


if __name__ == "__main__":
    unittest.main()
