from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class BP0403StageBContractTests(unittest.TestCase):
    def test_bp02_owns_parcel_and_address_identities(self):
        sql = (ROOT / "db/proposals/0013_bp02_parcel_address_candidate.sql").read_text()
        self.assertIn("CREATE TABLE sw_geo.parcel_profile", sql)
        self.assertIn("CREATE TABLE sw_geo.address_profile", sql)
        self.assertIn("REFERENCES sw_geo.entity(spatial_id)", sql)
        self.assertIn("geometry_payload", sql)
        self.assertIn("geometry_sha256", sql)
        self.assertNotIn("CREATE SCHEMA sw_property", sql)

    def test_parcel_address_quality_and_lineage(self):
        sql = (ROOT / "db/proposals/0013_bp02_parcel_address_candidate.sql").read_text()
        for value in ("generated_design_value","derived_geometry","candidate_unreviewed",
                      "direct_public_frontage","shared_private_approach","campus_access",
                      "waterfront_access","no_conventional_frontage","unresolved"):
            self.assertIn(value, sql)
        for table in ("parcel_lineage","address_alias"):
            self.assertIn(f"CREATE TABLE sw_geo.{table}", sql)
        self.assertIn("address_active_road_locator_uq", sql)
        self.assertIn("address_active_parcel_locator_uq", sql)

    def test_append_only_kind_guards_and_no_approval(self):
        sql = (ROOT / "db/proposals/0013_bp02_parcel_address_candidate.sql").read_text()
        self.assertIn("guard_parcel_profile_kind", sql)
        self.assertIn("guard_address_profile_kind", sql)
        self.assertIn("reject_candidate_record_mutation", sql)
        self.assertIn("CHECK (geometry_quality <> 'approved')", sql)
        self.assertIn("Disposable PostgreSQL 16 candidate only", sql)
        self.assertNotIn("neon.tech", sql.lower())
        self.assertNotIn("postgresql://", sql.lower())

    def test_acceptance_is_synthetic_and_rolls_back(self):
        sql = (ROOT / "tests/pkg001/bp04_03_stage_b_acceptance.sql").read_text()
        self.assertIn("BP04-03", sql)
        self.assertIn("ROLLBACK;", sql)
        self.assertIn("duplicate active road locator was accepted", sql)
        self.assertIn("non-road spatial reference was accepted", sql)

if __name__ == "__main__":
    unittest.main()
