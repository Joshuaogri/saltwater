import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import patch

from runtime.bp04_police_access import (
    BP04PoliceLookupAccess,
    BP04IncidentLocationResolver,
    create_postgres_bp04_police_lookup_access,
)
from runtime.bp12_incident_location_history import PostgresIncidentLocationHistoryReader
from runtime.bp12_incident_operational_events import (
    PostgresIncidentOperationalEventWriter,
    PostgresIncidentOperationalTimelineReader,
    build_incident_operational_timeline_view,
    reconcile_incident_command_handover,
)
from runtime.security import (
    AuthorizationService, Effect, Grant, InMemoryAuditSink,
    PrincipalKind, PrincipalStatus, SessionStatus, VerifiedSession,
)


class FakeVerifier:
    def __init__(self, session):
        self.session = session

    def verify(self, credential):
        return self.session if credential == "officer-session" else None


class FailingAuditSink:
    def append(self, _record):
        raise RuntimeError("audit storage unavailable")


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


class FakeHistoryCursor:
    description = [
        ("incident_location_id",), ("incident_id",), ("location_role",),
        ("location_type",), ("spatial_id",), ("location_ref",),
        ("raw_description",), ("confidence",), ("effective_tick",),
        ("source_event_id",), ("source_ref",), ("event_occurred_at",),
        ("event_source_ref",), ("event_attributes",),
    ]

    def __init__(self, rows):
        self.rows = rows
        self.executed = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.executed = (query, params)

    def fetchall(self):
        return self.rows


class FakeHistoryConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return self._cursor


class FakeOperationalCursor:
    def __init__(self, result=(8801,)):
        self.result = result
        self.executed = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.executed = (query, params)

    def fetchone(self):
        return self.result


class FakeOperationalConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


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


    def test_postgres_factory_uses_live_verifier_grant_provider_and_durable_audit(self):
        with patch("runtime.postgres_security.PostgresSessionVerifier") as verifier, patch(
            "runtime.postgres_security.PostgresAuditSink"
        ) as audit, patch(
            "runtime.postgres_security.PostgresGrantProvider"
        ) as grants:
            access = create_postgres_bp04_police_lookup_access(
                lambda: None, self.lookup, self.session.principal_id
            )
        self.assertIsInstance(access, BP04PoliceLookupAccess)
        verifier.assert_called_once()
        audit.assert_called_once()
        grants.assert_called_once()

    def test_audit_storage_failure_denies_authorized_lookup(self):
        authorization = AuthorizationService(
            self.verifier, FailingAuditSink(), self.grants
        )
        access = BP04PoliceLookupAccess(
            self.lookup, authorization, self.session.principal_id
        )
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            access.search("officer-session", "address", "Harbour Avenue")
        
    def test_revoked_session_is_denied_and_audited(self):
        from dataclasses import replace
        self.verifier.session = replace(
            self.session, session_status=SessionStatus.REVOKED
        )
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            self.access.search("officer-session", "address", "Harbour Avenue")
        self.assertEqual(self.audit.records[-1].reason, "session_not_active")
        self.assertFalse(self.audit.records[-1].allowed)

    def test_incident_location_candidate_preserves_provenance_without_writing(self):
        incident_grants = self.grants + (
            Grant(
                "bp12.incident.inspect.location", "incident:*",
                "police_workflow", Effect.ALLOW,
                principal_kind=PrincipalKind.OFFICER, role="property_reader",
            ),
        )
        access = BP04PoliceLookupAccess(
            self.lookup,
            AuthorizationService(self.verifier, self.audit, incident_grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(
            access,
            lambda incident_id: {
                "incident_id": incident_id,
                "incident_ref": "SWI-0000042",
                "source_type": "police_call",
                "source_record_id": "CALL-77",
                "source_ref": "police_call:CALL-77",
            },
        )
        candidate = resolver.prepare_address_candidate(
            "officer-session", 42, "SWADDR-1",
            location_role="primary", confidence="unverified",
            source_ref="caller-stated:Harbour Avenue",
        )
        self.assertEqual(candidate["incident_source_ref"], "police_call:CALL-77")
        self.assertEqual(candidate["source_ref"], "caller-stated:Harbour Avenue")
        self.assertEqual(candidate["address_source_ref"], "bp04-address:SWADDR-1")
        self.assertTrue(candidate["approval_required"])
        self.assertFalse(candidate["persisted"])
        self.assertEqual(len(self.audit.records), 2)
        self.assertTrue(all(record.allowed for record in self.audit.records))

    def test_record_address_location_uses_bp12_writer_with_both_provenance_refs(self):
        incident_grants = self.grants + (
            Grant(
                "bp12.incident.inspect.location", "incident:*",
                "police_workflow", Effect.ALLOW,
                principal_kind=PrincipalKind.OFFICER, role="property_reader",
            ),
        )
        access = BP04PoliceLookupAccess(
            self.lookup,
            AuthorizationService(self.verifier, self.audit, incident_grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(
            access,
            lambda incident_id: {
                "incident_id": incident_id,
                "incident_ref": "SWI-0000042",
                "source_type": "police_call",
                "source_record_id": "CALL-77",
            },
        )
        captured = {}
        def writer(**kwargs):
            captured.update(kwargs)
            return 901
        result = resolver.record_address_location(
            "officer-session", 42, "SWADDR-1",
            location_writer=writer, actor_ref="officer:7",
            authority_ref="grant:location-write",
            idempotency_key="INC-42-LOC-1",
            source_ref="caller-stated:Harbour Avenue",
            raw_description="Caller reports entrance on Harbour Avenue",
        )
        self.assertEqual(result["incident_location_id"], 901)
        self.assertTrue(result["persisted"])
        self.assertFalse(result["approval_required"])
        self.assertEqual(captured["p_source_ref"], "caller-stated:Harbour Avenue")
        self.assertEqual(captured["p_address_source_ref"], "bp04-address:SWADDR-1")
        self.assertEqual(captured["p_location_ref"], "SWADDR-1")
        self.assertIsNone(captured["p_spatial_id"])
        self.assertEqual(captured["p_idempotency_key"], "INC-42-LOC-1")

    def test_postgres_operational_event_writer_uses_parameterised_bp12_function(self):
        cursor = FakeOperationalCursor((8801,))
        connection = FakeOperationalConnection(cursor)
        writer = PostgresIncidentOperationalEventWriter(lambda: connection)
        event_id = writer.record(
            incident_id=42, event_code="UNIT_ARRIVED",
            actor_ref="officer:12", authority_ref="patrol-order:5",
            source_ref="bp10-arrival:PATROL-ACT-19",
            description="Unit arrived", idempotency_key="ARRIVAL-001",
            unit_ref="UNIT-7", assignment_ref="DEP-4",
            field_activity_ref="PATROL-ACT-19",
        )
        self.assertEqual(event_id, 8801)
        self.assertIn("record_operational_timeline_event(", cursor.executed[0])
        self.assertEqual(cursor.executed[0].count("%s"), 11)
        self.assertEqual(cursor.executed[1][0:2], (42, "UNIT_ARRIVED"))
        self.assertEqual(cursor.executed[1][7:9], ("DEP-4", "PATROL-ACT-19"))
        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)

    def test_postgres_operational_event_writer_rejects_missing_arrival_refs(self):
        writer = PostgresIncidentOperationalEventWriter(lambda: self.fail("DB must not be opened"))
        with self.assertRaisesRegex(ValueError, "Unit, deployment and field activity"):
            writer.record(
                incident_id=42, event_code="UNIT_ARRIVED",
                actor_ref="officer:12", authority_ref="patrol-order:5",
                source_ref="bp10-arrival:bad", description="Unit arrived",
                idempotency_key="ARRIVAL-BAD",
            )

    def test_postgres_incident_location_history_reader_uses_parameterised_read(self):
        values = (901, 42, "primary", "property", None, "SWADDR-1",
                  "Reported address", "unverified", 12, 7001,
                  "dispatch:CALL-9", None, "dispatch:CALL-9",
                  {"address_source_ref": "bp04-address:SWADDR-1"})
        cursor = FakeHistoryCursor([values])
        reader = PostgresIncidentLocationHistoryReader(
            lambda: FakeHistoryConnection(cursor)
        )
        rows = reader.read(42)
        self.assertEqual(rows[0]["incident_id"], 42)
        self.assertEqual(rows[0]["event_attributes"]["address_source_ref"],
                         "bp04-address:SWADDR-1")
        self.assertEqual(cursor.executed[1], (42,))
        self.assertIn("incident_location_history(%s)", cursor.executed[0])

    def test_postgres_incident_location_history_reader_rejects_invalid_id(self):
        reader = PostgresIncidentLocationHistoryReader(lambda: None)
        with self.assertRaises(ValueError):
            reader.read(0)

    def test_incident_location_history_requires_separate_history_grant_and_preserves_rows(self):
        grants = self.grants + (
            Grant(
                "bp12.incident.inspect.location.history", "incident:*",
                "police_workflow", Effect.ALLOW,
                principal_kind=PrincipalKind.OFFICER, role="property_reader",
            ),
        )
        access = BP04PoliceLookupAccess(
            self.lookup,
            AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        rows = [{
            "incident_id": 42, "incident_location_id": 901,
            "source_event_id": 7001, "source_ref": "caller:CALL-77",
            "event_attributes": {"address_source_ref": "bp04-address:SWADDR-1"},
        }]
        result = resolver.read_location_history(
            "officer-session", 42,
            location_history_reader=lambda incident_id: rows,
        )
        self.assertEqual(result, rows)
        self.assertEqual(self.audit.records[-1].action,
                         "bp12.incident.inspect.location.history")
        self.assertTrue(self.audit.records[-1].allowed)

    def test_incident_location_history_denies_without_history_grant(self):
        resolver = BP04IncidentLocationResolver(
            self.access, lambda _id: None
        )
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.read_location_history(
                "officer-session", 42,
                location_history_reader=lambda _id: [],
            )
        self.assertEqual(
            self.audit.records[-1].action,
            "bp12.incident.inspect.location.history",
        )
        self.assertFalse(self.audit.records[-1].allowed)

    def test_incident_location_history_rejects_cross_incident_or_missing_provenance(self):
        grants = self.grants + (
            Grant(
                "bp12.incident.inspect.location.history", "incident:*",
                "police_workflow", Effect.ALLOW,
                principal_kind=PrincipalKind.OFFICER, role="property_reader",
            ),
        )
        access = BP04PoliceLookupAccess(
            self.lookup,
            AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        with self.assertRaisesRegex(ValueError, "conflicting incident identity"):
            resolver.read_location_history(
                "officer-session", 42,
                location_history_reader=lambda _id: [{"incident_id": 43}],
            )
        with self.assertRaisesRegex(ValueError, "missing mandatory provenance"):
            resolver.read_location_history(
                "officer-session", 42,
                location_history_reader=lambda _id: [{"incident_id": 42}],
            )

    def test_dispatch_handoff_requires_dispatch_incident_and_address_permissions(self):
        grants = self.grants + (
            Grant("bp11.dispatch.location.resolve", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp12.incident.inspect.location", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(
            access, lambda incident_id: {
                "incident_id": incident_id, "incident_ref": "SWI-42",
                "source_type": "call", "source_record_id": "CALL-9",
            },
        )
        result = resolver.prepare_dispatch_address_candidate(
            "officer-session", 42, "SWADDR-1",
            source_ref="dispatch:CALL-9",
        )
        self.assertEqual(result["address_id"], "SWADDR-1")
        self.assertTrue(result["dispatch_use_only"])
        self.assertNotIn("address", result)
        actions = [row.action for row in self.audit.records]
        self.assertEqual(actions, [
            "bp11.dispatch.location.resolve",
            "bp12.incident.inspect.location",
            "bp04.lookup.inspect.address",
        ])

    def test_dispatch_acknowledgement_requires_verified_assignment_and_mirrors_event(self):
        grants = self.grants + (
            Grant("bp11.dispatch.acknowledgement.record", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp11.dispatch.inspect.assignment", "dispatch:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        captured = {}
        result = resolver.record_dispatch_acknowledgement(
            "officer-session", 42, dispatch_ref="CAD-88",
            dispatch_incident_verifier=lambda ref, incident: ref == "CAD-88" and incident == 42,
            event_writer=lambda **kw: captured.update(kw) or 7101,
            actor_ref="dispatcher:4", authority_ref="dispatch-grant:9",
            idempotency_key="CAD-88-ACK-1", acknowledgement_ref="ACK-11",
            description="Unit acknowledges dispatch",
        )
        self.assertEqual(result["event_code"], "DISPATCH_ACKNOWLEDGED")
        self.assertEqual(result["event_id"], 7101)
        self.assertEqual(captured["dispatch_ref"], "CAD-88")
        self.assertEqual(captured["source_ref"], "dispatch-ack:ACK-11")
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp11.dispatch.acknowledgement.record",
             "bp11.dispatch.inspect.assignment"],
        )

    def test_dispatch_acknowledgement_rejects_unlinked_assignment_before_writer(self):
        grants = self.grants + (
            Grant("bp11.dispatch.acknowledgement.record", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp11.dispatch.inspect.assignment", "dispatch:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.record_dispatch_acknowledgement(
                "officer-session", 42, dispatch_ref="CAD-88",
                dispatch_incident_verifier=lambda _ref, _incident: False,
                event_writer=lambda **_kw: self.fail("writer must not run"),
                actor_ref="dispatcher:4", authority_ref="dispatch-grant:9",
                idempotency_key="CAD-88-ACK-2", acknowledgement_ref="ACK-12",
                description="Unlinked acknowledgement",
            )
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp11.dispatch.acknowledgement.record",
             "bp11.dispatch.inspect.assignment"],
        )

    def test_field_unit_arrival_requires_bp08_and_bp10_authorisation(self):
        grants = self.grants + (
            Grant("bp10.patrol.record_arrival", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp08.deployment.inspect.assignment", "assignment:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp10.patrol.inspect.field_activity", "field_activity:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        captured = {}
        result = resolver.record_field_unit_arrival(
            "officer-session", 42, unit_ref="UNIT-7", assignment_ref="DEP-4",
            field_activity_ref="PATROL-ACT-19",
            deployment_activity_verifier=lambda unit, assignment, activity, incident:
                (unit, assignment, activity, incident) ==
                ("UNIT-7", "DEP-4", "PATROL-ACT-19", 42),
            event_writer=lambda **kw: captured.update(kw) or 7102,
            actor_ref="officer:12", authority_ref="patrol-order:5",
            idempotency_key="PATROL-ACT-19-ARRIVAL",
            description="Unit reports arrival at incident location",
        )
        self.assertEqual(result["event_code"], "UNIT_ARRIVED")
        self.assertEqual(result["event_id"], 7102)
        self.assertEqual(captured["unit_ref"], "UNIT-7")
        self.assertEqual(captured["assignment_ref"], "DEP-4")
        self.assertEqual(captured["field_activity_ref"], "PATROL-ACT-19")
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp10.patrol.record_arrival", "bp08.deployment.inspect.assignment",
             "bp10.patrol.inspect.field_activity"],
        )

    def test_field_unit_arrival_rejects_unverified_deployment_before_writer(self):
        grants = self.grants + (
            Grant("bp10.patrol.record_arrival", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp08.deployment.inspect.assignment", "assignment:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp10.patrol.inspect.field_activity", "field_activity:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.record_field_unit_arrival(
                "officer-session", 42, unit_ref="UNIT-7", assignment_ref="DEP-4",
                field_activity_ref="PATROL-ACT-19",
                deployment_activity_verifier=lambda *_args: False,
                event_writer=lambda **_kw: self.fail("writer must not run"),
                actor_ref="officer:12", authority_ref="patrol-order:5",
                idempotency_key="PATROL-ACT-19-ARRIVAL-2",
                description="Unverified arrival",
            )
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp10.patrol.record_arrival", "bp08.deployment.inspect.assignment",
             "bp10.patrol.inspect.field_activity"],
        )

    def test_dispatch_location_update_is_event_writer_handoff_with_provenance(self):
        grants = self.grants + (
            Grant("bp11.dispatch.location.record", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp11.dispatch.inspect.assignment", "dispatch:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp11.dispatch.location.resolve", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp12.incident.inspect.location", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(
            access, lambda incident_id: {
                "incident_id": incident_id, "incident_ref": "SWI-42",
                "source_type": "call", "source_record_id": "CALL-9",
            },
        )
        captured = {}
        result = resolver.record_dispatch_address_location(
            "officer-session", 42, "SWADDR-1",
            dispatch_ref="CAD-88",
            dispatch_incident_verifier=lambda ref, incident_id: (
                ref == "CAD-88" and incident_id == 42
            ),
            location_writer=lambda **kw: (captured.update(kw) or 902),
            actor_ref="dispatcher:4", authority_ref="dispatch-grant:9",
            idempotency_key="CAD-88-LOC-1",
            raw_description="Dispatcher confirms caller's reported entrance",
            confidence="medium",
        )
        self.assertTrue(result["persisted"])
        self.assertEqual(result["incident_location_id"], 902)
        self.assertEqual(result["dispatch_ref"], "CAD-88")
        self.assertEqual(captured["p_source_ref"], "dispatch:CAD-88")
        self.assertEqual(captured["p_address_source_ref"], "bp04-address:SWADDR-1")
        self.assertEqual(captured["p_actor_ref"], "dispatcher:4")
        self.assertEqual(captured["p_authority_ref"], "dispatch-grant:9")
        self.assertEqual(captured["p_confidence"], "medium")
        self.assertEqual(captured["p_idempotency_key"], "CAD-88-LOC-1")
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp11.dispatch.location.record", "bp11.dispatch.inspect.assignment",
             "bp11.dispatch.location.resolve",
             "bp12.incident.inspect.location", "bp04.lookup.inspect.address"],
        )

    def test_dispatch_location_update_rejects_dispatch_linked_to_another_incident(self):
        grants = self.grants + (
            Grant("bp11.dispatch.location.record", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp11.dispatch.inspect.assignment", "dispatch:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(
            access, lambda _id: self.fail("incident should not be read")
        )
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.record_dispatch_address_location(
                "officer-session", 42, "SWADDR-1",
                dispatch_ref="CAD-OTHER",
                dispatch_incident_verifier=lambda _ref, _incident: False,
                location_writer=lambda **_kw: self.fail("BP12 writer must not run"),
                actor_ref="dispatcher:4", authority_ref="dispatch-grant:9",
                idempotency_key="CAD-OTHER-LOC-1",
                raw_description="Mismatched dispatch reference",
            )
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp11.dispatch.location.record", "bp11.dispatch.inspect.assignment"],
        )

    def test_dispatch_location_update_denies_before_writer_without_record_grant(self):
        grants = self.grants + (
            Grant("bp11.dispatch.location.resolve", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp12.incident.inspect.location", "incident:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: self.fail("incident read"))
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.record_dispatch_address_location(
                "officer-session", 42, "SWADDR-1",
                dispatch_ref="CAD-88",
                dispatch_incident_verifier=lambda _ref, _incident: True,
                location_writer=lambda **_kw: self.fail("writer"),
                actor_ref="dispatcher:4", authority_ref="dispatch-grant:9",
                idempotency_key="CAD-88-LOC-1", raw_description="Dispatch update",
            )
        self.assertEqual(self.audit.records[-1].action, "bp11.dispatch.location.record")
        self.assertFalse(self.audit.records[-1].allowed)

    def test_investigation_handoff_requires_investigation_and_bp12_history_grants(self):
        grants = self.grants + (
            Grant("bp16.investigation.inspect.case", "case:*",
                  "police_workflow", Effect.ALLOW,
                  principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp16.investigation.incident.location.history", "incident:*",
                  "police_workflow", Effect.ALLOW,
                  principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp12.incident.inspect.location.history", "incident:*",
                  "police_workflow", Effect.ALLOW,
                  principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        history = [{
            "incident_id": 42, "incident_location_id": 901,
            "source_event_id": 7001, "source_ref": "dispatch:CALL-9",
        }]
        result = resolver.read_investigation_location_history(
            "officer-session", 42, case_ref="CASE-7",
            case_incident_verifier=lambda case_ref, incident_id: (
                case_ref == "CASE-7" and incident_id == 42
            ),
            location_history_reader=lambda _id: history,
        )
        self.assertEqual(result, history)
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp16.investigation.inspect.case",
             "bp16.investigation.incident.location.history",
             "bp12.incident.inspect.location.history"],
        )

    def test_investigation_history_rejects_unlinked_incident_before_bp12_read(self):
        grants = self.grants + (
            Grant("bp16.investigation.inspect.case", "case:*", "police_workflow",
                  Effect.ALLOW, principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp16.investigation.incident.location.history", "incident:*",
                  "police_workflow", Effect.ALLOW,
                  principal_kind=PrincipalKind.OFFICER, role="property_reader"),
            Grant("bp12.incident.inspect.location.history", "incident:*",
                  "police_workflow", Effect.ALLOW,
                  principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.read_investigation_location_history(
                "officer-session", 42, case_ref="CASE-7",
                case_incident_verifier=lambda _case, _incident: False,
                location_history_reader=lambda _id: self.fail("history read must not run"),
            )
        self.assertEqual(
            [row.action for row in self.audit.records],
            ["bp16.investigation.inspect.case"],
        )

    def test_investigation_handoff_denies_without_investigation_grant(self):
        resolver = BP04IncidentLocationResolver(self.access, lambda _id: None)
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.read_investigation_location_history(
                "officer-session", 42, case_ref="CASE-7",
                case_incident_verifier=lambda _case, _incident: True,
                location_history_reader=lambda _id: [],
            )
        self.assertEqual(
            self.audit.records[-1].action,
            "bp16.investigation.inspect.case",
        )
        self.assertFalse(self.audit.records[-1].allowed)

    def test_incident_location_candidate_requires_incident_grant(self):
        resolver = BP04IncidentLocationResolver(
            self.access, lambda incident_id: {"incident_id": incident_id}
        )
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.prepare_address_candidate(
                "officer-session", 42, "SWADDR-1",
                source_ref="call:77",
            )
        self.assertEqual(self.audit.records[-1].action, "bp12.incident.inspect.location")
        self.assertFalse(self.audit.records[-1].allowed)

    def test_incident_location_candidate_rejects_missing_incident(self):
        incident_grants = self.grants + (
            Grant(
                "bp12.incident.inspect.location", "incident:*",
                "police_workflow", Effect.ALLOW,
                principal_kind=PrincipalKind.OFFICER, role="property_reader",
            ),
        )
        access = BP04PoliceLookupAccess(
            self.lookup,
            AuthorizationService(self.verifier, self.audit, incident_grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        with self.assertRaisesRegex(LookupError, "Incident not found"):
            resolver.prepare_address_candidate(
                "officer-session", 42, "SWADDR-1", source_ref="call:77"
            )
        self.assertEqual(len(self.audit.records), 1)

    def test_operational_timeline_read_requires_dedicated_grant_and_validates_provenance(self):
        grants = self.grants + (
            Grant("bp12.incident.inspect.operational_timeline", "incident:*",
                  "police_workflow", Effect.ALLOW,
                  principal_kind=PrincipalKind.OFFICER, role="property_reader"),
        )
        access = BP04PoliceLookupAccess(
            self.lookup, AuthorizationService(self.verifier, self.audit, grants),
            self.session.principal_id,
        )
        resolver = BP04IncidentLocationResolver(access, lambda _id: None)
        rows = [{
            "incident_id": 42, "event_id": 8801,
            "event_code": "UNIT_ARRIVED", "source_ref": "bp10-arrival:ACT-1",
            "attributes": {"source_ref": "bp10-arrival:ACT-1", "actor_ref": "officer:12", "authority_ref": "order:5", "unit_ref": "UNIT-7", "assignment_ref": "DEP-4", "field_activity_ref": "ACT-1"},
        }]
        self.assertEqual(
            resolver.read_operational_timeline(
                "officer-session", 42, operational_timeline_reader=lambda _id: rows
            ),
            rows,
        )
        self.assertEqual(self.audit.records[-1].action,
                         "bp12.incident.inspect.operational_timeline")

        with self.assertRaisesRegex(ValueError, "conflicting incident identity"):
            resolver.read_operational_timeline(
                "officer-session", 42,
                operational_timeline_reader=lambda _id: [{**rows[0], "incident_id": 43}],
            )

    def test_operational_timeline_read_denies_without_grant_before_reader(self):
        resolver = BP04IncidentLocationResolver(self.access, lambda _id: None)
        with self.assertRaisesRegex(PermissionError, "Access denied"):
            resolver.read_operational_timeline(
                "officer-session", 42,
                operational_timeline_reader=lambda _id: self.fail("timeline reader must not run"),
            )
        self.assertEqual(
            self.audit.records[-1].action,
            "bp12.incident.inspect.operational_timeline",
        )
        self.assertFalse(self.audit.records[-1].allowed)

    def test_postgres_operational_timeline_reader_uses_parameterised_read(self):
        class Cursor:
            def __init__(self):
                self.query = None
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def execute(self, query, params): self.query = (query, params)
            def fetchall(self):
                return [(8801, 42, "UNIT_ARRIVED", "2026-11-26T12:00:00Z", 17,
                         "bp10-arrival:ACT-1",
                         {"source_ref": "bp10-arrival:ACT-1", "actor_ref": "officer:12", "authority_ref": "order:5", "unit_ref": "UNIT-7", "assignment_ref": "DEP-4", "field_activity_ref": "ACT-1"})]
        class Connection:
            def __init__(self, cursor): self._cursor = cursor
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def cursor(self): return self._cursor
        cursor = Cursor()
        reader = PostgresIncidentOperationalTimelineReader(lambda: Connection(cursor))
        rows = reader.read(42)
        self.assertEqual(rows[0]["event_id"], 8801)
        self.assertEqual(cursor.query[1], (42,))
        self.assertIn("operational_timeline(%s)", cursor.query[0])

    def test_authorised_timeline_projects_dispatch_and_arrival_for_operational_views(self):
        rows = [
            {
                "event_id": 100, "event_code": "DISPATCH_ACKNOWLEDGED",
                "occurred_at": "2026-11-26T12:00:00Z", "world_tick": 18,
                "source_ref": "bp11-dispatch:CAD-4",
                "attributes": {"dispatch_ref": "CAD-4", "actor_ref": "dispatcher:2",
                               "authority_ref": "dispatch-order:8"},
            },
            {
                "event_id": 104, "event_code": "UNIT_ARRIVED",
                "occurred_at": "2026-11-26T12:03:00Z", "world_tick": 19,
                "source_ref": "bp10-arrival:ACT-7",
                "attributes": {"unit_ref": "UNIT-7", "assignment_ref": "DEP-9",
                               "field_activity_ref": "ACT-7", "actor_ref": "officer:12",
                               "authority_ref": "deployment:9"},
            },
        ]
        view = build_incident_operational_timeline_view(rows)
        self.assertEqual([item["label"] for item in view],
                         ["Dispatch acknowledged", "Unit arrived"])
        self.assertEqual(view[0]["references"], {"dispatch_ref": "CAD-4"})
        self.assertEqual(view[1]["references"]["unit_ref"], "UNIT-7")
        self.assertEqual(view[1]["source_ref"], "bp10-arrival:ACT-7")

    def test_operational_timeline_projection_rejects_out_of_order_events(self):
        rows = [
            {"event_id": 9, "event_code": "DISPATCH_ACKNOWLEDGED",
             "occurred_at": "2026-11-26T12:00:00Z", "world_tick": 20,
             "source_ref": "bp11:9",
             "attributes": {"dispatch_ref": "CAD-9"}},
            {"event_id": 8, "event_code": "DISPATCH_ACKNOWLEDGED",
             "occurred_at": "2026-11-26T11:59:00Z", "world_tick": 19,
             "source_ref": "bp11:8",
             "attributes": {"dispatch_ref": "CAD-8"}},
        ]
        with self.assertRaisesRegex(ValueError, "canonical event order"):
            build_incident_operational_timeline_view(rows)

    def test_command_handover_reconciles_assignment_arrival_and_open_discrepancies(self):
        result = reconcile_incident_command_handover(
            42, incident_status="ACTIVE_MANAGEMENT",
            snapshot_source_ref="bp08-assignment-snapshot:88",
            as_of_world_tick=25,
            assignment_snapshot=[
                {"assignment_ref": "DEP-1", "unit_ref": "UNIT-1",
                 "status": "ON_SCENE", "source_ref": "bp08:DEP-1"},
                {"assignment_ref": "DEP-2", "unit_ref": "UNIT-2",
                 "status": "EN_ROUTE", "source_ref": "bp08:DEP-2"},
                {"assignment_ref": "DEP-3", "unit_ref": "UNIT-3",
                 "status": "COMPLETED", "source_ref": "bp08:DEP-3"},
            ],
            timeline_rows=[
                {"incident_id": 42, "event_code": "UNIT_ARRIVED",
                 "event_id": 700, "world_tick": 20,
                 "source_ref": "bp10:ACT-1",
                 "attributes": {"assignment_ref": "DEP-1", "unit_ref": "UNIT-1"}},
                {"incident_id": 42, "event_code": "UNIT_ARRIVED",
                 "event_id": 701, "world_tick": 21,
                 "source_ref": "bp10:ACT-2",
                 "attributes": {"assignment_ref": "DEP-99", "unit_ref": "UNIT-99"}},
            ],
        )
        self.assertEqual(result["unresolved_assignment_refs"], ["DEP-2"])
        self.assertEqual(
            [d["type"] for d in result["discrepancies"]],
            ["ARRIVAL_WITHOUT_CURRENT_ASSIGNMENT"],
        )
        self.assertFalse(result["handover_ready"])
        self.assertTrue(result["read_only"])

    def test_command_handover_detects_assignment_unit_mismatch(self):
        result = reconcile_incident_command_handover(
            42, incident_status="RECEIVED",
            snapshot_source_ref="bp08:snapshot:4", as_of_world_tick=12,
            assignment_snapshot=[
                {"assignment_ref": "DEP-4", "unit_ref": "UNIT-4",
                 "status": "ON_SCENE", "source_ref": "bp08:DEP-4"},
            ],
            timeline_rows=[
                {"incident_id": 42, "event_code": "UNIT_ARRIVED",
                 "event_id": 702, "world_tick": 11, "source_ref": "bp10:ACT-4",
                 "attributes": {"assignment_ref": "DEP-4", "unit_ref": "UNIT-OTHER"}},
            ],
        )
        self.assertEqual(
            [d["type"] for d in result["discrepancies"]],
            ["ARRIVAL_UNIT_MISMATCH"],
        )
        self.assertFalse(result["handover_ready"])

    def test_command_handover_flags_active_assignment_on_closed_incident(self):
        result = reconcile_incident_command_handover(
            42, incident_status="CLOSED", snapshot_source_ref="bp08:snapshot:6",
            as_of_world_tick=40,
            assignment_snapshot=[
                {"assignment_ref": "DEP-6", "unit_ref": "UNIT-6",
                 "status": "ON_SCENE", "source_ref": "bp08:DEP-6"},
            ],
            timeline_rows=[
                {"incident_id": 42, "event_code": "UNIT_ARRIVED",
                 "event_id": 706, "world_tick": 30, "source_ref": "bp10:ACT-6",
                 "attributes": {"assignment_ref": "DEP-6", "unit_ref": "UNIT-6"}},
            ],
        )
        self.assertEqual(
            [d["type"] for d in result["discrepancies"]],
            ["ACTIVE_ASSIGNMENT_ON_TERMINAL_INCIDENT"],
        )
        self.assertFalse(result["handover_ready"])

    def test_command_handover_rejects_duplicate_assignment_snapshot_rows(self):
        assignment = {"assignment_ref": "DEP-5", "unit_ref": "UNIT-5",
                      "status": "ASSIGNED", "source_ref": "bp08:DEP-5"}
        with self.assertRaisesRegex(ValueError, "duplicate assignment"):
            reconcile_incident_command_handover(
                42, incident_status="RECEIVED", snapshot_source_ref="bp08:snapshot:5",
                as_of_world_tick=1, assignment_snapshot=[assignment, assignment],
                timeline_rows=[],
            )

    def test_resource_scoped_inspection_is_not_broader_than_grant(self):
        with self.assertRaises(PermissionError):
            self.access.inspect("officer-session", "property", "SWPROP-1")
        self.assertEqual(self.audit.records[-1].reason, "no_matching_grant")


if __name__ == "__main__":
    unittest.main()
