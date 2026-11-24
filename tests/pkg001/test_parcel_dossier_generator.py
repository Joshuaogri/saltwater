import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


class ParcelDossierGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidates = build_candidates(SOURCE)
        cls.result = build_parcel_dossiers(SOURCE, candidates)

    def test_dossier_count_and_geometry_measurements(self):
        summary = self.result["summary"]
        self.assertEqual(summary["parcel_dossier_count"], 420)
        self.assertEqual(summary["valid_geometry_count"], 420)
        for row in self.result["parcels"]:
            dossier = row["dossier"]
            self.assertGreater(dossier["area_m2"], 0)
            self.assertGreater(dossier["perimeter_m"], 0)
            self.assertGreater(dossier["compactness_index"], 0)
            self.assertLessEqual(dossier["compactness_index"], 1.000001)
            self.assertGreaterEqual(dossier["exterior_vertex_count"], 3)
            self.assertGreaterEqual(dossier["interior_ring_count"], 0)
            self.assertEqual(dossier["measurement_basis"], "DERIVED_FROM_GENERATED_POLYGON_GEOMETRY")

    def test_frontage_and_access_candidates_are_explicit_and_non_operational(self):
        summary = self.result["summary"]
        self.assertEqual(summary["frontage_review_required_count"], 418)
        self.assertEqual(summary["no_road_edge_contact_count"], 2)
        self.assertGreaterEqual(summary["frontage_candidate_count"], 418)
        self.assertEqual(summary["access_location_candidate_count"], summary["frontage_candidate_count"])
        self.assertEqual(summary["operational_access_points_created"], 0)
        for row in self.result["parcels"]:
            for access in row["access_candidates"]:
                self.assertEqual(access["review_status"], "UNREVIEWED_GEOMETRIC_CANDIDATE")
                self.assertEqual(access["candidate_type"], "unclassified_access_location")

    def test_adjacency_pairs_are_unique_and_canonical(self):
        pairs = [(r["left_candidate_parcel_id"], r["right_candidate_parcel_id"]) for r in self.result["adjacency"]]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertTrue(all(a < b for a, b in pairs))
        self.assertTrue(all(r["shared_boundary_length_m"] >= 0 for r in self.result["adjacency"]))
        self.assertGreater(self.result["summary"]["adjacency_relationship_count"], 0)

    def test_frontage_and_water_contacts_are_not_inferred_as_addresses(self):
        self.assertEqual(self.result["summary"]["canonical_addresses_created"], 0)
        self.assertFalse(self.result["operational_approval"])
        self.assertTrue(all(
            row["dossier"]["frontage_review_status"] in
            ("REVIEW_REQUIRED", "NO_ROAD_EDGE_CONTACT_REVIEW_REQUIRED")
            for row in self.result["parcels"]
        ))

    def test_dossier_manifest_is_deterministic(self):
        second = build_parcel_dossiers(SOURCE, build_candidates(SOURCE))
        self.assertEqual(self.result["manifest_sha256"], second["manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
