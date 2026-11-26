"""Contract tests for the isolated BP-02 migration stream."""
import hashlib
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from scripts.migrate_bp02 import MIGRATION, migration_checksum, apply_bp02

class BP02DomainMigrationTests(unittest.TestCase):
    def test_migration_is_independent_and_has_no_bp04_dependency(self):
        sql=MIGRATION.read_text(encoding="utf-8").lower()
        self.assertIn("sw_geo.bp02_schema_migration",sql)
        self.assertIn("sw_geo.source_archive",sql)
        self.assertNotIn("sw_ops.schema_migration",sql)
        self.assertNotIn("sw_property",sql)
        self.assertNotIn("sw_people",sql)

    def test_checksum_is_sha256_of_exact_migration_bytes(self):
        self.assertEqual(migration_checksum(),hashlib.sha256(MIGRATION.read_bytes()).hexdigest())

    def test_database_name_mismatch_fails_before_any_ddl(self):
        conn=MagicMock()
        conn.execute.return_value.fetchone.return_value=("other_db",)
        with self.assertRaises(ValueError):
            apply_bp02(conn,"neondb")
        self.assertEqual(conn.execute.call_count,1)

    def test_production_requires_explicit_guard(self):
        conn=MagicMock()
        conn.execute.return_value.fetchone.return_value=("neondb",)
        with self.assertRaises(PermissionError):
            apply_bp02(conn,"neondb",False)
        self.assertEqual(conn.execute.call_count,1)

if __name__=="__main__":
    unittest.main()
