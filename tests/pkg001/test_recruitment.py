"""PKG-003 adapter contract tests; PostgreSQL invariants run in SQL acceptance tests."""
import unittest
from uuid import uuid4

from runtime.recruitment import PostgresRecruitmentService, RecruitmentError


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.executed = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params):
        self.executed = (sql, params)

    def fetchone(self):
        return self.row

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self, row):
        self.cursor_value = FakeCursor(row)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cursor(self):
        return self.cursor_value


class RecruitmentAdapterTests(unittest.TestCase):
    def setUp(self):
        self.row = (uuid4(),)
        self.connection = FakeConnection(self.row)
        self.service = PostgresRecruitmentService(lambda: self.connection)

    def test_request_calls_single_authoritative_database_function(self):
        player_id = uuid4()
        result = self.service.request_intake(player_id, "Player", "request-0001")
        self.assertEqual(result, self.row[0])
        sql, params = self.connection.cursor_value.executed
        self.assertIn("sw_police.request_recruit_intake", sql)
        self.assertEqual(params, (player_id, "Player", "request-0001"))

    def test_accept_requires_explicit_approver_and_supervisor(self):
        intake_id, approver_id = uuid4(), uuid4()
        result = self.service.accept_intake(
            intake_id, supervisor_person_id=12, appointment_source="Recruitment decision",
            idempotency_key="accept-0001", authorised_by_principal_id=approver_id,
            given_name="Alex", middle_name="Morgan", family_name="Taylor",
        )
        self.assertEqual(result, self.row[0])
        sql, params = self.connection.cursor_value.executed
        self.assertIn("sw_police.accept_recruit_intake", sql)
        self.assertEqual(params[:5], (
            intake_id, 12, "Recruitment decision", "accept-0001", approver_id
        ))

    def test_rejects_short_idempotency_key_before_database_call(self):
        with self.assertRaises(ValueError):
            self.service.request_intake(uuid4(), "Player", "short")
        self.assertIsNone(self.connection.cursor_value.executed)

    def test_rejects_incomplete_canonical_name_before_database_call(self):
        with self.assertRaises(ValueError):
            self.service.accept_intake(
                uuid4(), supervisor_person_id=12, appointment_source="Decision",
                idempotency_key="accept-0003", authorised_by_principal_id=uuid4(),
                given_name="Alex",
            )
        self.assertIsNone(self.connection.cursor_value.executed)

    def test_rejects_missing_supervisor_before_database_call(self):
        with self.assertRaises(ValueError):
            self.service.accept_intake(
                uuid4(), supervisor_person_id=0, appointment_source="Decision",
                idempotency_key="accept-0002", authorised_by_principal_id=uuid4(),
            )
        self.assertIsNone(self.connection.cursor_value.executed)

    def test_database_errors_are_returned_as_recruitment_errors(self):
        def unavailable():
            raise RuntimeError("database unavailable")
        service = PostgresRecruitmentService(unavailable)
        with self.assertRaises(RecruitmentError):
            service.request_intake(uuid4(), "Player", "request-0004")

    def test_rejects_non_uuid_player_identifier(self):
        with self.assertRaises(ValueError):
            self.service.request_intake("player-1", "Player", "request-0003")


if __name__ == "__main__":
    unittest.main()
