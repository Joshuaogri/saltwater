"""PKG-006 trusted host adapter tests."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from runtime.player_host_adapter import (
    HostCommandRequest,
    TrustedHostContext,
    TrustedPlayerHostAdapter,
)


class FakeCredentialProvider:
    def __init__(self, credential="opaque-game-session"):
        self.credential = credential
        self.contexts = []

    def resolve(self, context):
        self.contexts.append(context)
        return self.credential


class TrustedPlayerHostAdapterTests(unittest.TestCase):
    def setUp(self):
        self.context = TrustedHostContext(
            "host-session-reference",
            datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        self.provider = FakeCredentialProvider()
        self.runtime = Mock()
        self.runtime.execute.return_value = type(
            "Result", (), {"ok": True, "message": "Profile loaded."}
        )()
        self.adapter = TrustedPlayerHostAdapter(self.provider, self.runtime)

    def test_forwards_only_credential_and_single_command_to_pkg005(self):
        response = self.adapter.execute(
            self.context, HostCommandRequest("profile", "req-001")
        )
        self.assertTrue(response.ok)
        self.assertEqual(response.message, "Profile loaded.")
        self.assertEqual(self.provider.contexts, [self.context])
        self.runtime.execute.assert_called_once_with(
            "opaque-game-session", "profile"
        )

    def test_absent_wrong_type_and_expired_context_fail_before_provider(self):
        request = HostCommandRequest("profile")
        for context in (None, {"host_session_ref": "forged"}):
            self.assertFalse(self.adapter.execute(context, request).ok)
        expired = TrustedHostContext(
            "expired", datetime.now(timezone.utc) - timedelta(seconds=1)
        )
        self.assertFalse(self.adapter.execute(expired, request).ok)
        self.assertEqual(self.provider.contexts, [])
        self.runtime.execute.assert_not_called()

    def test_missing_credential_fails_closed(self):
        adapter = TrustedPlayerHostAdapter(FakeCredentialProvider(None), self.runtime)
        response = adapter.execute(self.context, HostCommandRequest("profile"))
        self.assertFalse(response.ok)
        self.assertEqual(response.message, "Access denied.")
        self.runtime.execute.assert_not_called()

    def test_multi_command_arguments_and_unknown_commands_rejected(self):
        for command in ("profile;quit", "profile quit", "profile extra", "Bingo", " bingo", "bingo ", '"bingo"', "not bingo", ""):
            response = self.adapter.execute(self.context, HostCommandRequest(command))
            self.assertFalse(response.ok)
        self.assertEqual(self.provider.contexts, [])
        self.runtime.execute.assert_not_called()

    def test_exact_bingo_command_is_forwarded_to_authenticated_runtime(self):
        response = self.adapter.execute(self.context, HostCommandRequest("bingo"))
        self.assertTrue(response.ok)
        self.runtime.execute.assert_called_once_with("opaque-game-session", "bingo")

    def test_workspace_navigation_command_is_forwarded_but_other_arguments_fail(self):
        response = self.adapter.execute(self.context, HostCommandRequest("workspace evidence-scenes"))
        self.assertTrue(response.ok)
        self.runtime.execute.assert_called_once_with("opaque-game-session", "workspace evidence-scenes")
        for command in ("workspace", "workspace cases extra", "workspace Cases", "workspace unknown", "workspace;quit"):
            self.assertFalse(self.adapter.execute(self.context, HostCommandRequest(command)).ok)

    def test_raw_credential_never_appears_in_response(self):
        self.runtime.execute.return_value = type(
            "Result", (), {
                "ok": True, "message": "unexpected opaque-game-session leak"
            }
        )()
        response = self.adapter.execute(self.context, HostCommandRequest("profile"))
        self.assertFalse(response.ok)
        self.assertNotIn("opaque-game-session", response.message)

    def test_provider_and_runtime_exceptions_are_generic(self):
        provider = Mock()
        provider.resolve.side_effect = RuntimeError("secret=opaque-game-session")
        adapter = TrustedPlayerHostAdapter(provider, self.runtime)
        response = adapter.execute(self.context, HostCommandRequest("profile"))
        self.assertFalse(response.ok)
        self.assertNotIn("opaque-game-session", response.message)

        provider.resolve.side_effect = None
        provider.resolve.return_value = "opaque-game-session"
        self.runtime.execute.side_effect = RuntimeError(
            "credential opaque-game-session internal SQL detail"
        )
        response = adapter.execute(self.context, HostCommandRequest("profile"))
        self.assertFalse(response.ok)
        self.assertEqual(response.message, "Command unavailable.")
        self.assertNotIn("opaque-game-session", response.message)
        self.assertNotIn("SQL", response.message)

    def test_model_request_cannot_carry_identity_or_credential_fields(self):
        with self.assertRaises(TypeError):
            HostCommandRequest("profile", principal_id="forged", credential="forged")
        with self.assertRaises(ValueError):
            HostCommandRequest("profile", "x" * 129)

    def test_constructor_rejects_naive_expiry(self):
        with self.assertRaises(ValueError):
            TrustedHostContext("host-ref", datetime(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
