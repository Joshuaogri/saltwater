from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class BP0402ContractTests(unittest.TestCase):
    def test_all_five_typed_profiles_and_history(self):
        sql = (ROOT / "db/proposals/0012_bp04_physical_asset_detail_profiles.sql").read_text()
        for table in ("property_profile", "building_profile", "premises_profile", "unit_profile", "access_point_profile"):
            self.assertIn(f"CREATE TABLE sw_property.{table}", sql)
            self.assertIn("effective_from_tick", sql)
            self.assertIn("recorded_at", sql)
        self.assertIn("UNIQUE(property_id,effective_from_tick)", sql)
        self.assertIn("UNIQUE(building_id,effective_from_tick)", sql)
        self.assertIn("UNIQUE(premises_id,effective_from_tick)", sql)
        self.assertIn("UNIQUE(unit_id,effective_from_tick)", sql)
        self.assertIn("UNIQUE(access_point_id,effective_from_tick)", sql)

    def test_structured_child_records_and_provenance(self):
        sql = (ROOT / "db/proposals/0012_bp04_physical_asset_detail_profiles.sql").read_text()
        for table in ("physical_measurement", "building_level", "building_component", "premises_room",
                      "utility_system", "physical_feature", "condition_assessment", "physical_defect",
                      "asset_assertion"):
            self.assertIn(f"CREATE TABLE sw_property.{table}", sql)
        self.assertIn("source_ref text NOT NULL", sql)
        self.assertIn("actor_ref text NOT NULL", sql)
        self.assertIn("confidence_code", sql)
        self.assertIn("knowledge_state", sql)
        self.assertIn("not_assessed", sql)
        self.assertIn("not_applicable", sql)
        self.assertIn("not_present", sql)

    def test_append_only_and_disposable_only(self):
        sql = (ROOT / "db/proposals/0012_bp04_physical_asset_detail_profiles.sql").read_text()
        self.assertIn("CREATE TRIGGER", sql)
        self.assertIn("reject_profile_mutation", sql)
        self.assertIn("Disposable PostgreSQL 16", sql)
        self.assertNotIn("neon.tech", sql.lower())
        self.assertNotIn("postgresql://", sql.lower())

    def test_acceptance_covers_all_five_entities(self):
        sql = (ROOT / "tests/pkg001/bp04_02_profile_acceptance.sql").read_text()
        for entity in ("'PROPERTY'", "'BUILDING'", "'PREMISES'", "'UNIT'", "'ACCESS_POINT'"):
            self.assertIn(entity, sql)
        self.assertIn("BP04_02_ACCEPTANCE_PASS", sql)
        self.assertIn("ROLLBACK;", sql)

if __name__ == "__main__":
    unittest.main()
