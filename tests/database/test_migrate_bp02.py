import unittest
from unittest.mock import patch

from scripts.migrate_bp02 import verify_bp02


class _Result:
    def __init__(self, one=None, many=None):
        self._one = one
        self._many = many

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._many


class _ReadOnlyConnection:
    def __init__(self, rows, ledger_exists=True):
        self.rows = rows
        self.ledger_exists = ledger_exists
        self.statements = []

    def execute(self, sql):
        self.statements.append(sql.strip())
        if "current_database()" in sql:
            return _Result(one=("saltwater_test",))
        if "to_regclass('sw_geo.bp02_schema_migration')" in sql:
            return _Result(one=(self.ledger_exists,))
        if "FROM sw_geo.bp02_schema_migration" in sql:
            return _Result(many=self.rows)
        raise AssertionError(f"Unexpected query in read-only verifier: {sql}")


PLAN = [
    {"version": 1, "migration_name": "0001_source_archive", "checksum_sha256": "a" * 64},
    {"version": 2, "migration_name": "0002_operational_geography", "checksum_sha256": "b" * 64},
]


class BP02ReadOnlyLedgerVerificationTests(unittest.TestCase):
    def test_exact_ledger_verifies_without_writes(self):
        conn = _ReadOnlyConnection([
            (1, PLAN[0]["migration_name"], PLAN[0]["checksum_sha256"]),
            (2, PLAN[1]["migration_name"], PLAN[1]["checksum_sha256"]),
        ])
        with patch("scripts.migrate_bp02.migration_plan", return_value=PLAN):
            result = verify_bp02(conn, "saltwater_test")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["current_version"], 2)
        self.assertEqual(result["pending_migrations"], [])
        self.assertTrue(all(sql.upper().startswith("SELECT") for sql in conn.statements))

    def test_pending_source_migration_is_reported_without_apply(self):
        conn = _ReadOnlyConnection([
            (1, PLAN[0]["migration_name"], PLAN[0]["checksum_sha256"]),
        ])
        with patch("scripts.migrate_bp02.migration_plan", return_value=PLAN):
            result = verify_bp02(conn, "saltwater_test")
        self.assertEqual(result["pending_migrations"], [PLAN[1]["migration_name"]])
        self.assertTrue(all(sql.upper().startswith("SELECT") for sql in conn.statements))

    def test_checksum_mismatch_fails_closed(self):
        conn = _ReadOnlyConnection([
            (1, PLAN[0]["migration_name"], "f" * 64),
        ])
        with patch("scripts.migrate_bp02.migration_plan", return_value=PLAN):
            with self.assertRaisesRegex(RuntimeError, "ledger mismatch"):
                verify_bp02(conn, "saltwater_test")

    def test_unknown_future_version_fails_closed(self):
        conn = _ReadOnlyConnection([
            (1, PLAN[0]["migration_name"], PLAN[0]["checksum_sha256"]),
            (2, PLAN[1]["migration_name"], PLAN[1]["checksum_sha256"]),
            (3, "unknown", "c" * 64),
        ])
        with patch("scripts.migrate_bp02.migration_plan", return_value=PLAN):
            with self.assertRaisesRegex(RuntimeError, "ahead of source"):
                verify_bp02(conn, "saltwater_test")

    def test_missing_independent_ledger_fails_closed(self):
        conn = _ReadOnlyConnection([], ledger_exists=False)
        with patch("scripts.migrate_bp02.migration_plan", return_value=PLAN):
            with self.assertRaisesRegex(RuntimeError, "ledger is absent"):
                verify_bp02(conn, "saltwater_test")

    def test_wrong_database_fails_closed(self):
        conn = _ReadOnlyConnection([])
        with patch("scripts.migrate_bp02.migration_plan", return_value=PLAN):
            with self.assertRaisesRegex(ValueError, "Database mismatch"):
                verify_bp02(conn, "another_database")


if __name__ == "__main__":
    unittest.main()
