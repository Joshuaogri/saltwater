"""PKG-007 ChatGPT tool handler contract tests."""
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from runtime.chatgpt_tool_handler import handle_player_command
from runtime.player_host_adapter import HostCommandResponse, TrustedHostContext


class ChatGPTToolHandlerTests(unittest.TestCase):
    def setUp(self):
        self.context = TrustedHostContext(
            "opaque-host-session",
            datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.adapter = Mock()
        self.adapter.execute.return_value = HostCommandResponse(True, "Profile loaded.")

    def call_handler(self, args, context=None):
        return handle_player_command(
            args, self.context if context is None else context, self.adapter
        )

    def test_valid_decoded_and_json_requests_delegate_once_each(self):
        for args in (
            {"command_text": "profile", "request_reference": "req-1"},
            json.dumps({"command_text": "status"}),
        ):
            result = self.call_handler(args)
            self.assertEqual(set(result), {"ok", "message"})
            self.assertIs(result["ok"], True)
            self.assertEqual(result["message"], "Profile loaded.")
        self.assertEqual(self.adapter.execute.call_count, 2)

    def test_unknown_fields_missing_fields_and_bad_json_fail_before_adapter(self):
        invalid = (
            {"command_text": "profile", "credential": "forged"},
            {"command_text": "profile", "player_id": "forged"},
            {"credential": "forged"},
            {},
            '{"command_text":',
            "[]",
            [],
            None,
        )
        for args in invalid:
            result = self.call_handler(args)
            self.assertFalse(result["ok"])
            self.assertEqual(result["message"], "Invalid command request.")
        self.adapter.execute.assert_not_called()

    def test_only_exact_single_command_allowlist_is_accepted(self):
        for command in (
            "", " profile", "profile ", "PROFILE", "profile quit",
            "profile;quit", "Bingo", " bingo", "bingo ", '"bingo"', "not bingo", "start now", "SELECT",
        ):
            self.assertFalse(self.call_handler({"command_text": command})["ok"])
        self.adapter.execute.assert_not_called()

    def test_exact_bingo_command_is_allowed_and_forwarded(self):
        result = self.call_handler({"command_text": "bingo"})
        self.assertTrue(result["ok"])
        self.adapter.execute.assert_called_once()
        self.assertEqual(self.adapter.execute.call_args.args[1].command_text, "bingo")

    def test_exact_workspace_navigation_arguments_are_allowed(self):
        result = self.call_handler({"command_text": "workspace reports-notifications"})
        self.assertTrue(result["ok"])
        self.adapter.execute.assert_called_once()
        for command in ("workspace", "workspace cases extra", "workspace Cases", "workspace unknown", "workspace;quit"):
            self.assertFalse(self.call_handler({"command_text": command})["ok"])


    def test_property_and_business_lookup_commands_are_allowed_with_bounded_search_text(self):
        command = "find business Harbour Bank Global Headquarters"
        result = self.call_handler({"command_text": command})
        self.assertTrue(result["ok"])
        self.adapter.execute.assert_called_once()
        forwarded = self.adapter.execute.call_args.args[1]
        self.assertEqual(forwarded.command_text, command)
        self.assertTrue(self.call_handler({
            "command_text": "inspect property SWPROP-000000000001"
        })["ok"])

    def test_lookup_command_length_is_bounded_at_256_characters(self):
        accepted = "find address " + ("A" * 240)
        rejected = "find address " + ("A" * 250)
        self.assertTrue(self.call_handler({"command_text": accepted})["ok"])
        self.assertFalse(self.call_handler({"command_text": rejected})["ok"])

    def test_request_reference_boundaries_and_type(self):
        self.assertTrue(self.call_handler({
            "command_text": "help", "request_reference": "x" * 128
        })["ok"])
        self.assertFalse(self.call_handler({
            "command_text": "help", "request_reference": "x" * 129
        })["ok"])
        self.assertFalse(self.call_handler({
            "command_text": "help", "request_reference": 123
        })["ok"])
        self.assertFalse(self.call_handler({
            "command_text": "help", "request_reference": " "
        })["ok"])

    def test_missing_forged_wrong_type_and_expired_context_fail_before_adapter(self):
        expired = TrustedHostContext(
            "expired", datetime.now(timezone.utc) - timedelta(seconds=1)
        )
        for context in (None, {"host_session_ref": "forged"}, expired):
            result = handle_player_command(
                {"command_text": "profile"}, context, self.adapter
            )
            self.assertEqual(result, {"ok": False, "message": "Access denied."})
        self.adapter.execute.assert_not_called()

    def test_context_is_not_read_from_model_arguments(self):
        result = self.call_handler({
            "command_text": "profile",
            "trusted_context": self.context,
            "host_session_ref": self.context.host_session_ref,
        })
        self.assertFalse(result["ok"])
        self.adapter.execute.assert_not_called()

    def test_adapter_denial_is_returned_without_changing_authority(self):
        self.adapter.execute.return_value = HostCommandResponse(False, "Access denied.")
        result = self.call_handler({"command_text": "start"})
        self.assertEqual(result, {"ok": False, "message": "Access denied."})
        self.adapter.execute.assert_called_once()

    def test_host_reference_and_malformed_adapter_response_are_not_exposed(self):
        self.adapter.execute.return_value = HostCommandResponse(
            True, f"Unexpected {self.context.host_session_ref}"
        )
        result = self.call_handler({"command_text": "profile"})
        self.assertEqual(result, {"ok": False, "message": "Command unavailable."})
        self.adapter.execute.return_value = {"ok": True, "message": "unsafe"}
        result = self.call_handler({"command_text": "profile"})
        self.assertEqual(result, {"ok": False, "message": "Command unavailable."})

    def test_adapter_exception_is_generic(self):
        self.adapter.execute.side_effect = RuntimeError(
            "secret=host-session SQL internal stack"
        )
        result = self.call_handler({"command_text": "profile"})
        self.assertEqual(result, {"ok": False, "message": "Command unavailable."})
        self.assertNotIn("secret", result["message"])
        self.assertNotIn("SQL", result["message"])


if __name__ == "__main__":
    unittest.main()
