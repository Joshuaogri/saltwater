import hashlib
import json
import unittest
from pathlib import Path

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.parcel_dossier_geometry_audit import audit_parcel_dossiers
from runtime.road_corridor_audit import build_road_corridor_audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())


def _rehash_manifest(data):
    body = dict(data)
    body.pop("manifest_sha256", None)
    return hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()


class ParcelDossierGeometryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = build_candidates(SOURCE)
        cls.dossiers = build_parcel_dossiers(SOURCE, cls.candidates)

    def test_complete_parcel_dossier_geometry_passes(self):
        report = audit_parcel_dossiers(SOURCE, self.candidates, self.dossiers)
        self.assertEqual(report["failed_checks"], [])
        self.assertEqual(report["passed_checks"], 10)
        self.assertEqual(report["counts"]["candidate_parcels"], 420)
        self.assertEqual(report["counts"]["frontage_candidates"], 1374)
        self.assertEqual(report["counts"]["access_location_candidates"], 1374)
        self.assertEqual(report["measurements"]["parcel_interior_overlap_area_m2"], 0)
        self.assertFalse(report["operational_seed_eligible"])

    def test_frontage_cannot_reference_a_different_road(self):
        bad = json.loads(json.dumps(self.dossiers))
        bad["parcels"][0]["frontages"][0]["road_id"] = "SW-RD-MISSING"
        report = audit_parcel_dossiers(SOURCE, self.candidates, bad)
        self.assertIn("frontage_candidates_match_complete_road_edge_geometry", report["failed_checks"])

    def test_frontage_candidate_point_must_lie_on_actual_shared_boundary(self):
        bad = json.loads(json.dumps(self.dossiers))
        bad["parcels"][0]["frontages"][0]["candidate_point_x_m"] += 50
        report = audit_parcel_dossiers(SOURCE, self.candidates, bad)
        self.assertIn("frontage_candidates_match_complete_road_edge_geometry", report["failed_checks"])

    def test_access_candidate_must_match_frontage_point(self):
        bad = json.loads(json.dumps(self.dossiers))
        bad["parcels"][0]["access_candidates"][0]["candidate_x_m"] += 20
        report = audit_parcel_dossiers(SOURCE, self.candidates, bad)
        self.assertIn("access_candidates_match_frontage_points_and_remain_unreviewed", report["failed_checks"])

    def test_water_adjacency_must_match_source_geometry(self):
        bad = json.loads(json.dumps(self.dossiers))
        bad["parcels"][0]["water_adjacencies"].append({
            "water_feature_id": "SW-WTR-999", "contact_length_m": 1
        })
        report = audit_parcel_dossiers(SOURCE, self.candidates, bad)
        self.assertIn("water_adjacencies_match_source_water_geometry", report["failed_checks"])

    def test_adjacency_register_must_be_complete(self):
        bad = json.loads(json.dumps(self.dossiers))
        bad["adjacency"].pop()
        report = audit_parcel_dossiers(SOURCE, self.candidates, bad)
        self.assertIn("parcel_adjacency_register_is_complete_and_measured", report["failed_checks"])

    def test_parcel_cannot_intrude_into_road_reserve_or_water(self):
        bad = json.loads(json.dumps(self.candidates))
        corridors = build_road_corridor_audit(SOURCE)
        reserve_ring = corridors["segments"][0]["reserve_polygon"][0]
        bad["parcels"][0]["geometry"] = [reserve_ring]
        bad["manifest_sha256"] = _rehash_manifest(bad)
        dossiers = json.loads(json.dumps(self.dossiers))
        dossiers["candidate_manifest_sha256"] = bad["manifest_sha256"]
        report = audit_parcel_dossiers(SOURCE, bad, dossiers)
        self.assertIn("parcels_exclude_road_reserve_and_mapped_water", report["failed_checks"])

    def test_no_canonical_address_or_operational_access_is_created(self):
        report = audit_parcel_dossiers(SOURCE, self.candidates, self.dossiers)
        self.assertEqual(report["canonical_addresses_created"], 0)
        self.assertEqual(report["operational_access_points_created"], 0)
        self.assertFalse(report["database_write_performed"])


if __name__ == "__main__":
    unittest.main()
