"""Contract tests for the isolated BP02 migration stream."""
import hashlib
import unittest
from unittest.mock import MagicMock
from scripts.migrate_bp02 import MIGRATION, MIGRATIONS, migration_checksum, migration_plan, apply_bp02


class BP02DomainMigrationTests(unittest.TestCase):
    def test_migrations_are_ordered_and_independent_of_global_bp04(self):
        plan = migration_plan()
        self.assertEqual([row["version"] for row in plan], [1, 2])
        self.assertEqual(plan[0]["migration_name"], "0001_source_archive")
        self.assertEqual(plan[1]["migration_name"], "0002_operational_geography")
        for path in MIGRATIONS:
            sql = path.read_text(encoding="utf-8").lower()
            self.assertIn("sw_geo.bp02_schema_migration", (MIGRATIONS[0].read_text(encoding="utf-8")).lower())
            self.assertNotIn("sw_ops.schema_migration", sql)
            self.assertNotIn("sw_property", sql)
            self.assertNotIn("sw_people", sql)

    def test_operational_schema_is_compact_and_preserves_gameplay_boundary(self):
        sql = MIGRATIONS[1].read_text(encoding="utf-8").lower()
        for table in (
            "bp02_district", "bp02_neighbourhood", "bp02_feature", "bp02_road",
            "bp02_node", "bp02_segment", "bp02_route", "bp02_route_node",
            "bp02_route_segment", "bp02_parcel", "bp02_address",
            "bp02_access_point", "bp02_bridge_connector",
        ):
            self.assertIn(f"sw_geo.{table}", sql)
        self.assertIn("production_seed_approved boolean not null default false", sql)
        self.assertIn("operational_status='active_in_game'", sql)
        self.assertNotIn("postgis", sql)

    def test_checksum_is_sha256_of_exact_migration_bytes(self):
        self.assertEqual(migration_checksum(), hashlib.sha256(MIGRATION.read_bytes()).hexdigest())

    def test_database_name_mismatch_fails_before_any_ddl(self):
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = ("other_db",)
        with self.assertRaises(ValueError):
            apply_bp02(conn, "neondb")
        self.assertEqual(conn.execute.call_count, 1)

    def test_production_requires_explicit_guard(self):
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = ("neondb",)
        with self.assertRaises(PermissionError):
            apply_bp02(conn, "neondb", False)
        self.assertEqual(conn.execute.call_count, 1)


if __name__ == "__main__":
    unittest.main()
