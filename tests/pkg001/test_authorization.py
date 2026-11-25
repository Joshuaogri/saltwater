import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from runtime.security import (
    AuthorizationService, Effect, Grant, InMemoryAuditSink,
    PrincipalKind, PrincipalStatus, SessionStatus, VerifiedSession,
)


class FakeVerifier:
    def __init__(self, session):
        self.session = session

    def verify(self, credential):
        return self.session if credential == "opaque-valid-session" else None


class FailingAuditSink:
    def append(self, record):
        raise OSError("audit storage unavailable")


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 23, 12, 0, tzinfo=timezone.utc)
        self.player_id = uuid4()
        self.session = VerifiedSession(
            session_id=uuid4(),
            principal_id=self.player_id,
            principal_kind=PrincipalKind.PLAYER,
            principal_status=PrincipalStatus.ACTIVE,
            session_status=SessionStatus.ACTIVE,
            issued_at=self.now - timedelta(minutes=1),
            expires_at=self.now + timedelta(hours=1),
            roles=frozenset({"player"}),
            policy_version="test-1",
        )
        self.audit = InMemoryAuditSink()
        self.grants = (
            Grant("read_case", "case/*", "active_play", Effect.ALLOW, principal_kind=PrincipalKind.PLAYER),
            Grant("reveal_hidden_truth", "case/*", "player_requested_reveal", Effect.ALLOW, principal_kind=PrincipalKind.PLAYER),
        )
        self.auth = AuthorizationService(FakeVerifier(self.session), self.audit, self.grants, policy_version="test-1")

    def decide(self, **kwargs):
        base = dict(
            action="read_case",
            resource="case/SM-TEST-1",
            purpose="active_play",
            now=self.now,
        )
        base.update(kwargs)
        return self.auth.decide("opaque-valid-session", **base)

    def test_explicit_grant_allows_and_is_audited(self):
        decision = self.decide()
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "explicit_allow")
        self.assertEqual(len(self.audit.records), 1)
        self.assertEqual(self.audit.records[0].principal_id, self.player_id)

    def test_expected_principal_mismatch_is_audited_as_denial(self):
        other_id = uuid4()
        decision = self.auth.decide(
            "opaque-valid-session",
            action="read_case",
            resource="case/SM-TEST-1",
            purpose="active_play",
            now=self.now,
            expected_principal_id=other_id,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "principal_mismatch")
        self.assertEqual(self.audit.records[-1].principal_id, self.player_id)
        self.assertFalse(self.audit.records[-1].allowed)
        self.assertEqual(self.audit.records[-1].reason, "principal_mismatch")


    def test_expected_principal_kind_is_enforced_and_audited(self):
        decision = self.auth.decide(
            "opaque-valid-session",
            action="read_case",
            resource="case/SM-TEST-1",
            purpose="active_play",
            now=self.now,
            expected_principal_kind=PrincipalKind.OFFICER,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "principal_kind_mismatch")
        self.assertFalse(self.audit.records[-1].allowed)
        self.assertEqual(self.audit.records[-1].reason, "principal_kind_mismatch")

    def test_default_deny(self):
        decision = self.decide(action="export_case")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "no_matching_grant")

    def test_explicit_deny_overrides_allow(self):
        grants = self.grants + (
            Grant("read_case", "case/SM-TEST-1", "active_play", Effect.DENY, principal_id=self.player_id),
        )
        auth = AuthorizationService(FakeVerifier(self.session), self.audit, grants)
        decision = auth.decide(
            "opaque-valid-session", action="read_case", resource="case/SM-TEST-1",
            purpose="active_play", now=self.now,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "explicit_deny")

    def test_expired_and_revoked_sessions_are_denied(self):
        expired = VerifiedSession(**{
            **{name: getattr(self.session, name) for name in self.session.__dataclass_fields__},
            "expires_at": self.now,
        })
        auth = AuthorizationService(FakeVerifier(expired), self.audit, self.grants)
        self.assertFalse(auth.decide(
            "opaque-valid-session", action="read_case", resource="case/SM-TEST-1",
            purpose="active_play", now=self.now,
        ).allowed)
        revoked = VerifiedSession(**{
            **{name: getattr(self.session, name) for name in self.session.__dataclass_fields__},
            "session_status": SessionStatus.REVOKED,
        })
        auth = AuthorizationService(FakeVerifier(revoked), self.audit, self.grants)
        self.assertFalse(auth.decide(
            "opaque-valid-session", action="read_case", resource="case/SM-TEST-1",
            purpose="active_play", now=self.now,
        ).allowed)

    def test_hidden_truth_requires_exact_standalone_trigger_and_player(self):
        base = dict(
            action="reveal_hidden_truth",
            resource="case/SM-TEST-1",
            purpose="player_requested_reveal",
            now=self.now,
        )
        for trigger in ("Bingo", " bingo", "bingo ", "bingo!", "not bingo", None):
            self.assertFalse(self.auth.decide(
                "opaque-valid-session", reveal_trigger=trigger, **base
            ).allowed, trigger)
        self.assertTrue(self.auth.decide(
            "opaque-valid-session", reveal_trigger="bingo", **base
        ).allowed)

    def test_non_player_cannot_reveal_hidden_truth(self):
        service_session = VerifiedSession(**{
            **{name: getattr(self.session, name) for name in self.session.__dataclass_fields__},
            "principal_kind": PrincipalKind.SERVICE,
        })
        auth = AuthorizationService(FakeVerifier(service_session), self.audit, self.grants)
        decision = auth.decide(
            "opaque-valid-session", action="reveal_hidden_truth", resource="case/SM-TEST-1",
            purpose="player_requested_reveal", now=self.now, reveal_trigger="bingo",
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "hidden_truth_requires_exact_player_trigger")

    def test_invalid_session_and_audit_failure_fail_closed(self):
        self.assertFalse(self.auth.decide(
            "not-valid", action="read_case", resource="case/SM-TEST-1",
            purpose="active_play", now=self.now,
        ).allowed)
        failing = AuthorizationService(FakeVerifier(self.session), FailingAuditSink(), self.grants)
        decision = failing.decide(
            "opaque-valid-session", action="reveal_hidden_truth", resource="case/SM-TEST-1",
            purpose="player_requested_reveal", now=self.now, reveal_trigger="bingo",
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "audit_unavailable")


if __name__ == "__main__":
    unittest.main()
