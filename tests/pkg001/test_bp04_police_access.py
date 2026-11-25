import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.bp04_police_access import BP04PoliceLookupAccess
from runtime.security import (
    AuthorizationService, Effect, Grant, InMemoryAuditSink,
    PrincipalKind, PrincipalStatus, SessionStatus, VerifiedSession,
)


class FakeVerifier:
    def __init__(self, session):
        self.session = session

    def verify(self, credential):
        return self.session if credential == "officer-session" else None


class FakeLookup:
    def search(self, kind, query, limit=20):
        return [{"address_id": "SWADDR-1", "address_label": "10 Harbour Avenue"}]

    def address_detail(self, identifier):
        return {"address": {"address_id": identifier, "address_label": "10 Harbour Avenue"}}

    def property_detail(self, identifier):
        return {"property": {"property_id": identifier}}

    def business_detail(self, identifier):
        return {"business": {"business_id": identifier}}

    def get(self, kind, identifier):
        return {"record_type": kind, "id": identifier}


def make_session(kind=PrincipalKind.OFFICER):
    now = datetime.now(timezone.utc)
    return VerifiedSession(
        session_id=uuid4(),
        principal_id=uuid4(),
        principal_kind=kind,
        principal_status=PrincipalStatus.ACTIVE,
        session_status=SessionStatus.ACTIVE,
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        roles=frozenset({"property_reader"}),
        policy_version="police-test",
    )


class BP04PoliceAccessTests(unittest.TestCase):
    def setUp(self):
        self.session = make_session()
        self.audit = InMemoryAuditSink()
        self.verifier = FakeVerifier(self.session)
        self.grants = (
            Grant(
                "bp04.lookup.search.address", "bp04:address:search",
                "police_workflow", Effect.ALLOW,
                principal_kind=PrincipalKind.OFFICER, role="property_reader",
            ),
            Grant(
                "bp04.lookup.inspect.address", "bp04:address:*",
                "police_workflow", Effect.ALLOW,
                principal_kind=PrincipalKind.OFFICER, role="property_reader",
            ),
        )
        self.authorization = AuthorizationService(self.verifier, self.audit, self.grants)
        self.lookup = FakeLookup()
        self.access = BP04PoliceLookupAccess(
            self.lookup, self.authorization, self.session.principal_id
        )

    def test_authorised_officer_search_is_returned_and_audited(self):
        rows = self.access.search("officer-session", "address", "Harbour Avenue", 5)
        self.assertEqual(rows[0]["address_id"], "SWADDR-1")
        self.assertEqual(len(self.audit.records), 1)
        self.assertTrue(self.audit.records[0].allowed)
        self.assertEqual(self.audit.records[0].action, "bp04.lookup.search.address")

    def test_authorised_officer_can_resolve_address_and_is_audited(self):
        row = self.access.resolve_address("officer-session", "SWADDR-1")
        self.assertEqual(row["address"]["address_id"], "SWADDR-1")
        self.assertTrue(self.audit.records[-1].allowed)
        self.assertEqual(self.audit.records[-1].resource, "bp04:address:SWADDR-1")

    def test_player_principal_is_denied_even_if_an_officer_grant_exists(self):
        player = make_session(PrincipalKind.PLAYER)
        self.verifier.session = player
        access = BP04PoliceLookupAccess(
            self.lookup, self.authorization, player.principal_id
        )
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            access.search("officer-session", "address", "Harbour Avenue")
        self.assertEqual(self.audit.records[-1].reason, "principal_kind_mismatch")
        self.assertFalse(self.audit.records[-1].allowed)

    def test_default_deny_without_explicit_police_grant(self):
        denied = BP04PoliceLookupAccess(
            self.lookup,
            AuthorizationService(self.verifier, self.audit, ()),
            self.session.principal_id,
        )
        with self.assertRaises(PermissionError):
            denied.search("officer-session", "address", "Harbour Avenue")
        self.assertEqual(self.audit.records[-1].reason, "no_matching_grant")

    def test_invalid_entity_type_is_rejected_before_lookup(self):
        with self.assertRaises(ValueError):
            self.access.search("officer-session", "room", "private")
        with self.assertRaises(ValueError):
            self.access.inspect("officer-session", "room", "ROOM-1")

    def test_resource_scoped_inspection_is_not_broader_than_grant(self):
        with self.assertRaises(PermissionError):
            self.access.inspect("officer-session", "property", "SWPROP-1")
        self.assertEqual(self.audit.records[-1].reason, "no_matching_grant")


if __name__ == "__main__":
    unittest.main()
