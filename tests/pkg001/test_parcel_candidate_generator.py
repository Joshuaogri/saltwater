import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))


class ParcelCandidateGeneratorTests(unittest.TestCase):
    def test_deterministic_manifest_and_candidate_ids(self):
        first = build_candidates(SOURCE)
        second = build_candidates(SOURCE)
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])
        self.assertEqual(
            [p["candidate_parcel_id"] for p in first["parcels"]],
            [p["candidate_parcel_id"] for p in second["parcels"]],
        )

    def test_neighbourhood_coverage_and_candidate_geometry(self):
        result = build_candidates(SOURCE)
        self.assertEqual(len(result["coverage_by_neighbourhood"]), 24)
        self.assertTrue(all(x["candidate_parcel_count"] > 0 for x in result["coverage_by_neighbourhood"]))
        ids = [p["candidate_parcel_id"] for p in result["parcels"]]
        self.assertEqual(len(ids), len(set(ids)))
        for parcel in result["parcels"]:
            ring = parcel["geometry"][0]
            self.assertEqual(ring[0], ring[-1])
            self.assertEqual(parcel["area_m2"], 470 * 470)
            self.assertEqual(parcel["geometry_quality"], "candidate_unreviewed")
            self.assertIsNone(parcel["candidate_spatial_id"])
            self.assertIsNone(parcel["canonical_address_id"])

    def test_water_conflicts_are_excluded_not_filled(self):
        result = build_candidates(SOURCE)
        self.assertGreater(len(result["excluded_cells"]), 0)
        self.assertTrue(all(x["status"] == "EXCLUDED_UNRESOLVED" for x in result["excluded_cells"]))
        self.assertTrue(all(p["geometry_quality"] == "candidate_unreviewed" for p in result["parcels"]))

    def test_frontage_is_never_inferred_without_matching_road_edge(self):
        result = build_candidates(SOURCE)
        for parcel in result["parcels"]:
            if parcel["frontage_status"] == "SUPPORTED_CANDIDATE":
                self.assertGreater(len(parcel["road_frontage_edges"]), 0)
            else:
                self.assertEqual(parcel["road_frontage_edges"], [])

    def test_no_operational_ids_or_addresses_are_created(self):
        result = build_candidates(SOURCE)
        self.assertFalse(result["operational_approval"])
        self.assertEqual(result["generation"]["spatial_ids_assigned"], 0)
        self.assertEqual(result["generation"]["canonical_addresses_created"], 0)
        self.assertEqual(result["address_generation"]["records_created"], 0)
        self.assertEqual(result["generation"]["unresolved_source_spatial_mappings"], 100)


if __name__ == "__main__":
    unittest.main()
