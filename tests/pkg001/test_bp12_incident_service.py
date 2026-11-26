import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.bp12_incident_service import PostgresIncidentService
from runtime.security import (
    AuthorizationService, Effect, Grant, InMemoryAuditSink, PrincipalKind,
    PrincipalStatus, SessionStatus, VerifiedSession,
)


class FakeVerifier:
    def __init__(self, session):
        self.session = session

    def verify(self, credential):
        return self.session if credential == "officer-session" else None


class FakeCursor:
    def __init__(self, one=None, many=None):
        self.one = one
        self.many = many or []
        self.calls = []

    def execute(self, query, params=None):
        self.calls.append((query, params))

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.many

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def build_service(cursor, *, grants=None, active_person_id=42):
    now = datetime.now(timezone.utc)
    session = VerifiedSession(
        session_id=uuid4(), principal_id=uuid4(),
        principal_kind=PrincipalKind.OFFICER,
        principal_status=PrincipalStatus.ACTIVE,
        session_status=SessionStatus.ACTIVE,
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        active_person_id=active_person_id,
        roles=frozenset({"dispatcher"}),
    )
    audit = InMemoryAuditSink()
    default_grants = (
        Grant("bp12.incident.list", "incidents:open", "police_workflow",
              Effect.ALLOW, principal_kind=PrincipalKind.OFFICER),
        Grant("bp12.incident.inspect", "incident:*", "police_workflow",
              Effect.ALLOW, principal_kind=PrincipalKind.OFFICER),
        Grant("bp12.incident.create", "incidents:intake", "police_workflow",
              Effect.ALLOW, principal_kind=PrincipalKind.OFFICER),
    )
    authorization = AuthorizationService(
        FakeVerifier(session), audit, default_grants if grants is None else grants
    )
    connection = FakeConnection(cursor)
    service = PostgresIncidentService(
        lambda: connection, authorization, session.principal_id
    )
    return service, audit, connection


class BP12IncidentServiceTests(unittest.TestCase):
    def test_list_open_returns_bounded_canonical_incident_rows(self):
        row = (7, "SWI-0000007", "RECEIVED", "police_call", "unclassified",
               2, "unassessed", None, 3, 3, 3, 1, 1)
        cursor = FakeCursor(many=[row])
        service, audit, _ = build_service(cursor)
        result = service.list_open("officer-session", limit=5)
        self.assertEqual(result[0]["incident_ref"], "SWI-0000007")
        self.assertIn("ORDER BY priority ASC NULLS LAST", cursor.calls[0][0])
        self.assertEqual(cursor.calls[0][1], (5,))
        self.assertTrue(audit.records[-1].allowed)

    def test_inspect_returns_incident_and_ordered_location_history(self):
        incident = (7, "SWI-0000007", 1, "RECEIVED", "police_call", "CALL-7",
                    "anonymous", "Caller reports a disturbance", None,
                    "unclassified", None, "unassessed", None, 3, 3, 3,
                    "communications", None, None, None, None, None, 1, 1)
        location = (10, "primary", "raw", None, None, "outside the terminal",
                    "unverified", 3, 91, "police_call:CALL-7")
        cursor = FakeCursor(one=incident, many=[location])
        service, _, _ = build_service(cursor)
        result = service.inspect("officer-session", 7)
        self.assertEqual(result["incident_id"], 7)
        self.assertEqual(result["locations"][0]["raw_description"], "outside the terminal")
        self.assertEqual(len(cursor.calls), 2)

    def test_create_uses_verified_officer_person_id_and_bp12_function(self):
        cursor = FakeCursor(one=(71,))
        service, audit, connection = build_service(cursor)
        incident_id = service.create(
            "officer-session", source_type="police_call",
            source_record_id="CALL-71", narrative="Caller reports a disturbance",
            idempotency_key="incident:CALL-71",
            caller_identity_state="anonymous",
            location_raw="outside the terminal",
        )
        self.assertEqual(incident_id, 71)
        query, params = cursor.calls[0]
        self.assertIn("sw_incident.create_incident", query)
        self.assertEqual(params[0:5], (
            "police_call", "CALL-71", "Caller reports a disturbance",
            "officer-person:42", "incident:CALL-71",
        ))
        self.assertEqual(params[8], "unassessed")
        self.assertEqual(params[9], "outside the terminal")
        self.assertTrue(connection.committed)
        self.assertTrue(audit.records[-1].allowed)

    def test_create_requires_verified_active_person(self):
        cursor = FakeCursor(one=(71,))
        service, _, _ = build_service(cursor, active_person_id=None)
        with self.assertRaises(PermissionError):
            service.create(
                "officer-session", source_type="police_call",
                source_record_id="CALL-71", narrative="Report",
                idempotency_key="incident:CALL-71",
            )
        self.assertEqual(cursor.calls, [])

    def test_default_deny_prevents_database_access(self):
        cursor = FakeCursor(many=[])
        service, audit, _ = build_service(cursor, grants=())
        with self.assertRaises(PermissionError):
            service.list_open("officer-session")
        self.assertEqual(cursor.calls, [])
        self.assertFalse(audit.records[-1].allowed)

    def test_player_principal_cannot_use_officer_incident_service(self):
        cursor = FakeCursor(many=[])
        service, audit, _ = build_service(cursor)
        session = service._authorization._verifier.session
        from dataclasses import replace
        service._authorization._verifier.session = replace(
            session, principal_kind=PrincipalKind.PLAYER
        )
        with self.assertRaises(PermissionError):
            service.list_open("officer-session")
        self.assertEqual(cursor.calls, [])
        self.assertEqual(audit.records[-1].reason, "principal_kind_mismatch")

    def test_invalid_queue_limit_and_incident_id_are_rejected(self):
        cursor = FakeCursor()
        service, _, _ = build_service(cursor)
        with self.assertRaises(ValueError):
            service.list_open("officer-session", limit=101)
        with self.assertRaises(ValueError):
            service.inspect("officer-session", 0)
        self.assertEqual(cursor.calls, [])

    def test_invalid_intake_values_are_rejected_before_authorization_or_write(self):
        cursor = FakeCursor()
        service, audit, _ = build_service(cursor)
        with self.assertRaises(ValueError):
            service.create(
                "officer-session", source_type="unknown_source",
                source_record_id="CALL-1", narrative="Report",
                idempotency_key="incident:CALL-1",
            )
        self.assertEqual(cursor.calls, [])
        self.assertEqual(audit.records, [])


if __name__ == "__main__":
    unittest.main()
