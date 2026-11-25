import copy
import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.building_access_route_corridor_audit import build_route_corridor_candidates

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class BuildingAccessRouteCorridorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = build_candidates(SOURCE)
        cls.dossiers = build_parcel_dossiers(SOURCE, cls.candidates)
        cls.inventory = build_asset_inventory(SOURCE, cls.candidates, cls.dossiers)
        cls.report = build_route_corridor_candidates(
            SOURCE, cls.candidates, cls.dossiers, cls.inventory
        )

    def test_all_connectors_have_route_corridor_centreline_candidates(self):
        summary = self.report["summary"]
        self.assertEqual(summary["connector_candidate_count"], 2948)
        self.assertEqual(summary["route_corridor_centreline_candidate_count"], 2948)
        self.assertEqual(summary["frontage_centreline_candidate_count"], 2944)
        self.assertEqual(summary["point_contact_or_proximity_centreline_candidate_count"], 4)
        self.assertEqual(summary["unresolved_connector_count"], 0)

    def test_geometric_obstacle_and_containment_checks_pass(self):
        self.assertEqual(self.report["passed_checks"], 7, self.report["exceptions"])
        self.assertEqual(self.report["failed_checks"], [])
        summary = self.report["summary"]
        self.assertEqual(summary["mapped_building_intersection_count"], 0)
        self.assertEqual(summary["mapped_water_intersection_count"], 0)
        self.assertEqual(summary["origin_building_interior_crossing_count"], 0)
        self.assertEqual(summary["road_reserve_overlap_count"], 0)

    def test_width_gradient_and_surface_remain_unknown(self):
        for row in self.report["route_corridors"]:
            self.assertIsNone(row["available_width_m"])
            self.assertIsNone(row["corridor_width_m"])
            self.assertEqual(row["width_assessment_state"], "NOT_ASSESSED_NO_WIDTH_OR_CLEARANCE_SOURCE")
            self.assertEqual(row["gradient_state"], "not_assessed_no_elevation_source")
            self.assertEqual(row["surface_state"], "unknown")
            self.assertEqual(row["route_suitability"], "unknown")
        self.assertEqual(self.report["summary"]["width_assessed_count"], 0)
        self.assertEqual(self.report["summary"]["gradient_assessed_count"], 0)
        self.assertEqual(self.report["summary"]["surface_assessed_count"], 0)
        self.assertEqual(self.report["summary"]["route_suitability_confirmed_count"], 0)

    def test_four_point_contacts_remain_non_frontage(self):
        rows = [r for r in self.report["route_corridors"]
                if r["connector_type"] == "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE"]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r["frontage_candidate_id"] is None
                            and r["road_connection_candidate_id"]
                            and r["contact_type"] == "POINT_CONTACT_ONLY"
                            for r in rows))

    def test_operational_manifests_are_rejected(self):
        bad = copy.deepcopy(self.inventory)
        bad["operational_approval"] = True
        with self.assertRaisesRegex(ValueError, "non-operational"):
            build_route_corridor_candidates(SOURCE, self.candidates, self.dossiers, bad)

    def test_source_manifest_mismatch_is_rejected(self):
        bad = copy.deepcopy(self.inventory)
        bad["parcel_dossier_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Asset/dossier manifest lineage mismatch"):
            build_route_corridor_candidates(SOURCE, self.candidates, self.dossiers, bad)


if __name__ == "__main__":
    unittest.main()
