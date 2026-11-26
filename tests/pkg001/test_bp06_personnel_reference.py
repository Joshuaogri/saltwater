import unittest
from uuid import uuid4

from runtime.postgres_security import PostgresPersonnelReferenceVerifier


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return self._cursor


class BP06PersonnelReferenceVerifierTests(unittest.TestCase):
    def test_matches_person_and_active_sworn_personnel_dossier(self):
        personnel_id = uuid4()
        cursor = FakeCursor((1,))
        verifier = PostgresPersonnelReferenceVerifier(lambda: FakeConnection(cursor))

        self.assertTrue(verifier(73, str(personnel_id)))
        self.assertIn("sw_police.personnel_service_current", cursor.query)
        self.assertIn("service_status='active'", cursor.query)
        self.assertIn("personnel_category='sworn_officer'", cursor.query)
        self.assertIn("service_state='active'", cursor.query)
        self.assertEqual(cursor.params, (73, personnel_id))

    def test_nonmatching_or_inactive_personnel_reference_is_false(self):
        cursor = FakeCursor(None)
        verifier = PostgresPersonnelReferenceVerifier(lambda: FakeConnection(cursor))
        self.assertFalse(verifier(73, str(uuid4())))

    def test_invalid_person_or_non_uuid_reference_fails_before_database(self):
        def unexpected_connect():
            raise AssertionError("database must not be queried")
        verifier = PostgresPersonnelReferenceVerifier(unexpected_connect)
        self.assertFalse(verifier(0, str(uuid4())))
        self.assertFalse(verifier(73, "officer:73"))
        self.assertFalse(verifier(73, ""))

    def test_database_failure_propagates_for_fail_closed_caller(self):
        def broken_connect():
            raise RuntimeError("database unavailable")
        verifier = PostgresPersonnelReferenceVerifier(broken_connect)
        with self.assertRaisesRegex(RuntimeError, "database unavailable"):
            verifier(73, str(uuid4()))


if __name__ == "__main__":
    unittest.main()
