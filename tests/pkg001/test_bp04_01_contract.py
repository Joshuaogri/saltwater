import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "db/proposals/0011_bp04_property_premises_foundation.sql"
ACCEPTANCE = ROOT / "tests/pkg001/bp04_01_acceptance.sql"
WORKFLOW = ROOT / ".github/workflows/sw-db-001-disposable.yml"


class BP0401ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = MIGRATION.read_text(encoding="utf-8")
        cls.acceptance = ACCEPTANCE.read_text(encoding="utf-8")
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_all_five_physical_identity_tables_exist(self):
        for table in ("property_asset", "building", "premises", "unit_space", "access_point"):
            with self.subTest(table=table):
                self.assertIn(f"CREATE TABLE sw_property.{table}", self.sql)

    def test_property_location_is_explicit_and_typed(self):
        self.assertIn("location_status IN ('resolved','unresolved')", self.sql)
        self.assertIn("BP-02 parcel (kind 6)", self.sql)
        self.assertIn("BP-02 address (kind 11)", self.sql)

    def test_global_naming_adapters_are_registered(self):
        for kind in ("PROPERTY", "BUILDING", "PREMISES", "UNIT", "ACCESS_POINT"):
            self.assertIn(f"'{kind}'", self.sql)
        self.assertIn("CREATE OR REPLACE FUNCTION sw_names.guard_reservation()", self.sql)
        self.assertIn("CREATE OR REPLACE FUNCTION sw_names.reserve_name(", self.sql)

    def test_identity_and_relationship_history_are_append_only(self):
        self.assertIn("CREATE TABLE sw_property.entity_history", self.sql)
        self.assertIn("CREATE TABLE sw_property.relationship_history", self.sql)
        self.assertIn("BP-04 identities cannot be deleted", self.sql)
        self.assertIn("relationship can be ended exactly once", self.sql)

    def test_acceptance_covers_required_boundaries(self):
        for phrase in (
            "wrong-kind parcel reference",
            "wrong-kind address reference",
            "business/property global name collision",
            "invalid building-premises parent link",
            "failed name reservation left a partial property identity",
            "BP04_01_ACCEPTANCE_PASS",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.acceptance)

    def test_disposable_workflow_applies_and_tests_proposal(self):
        self.assertIn("db/proposals/0011_bp04_property_premises_foundation.sql", self.workflow)
        self.assertIn("tests/pkg001/bp04_01_geography_fixture.sql", self.workflow)
        self.assertIn("tests/pkg001/bp04_01_acceptance.sql", self.workflow)


if __name__ == "__main__":
    unittest.main()
