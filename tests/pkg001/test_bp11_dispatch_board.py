import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.bp11_dispatch_board import PostgresDispatchBoard
from runtime.security import (
    AuthorizationService, Effect, Grant, InMemoryAuditSink, PrincipalKind,
    PrincipalStatus, SessionStatus, VerifiedSession,
)


class Verifier:
    def __init__(self, session):
        self.session = session

    def verify(self, credential):
        return self.session if credential == "dispatcher-session" else None


class Cursor:
    def __init__(self, rows=()):
        self.rows = list(rows)
        self.calls = []

    def execute(self, query, params=None):
        self.calls.append((query, params))

    def fetchall(self):
        return self.rows

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class Connection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def make_board(cursor, *, grants=None, principal_kind=PrincipalKind.OFFICER):
    now = datetime.now(timezone.utc)
    principal_id = uuid4()
    session = VerifiedSession(
        session_id=uuid4(), principal_id=principal_id,
        principal_kind=principal_kind, principal_status=PrincipalStatus.ACTIVE,
        session_status=SessionStatus.ACTIVE,
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        active_person_id=19, roles=frozenset({"dispatcher"}),
    )
    allowed = (
        Grant("bp11.dispatch.board.read", "dispatch-board:incidents",
              "police_workflow", Effect.ALLOW,
              principal_kind=PrincipalKind.OFFICER),
        Grant("bp11.dispatch.units.read", "dispatch-board:units",
              "police_workflow", Effect.ALLOW,
              principal_kind=PrincipalKind.OFFICER),
    )
    audit = InMemoryAuditSink()
    auth = AuthorizationService(
        Verifier(session), audit, allowed if grants is None else grants
    )
    board = PostgresDispatchBoard(
        lambda: Connection(cursor), auth, principal_id
    )
    return board, audit


class BP11DispatchBoardTests(unittest.TestCase):
    def test_incident_queue_reads_canonical_bp12_queue_bounded(self):
        row = (4, "SWI-0000004", "ASSESSED", "police_call", "assault",
               1, "high", "Immediate threat reported", 8, 8, 8, 1, 2,
               None, "communications")
        cursor = Cursor([row])
        board, audit = make_board(cursor)
        queue = board.incident_queue("dispatcher-session", limit=10)
        self.assertEqual(queue[0]["incident_ref"], "SWI-0000004")
        self.assertEqual(cursor.calls[0][1], (10,))
        self.assertIn("FROM sw_incident.incident_current", cursor.calls[0][0])
        self.assertTrue(audit.records[-1].allowed)

    def test_unit_readiness_uses_bp08_projection_and_preserves_reason(self):
        row = ("SWPS-UNIT-PATROL", "General Patrol", "general_patrol",
               "frontline", True, 2, 6, 12, 5, "available", True,
               False, "resource_readiness_not_integrated",
               ["patrol", "first_response"])
        cursor = Cursor([row])
        board, audit = make_board(cursor)
        units = board.unit_readiness("dispatcher-session")
        self.assertEqual(units[0]["unit_id"], "SWPS-UNIT-PATROL")
        self.assertTrue(units[0]["staffing_eligible"])
        self.assertFalse(units[0]["dispatch_eligible"])
        self.assertEqual(units[0]["readiness_reason"],
                         "resource_readiness_not_integrated")
        self.assertTrue(audit.records[-1].allowed)

    def test_snapshot_reports_zero_assignments_and_eligible_count(self):
        incident = (4, "SWI-0000004", "ASSESSED", "police_call", "assault",
                    1, "high", "Urgent", 8, 8, 8, 1, 1, None, "communications")
        unit = ("SWPS-UNIT-PATROL", "General Patrol", "general_patrol",
                "frontline", True, 2, 6, 12, 5, "available", True,
                False, "resource_readiness_not_integrated", ["patrol"])
        cursor = Cursor([incident, unit])
        board, _ = make_board(cursor)
        result = board.snapshot("dispatcher-session", incident_limit=5)
        self.assertEqual(result["incident_count"], 1)
        self.assertEqual(result["unit_profile_count"], 1)
        self.assertEqual(result["eligible_unit_count"], 0)
        self.assertEqual(result["assignments_created"], 0)
        self.assertTrue(result["snapshot_is_read_only"])
        self.assertEqual(len(cursor.calls), 2)

    def test_default_deny_blocks_database_reads(self):
        cursor = Cursor()
        board, audit = make_board(cursor, grants=())
        with self.assertRaises(PermissionError):
            board.incident_queue("dispatcher-session")
        self.assertEqual(cursor.calls, [])
        self.assertFalse(audit.records[-1].allowed)

    def test_player_principal_cannot_read_officer_dispatch_board(self):
        cursor = Cursor()
        board, audit = make_board(cursor, principal_kind=PrincipalKind.PLAYER)
        with self.assertRaises(PermissionError):
            board.unit_readiness("dispatcher-session")
        self.assertEqual(cursor.calls, [])
        self.assertEqual(audit.records[-1].reason, "principal_kind_mismatch")

    def test_invalid_limit_rejected_before_database_access(self):
        cursor = Cursor()
        board, _ = make_board(cursor)
        for value in (0, 101, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                board.incident_queue("dispatcher-session", limit=value)
        self.assertEqual(cursor.calls, [])


if __name__ == "__main__":
    unittest.main()
