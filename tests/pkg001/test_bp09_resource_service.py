import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.bp09_resource_service import PostgresResourceReadinessService
from runtime.security import (
    AuthorizationService, Effect, Grant, InMemoryAuditSink, PrincipalKind,
    PrincipalStatus, SessionStatus, VerifiedSession,
)


class Verifier:
    def __init__(self, session):
        self.session = session

    def verify(self, credential):
        return self.session if credential == "officer-session" else None


class Cursor:
    def __init__(self, rows=(), one=None):
        self.rows = list(rows)
        self.one = one
        self.calls = []

    def execute(self, query, params=None):
        self.calls.append((query, params))

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.one

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


def make_service(cursor, *, grants=None, principal_kind=PrincipalKind.OFFICER):
    now = datetime.now(timezone.utc)
    principal_id = uuid4()
    session = VerifiedSession(
        session_id=uuid4(), principal_id=principal_id,
        principal_kind=principal_kind, principal_status=PrincipalStatus.ACTIVE,
        session_status=SessionStatus.ACTIVE, issued_at=now-timedelta(minutes=1),
        expires_at=now+timedelta(hours=1), active_person_id=19,
        roles=frozenset({"resource_manager"}),
    )
    allowed = [
        Grant("bp09.resources.unit.read", "police-resources:unit:SWPS-UNIT-PATROL",
              "police_workflow", Effect.ALLOW, principal_kind=PrincipalKind.OFFICER)
    ]
    audit = InMemoryAuditSink()
    auth = AuthorizationService(Verifier(session), audit, allowed if grants is None else grants)
    service = PostgresResourceReadinessService(
        lambda: Connection(cursor), auth, principal_id
    )
    return service, audit


class BP09ResourceServiceTests(unittest.TestCase):
    def test_unit_readiness_returns_requirement_summary(self):
        cursor = Cursor(one=("SWPS-UNIT-PATROL", True, 6, 6))
        service, audit = make_service(cursor)
        result = service.unit_readiness("officer-session", "SWPS-UNIT-PATROL")
        self.assertEqual(result["satisfied_requirements"], 6)
        self.assertTrue(result["resources_ready"])
        self.assertEqual(cursor.calls[0][1], ("SWPS-UNIT-PATROL",))
        self.assertTrue(audit.records[-1].allowed)

    def test_unit_inventory_returns_allocated_and_serviceable_counts(self):
        cursor = Cursor([
            ("SWPS-RM-PATROL-VEH", "Marked patrol vehicle", 1, 1, 1),
            ("SWPS-RM-RADIO", "Handheld operational radio", 2, 2, 1),
        ])
        service, _ = make_service(cursor)
        rows = service.unit_inventory("officer-session", "SWPS-UNIT-PATROL")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["allocated_quantity"], 2)
        self.assertEqual(rows[1]["serviceable_quantity"], 1)
        self.assertIn("sw_police.resource_asset", cursor.calls[0][0])

    def test_default_deny_prevents_database_access(self):
        cursor = Cursor()
        service, audit = make_service(cursor, grants=())
        with self.assertRaises(PermissionError):
            service.unit_inventory("officer-session", "SWPS-UNIT-PATROL")
        self.assertEqual(cursor.calls, [])
        self.assertFalse(audit.records[-1].allowed)

    def test_player_principal_cannot_read_officer_resources(self):
        cursor = Cursor()
        service, audit = make_service(cursor, principal_kind=PrincipalKind.PLAYER)
        with self.assertRaises(PermissionError):
            service.unit_readiness("officer-session", "SWPS-UNIT-PATROL")
        self.assertEqual(cursor.calls, [])
        self.assertEqual(audit.records[-1].reason, "principal_kind_mismatch")

    def test_unknown_unit_returns_not_found(self):
        cursor = Cursor(one=None)
        service, _ = make_service(cursor)
        with self.assertRaises(LookupError):
            service.unit_readiness("officer-session", "SWPS-UNIT-PATROL")

    def test_invalid_unit_id_rejected_before_authorization_or_database(self):
        cursor = Cursor()
        service, _ = make_service(cursor)
        for value in ("", "x" * 121, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                service.unit_inventory("officer-session", value)
        self.assertEqual(cursor.calls, [])


if __name__ == "__main__":
    unittest.main()
