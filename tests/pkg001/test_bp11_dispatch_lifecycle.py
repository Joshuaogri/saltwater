import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.bp11_dispatch_lifecycle import (
    DispatchLifecycleError, PostgresDispatchLifecycle,
)
from runtime.security import (
    AuthorizationService, Effect, Grant, InMemoryAuditSink, PrincipalKind,
    PrincipalStatus, SessionStatus, VerifiedSession,
)


class Verifier:
    def __init__(self, session):
        self.session = session

    def verify(self, credential):
        return self.session if credential == "dispatcher-session" else None


class DeploymentPort:
    def __init__(self, status="issued"):
        self.status = status
        self.commands = []

    def get_deployment(self, deployment_id):
        return {"deployment_id": deployment_id, "status": self.status}

    def transition_deployment(self, **command):
        self.commands.append(command)
        self.status = command["resulting_status"]
        return {"deployment_id": command["deployment_id"], "status": self.status}


def make_service(port, *, grants=None, principal_kind=PrincipalKind.OFFICER):
    now = datetime.now(timezone.utc)
    principal_id = uuid4()
    session = VerifiedSession(
        session_id=uuid4(), principal_id=principal_id,
        principal_kind=principal_kind, principal_status=PrincipalStatus.ACTIVE,
        session_status=SessionStatus.ACTIVE, issued_at=now-timedelta(minutes=1),
        expires_at=now+timedelta(hours=1), active_person_id=19,
        roles=frozenset({"dispatcher"}),
    )
    actions = ("issue", "acknowledge", "refuse", "cancel", "reassign",
               "mobilise", "start", "complete", "stand_down")
    allowed = [
        Grant(f"bp11.dispatch.{action}", "dispatch-deployment:*",
              "police_workflow", Effect.ALLOW, principal_kind=PrincipalKind.OFFICER)
        for action in actions
    ]
    audit = InMemoryAuditSink()
    auth = AuthorizationService(Verifier(session), audit, allowed if grants is None else grants)
    service = PostgresDispatchLifecycle(auth, principal_id, port)
    return service, audit


class BP11DispatchLifecycleTests(unittest.TestCase):
    def invoke(self, service, command, status, tick=42):
        return service.transition(
            "dispatcher-session", uuid4(), command=command,
            expected_status=status, reason="Dispatcher operational decision",
            source_ref="CAD:CALL-1001", idempotency_key=f"dispatch-{command}-{tick}",
            effective_tick=tick,
        )

    def test_issue_transitions_authorised_deployment_to_issued(self):
        port = DeploymentPort(status="authorised")
        service, audit = make_service(port)
        result = self.invoke(service, "issue", "authorised")
        self.assertEqual(result["status"], "issued")
        self.assertEqual(port.commands[0]["event_kind"], "issued")
        self.assertEqual(port.commands[0]["effective_tick"], 42)
        self.assertTrue(audit.records[-1].allowed)

    def test_acknowledgement_and_refusal_are_explicit_outcomes(self):
        for command, expected in (("acknowledge", "acknowledged"), ("refuse", "rejected")):
            with self.subTest(command=command):
                port = DeploymentPort(status="issued")
                service, _ = make_service(port)
                self.assertEqual(self.invoke(service, command, "issued")["status"], expected)

    def test_cancel_and_reassignment_use_bp08_statuses(self):
        for command, expected in (("cancel", "cancelled"), ("reassign", "reassigned")):
            with self.subTest(command=command):
                port = DeploymentPort(status="acknowledged")
                service, _ = make_service(port)
                self.assertEqual(self.invoke(service, command, "acknowledged")["status"], expected)

    def test_mobilisation_start_completion_and_stand_down(self):
        cases = (("mobilise", "acknowledged", "mobilising"),
                 ("start", "mobilising", "active"),
                 ("complete", "active", "completed"),
                 ("stand_down", "active", "stood_down"))
        for command, current, expected in cases:
            with self.subTest(command=command):
                port = DeploymentPort(status=current)
                service, _ = make_service(port)
                self.assertEqual(self.invoke(service, command, current)["status"], expected)

    def test_stale_status_rejected_before_write(self):
        port = DeploymentPort(status="active")
        service, _ = make_service(port)
        with self.assertRaises(DispatchLifecycleError):
            self.invoke(service, "acknowledge", "issued")
        self.assertEqual(port.commands, [])

    def test_invalid_transition_rejected(self):
        port = DeploymentPort(status="proposed")
        service, _ = make_service(port)
        with self.assertRaises(DispatchLifecycleError):
            self.invoke(service, "start", "proposed")
        self.assertEqual(port.commands, [])

    def test_default_deny_prevents_deployment_access(self):
        port = DeploymentPort()
        service, audit = make_service(port, grants=())
        with self.assertRaises(PermissionError):
            self.invoke(service, "acknowledge", "issued")
        self.assertEqual(port.commands, [])
        self.assertFalse(audit.records[-1].allowed)

    def test_player_principal_cannot_dispatch(self):
        port = DeploymentPort()
        service, audit = make_service(port, principal_kind=PrincipalKind.PLAYER)
        with self.assertRaises(PermissionError):
            self.invoke(service, "acknowledge", "issued")
        self.assertEqual(port.commands, [])
        self.assertEqual(audit.records[-1].reason, "principal_kind_mismatch")

    def test_missing_deployment_rejected(self):
        class MissingPort(DeploymentPort):
            def get_deployment(self, deployment_id):
                return None
        service, _ = make_service(MissingPort())
        with self.assertRaises(LookupError):
            self.invoke(service, "acknowledge", "issued")

    def test_invalid_tick_rejected_before_access(self):
        port = DeploymentPort()
        service, _ = make_service(port)
        with self.assertRaises(ValueError):
            service.transition(
                "dispatcher-session", uuid4(), command="acknowledge",
                expected_status="issued", reason="Acknowledged",
                source_ref="CAD:CALL-1009", idempotency_key="dispatch-bad-tick",
                effective_tick=True,
            )
        self.assertEqual(port.commands, [])


if __name__ == "__main__":
    unittest.main()
