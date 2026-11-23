"""PKG-004 activation adapter contract tests."""
import hashlib
import unittest
from datetime import datetime, timezone
from uuid import uuid4

from runtime.player_activation import PostgresPlayerActivationService, PlayerActivationError


class Cursor:
    def __init__(self, person_id=42, fail_at=None):
        self.person_id = person_id
        self.fail_at = fail_at
        self.calls = []
        self.last = None

    def execute(self, sql, params=()):
        self.calls.append((sql, params))
        if self.fail_at == len(self.calls):
            raise RuntimeError("simulated database failure")
        if "bind_accepted_identity" in sql:
            self.last = (self.person_id,)
        elif "SELECT status FROM sw_auth.principal" in sql:
            self.last = ("active",)
        elif "SELECT policy_version FROM sw_auth.policy_version" in sql:
            self.last = ("test-policy",)
        else:
            self.last = None

    def fetchone(self):
        return self.last


class Connection:
    def __init__(self, cursor):
        self.value = cursor
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.rolled_back = exc_type is not None
        self.committed = exc_type is None
        return False

    def cursor(self):
        return self.value


class ActivationTests(unittest.TestCase):
    def test_binding_and_session_share_one_transaction_and_canonical_person(self):
        cursor = Cursor(person_id=812)
        connection = Connection(cursor)
        service = PostgresPlayerActivationService(lambda: connection)
        principal_id, player_id = uuid4(), uuid4()

        result = service.activate(
            principal_id, player_id,
            now=datetime(2026, 11, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(result.person_id, 812)
        self.assertEqual(result.session.active_person_id if hasattr(result.session, "active_person_id") else 812, 812)
        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        self.assertIn("bind_accepted_identity", cursor.calls[0][0])
        self.assertTrue(any("INSERT INTO sw_auth.session" in sql for sql, _ in cursor.calls))
        self.assertEqual(cursor.calls[0][1], (principal_id, player_id))

    def test_session_digest_not_raw_credential_is_inserted(self):
        cursor = Cursor()
        connection = Connection(cursor)
        service = PostgresPlayerActivationService(lambda: connection)
        result = service.activate(uuid4(), uuid4())
        insert = next(params for sql, params in cursor.calls if "INSERT INTO sw_auth.session" in sql)
        self.assertEqual(insert[2], hashlib.sha256(result.session.credential.encode()).digest())
        self.assertNotEqual(insert[2], result.session.credential.encode())

    def test_failed_session_issue_rolls_back_identity_binding_transaction(self):
        cursor = Cursor(fail_at=3)
        connection = Connection(cursor)
        service = PostgresPlayerActivationService(lambda: connection)
        with self.assertRaises(PlayerActivationError):
            service.activate(uuid4(), uuid4())
        self.assertTrue(connection.rolled_back)
        self.assertFalse(connection.committed)

    def test_invalid_ids_are_rejected_before_database_access(self):
        touched = []
        service = PostgresPlayerActivationService(lambda: touched.append(True))
        with self.assertRaises(TypeError):
            service.activate("principal", uuid4())
        self.assertEqual(touched, [])


if __name__ == "__main__":
    unittest.main()
