"""BP40-02 canonical player command catalogue and typed parser tests."""
import unittest
from dataclasses import FrozenInstanceError

from runtime.player_commands import (
    COMMAND_BY_TOKEN,
    COMMAND_CATALOGUE,
    COMMAND_IDS,
    CommandClass,
    CommandParseResult,
    ParseErrorCode,
    parse_player_command,
    render_command_help,
)


class PlayerCommandCatalogueTests(unittest.TestCase):
    def test_all_existing_commands_are_registered_once_with_stable_metadata(self):
        expected = {
            "help", "status", "profile", "recruit", "career", "start",
            "pause", "resume", "quit", "home", "workspaces", "workspace",
            "back", "where", "find", "inspect", "dispatch", "bingo",
        }
        self.assertEqual(set(COMMAND_BY_TOKEN), expected)
        self.assertEqual(len(COMMAND_CATALOGUE), len(expected))
        self.assertEqual(len(COMMAND_IDS), len(expected))
        for item in COMMAND_CATALOGUE:
            self.assertTrue(item.command_id.startswith("player."))
            self.assertTrue(item.owner)
            expected_action = "reveal_hidden_truth" if item.token == "bingo" else f"player.command.{item.token}"
            self.assertEqual(item.permission_action, expected_action)
            self.assertTrue(item.argument_grammar)
            self.assertIsInstance(item.classification, CommandClass)
            self.assertFalse(item.may_advance_time)

    def test_catalogue_and_parse_result_are_immutable(self):
        with self.assertRaises(TypeError):
            COMMAND_BY_TOKEN["new-command"] = COMMAND_BY_TOKEN["help"]
        parsed = parse_player_command("help")
        with self.assertRaises(FrozenInstanceError):
            parsed.command = None
        with self.assertRaises(ValueError):
            CommandParseResult()

    def test_catalogue_order_and_ids_are_deterministic(self):
        first = [(x.token, x.command_id) for x in COMMAND_CATALOGUE]
        second = [(x.token, x.command_id) for x in COMMAND_CATALOGUE]
        self.assertEqual(first, second)
        self.assertEqual(first[0], ("help", "player.help.v1"))
        self.assertEqual(first[-1], ("dispatch", "player.dispatch.v1"))

    def test_classification_distinguishes_all_reads_navigation_and_mutations(self):
        expected = {
            CommandClass.READ_ONLY: {"help", "status", "profile", "career", "workspaces", "where", "find", "inspect", "bingo"},
            CommandClass.PRESENTATION_STATE: {"home", "workspace", "back"},
            CommandClass.DOMAIN_MUTATION: {"recruit", "start", "pause", "resume", "quit", "dispatch"},
        }
        for classification, tokens in expected.items():
            actual = {
                item.token for item in COMMAND_CATALOGUE
                if item.classification == classification
            }
            self.assertEqual(actual, tokens)
        self.assertTrue(all(not item.may_advance_time for item in COMMAND_CATALOGUE))
        self.assertTrue(all(not item.confirmation_required for item in COMMAND_CATALOGUE))

    def test_international_input_is_preserved_without_guessing(self):
        result = parse_player_command("workspace Łódź")
        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, ParseErrorCode.INVALID_VALUE)
        self.assertIn("Łódź", result.error.message)

    def test_exact_forms_parse_and_preserve_workspace_identifier(self):
        for token in COMMAND_BY_TOKEN:
            if token in {"workspace", "find", "inspect"}:
                continue
            result = parse_player_command(token)
            self.assertTrue(result.ok, token)
            self.assertEqual(result.command.token, token)
        self.assertTrue(parse_player_command("find address Harbour Avenue").ok)
        self.assertEqual(parse_player_command('find business "Harbour Bank"').command.arguments,
                         ("business", "Harbour Bank"))
        self.assertTrue(parse_player_command("inspect property SWPROP-001").ok)
        self.assertTrue(parse_player_command("dispatch").ok)
        self.assertEqual(parse_player_command("dispatch assign SWINC-001").command.arguments,
                         ("assign", "SWINC-001"))
        self.assertEqual(parse_player_command("dispatch arrive SWNPC-DEP-000001").command.arguments,
                         ("arrive", "SWNPC-DEP-000001"))
        self.assertFalse(parse_player_command("dispatch assign").ok)
        self.assertFalse(parse_player_command("dispatch nonsense SWINC-001").ok)
        result = parse_player_command("workspace reports-notifications")
        self.assertTrue(result.ok)
        self.assertEqual(result.command.arguments, ("reports-notifications",))
        self.assertEqual(result.command.original_text, "workspace reports-notifications")

    def test_distinct_typed_parse_errors(self):
        cases = (
            ("", ParseErrorCode.EMPTY_INPUT),
            ('workspace "unterminated', ParseErrorCode.MALFORMED_SYNTAX),
            ("Bingo", ParseErrorCode.UNKNOWN_COMMAND),
            ("workspace", ParseErrorCode.MISSING_ARGUMENT),
            ("workspace cases extra", ParseErrorCode.INVALID_ARGUMENT_COUNT),
            ("status extra", ParseErrorCode.INVALID_ARGUMENT_COUNT),
            ("workspace Cases", ParseErrorCode.INVALID_VALUE),
            ("find", ParseErrorCode.MISSING_ARGUMENT),
            ("find address", ParseErrorCode.MISSING_ARGUMENT),
            ("find person Joshua", ParseErrorCode.INVALID_VALUE),
            ("inspect property", ParseErrorCode.INVALID_ARGUMENT_COUNT),
            ("inspect person P-1", ParseErrorCode.INVALID_VALUE),
        )
        for command, expected in cases:
            with self.subTest(command=command):
                result = parse_player_command(command)
                self.assertFalse(result.ok)
                self.assertEqual(result.error.code, expected)

    def test_no_fuzzy_matching_case_guessing_or_silent_substitution(self):
        for command in ("statuz", "workspac cases", "workspace Cases", "workspace case", "workspace unknown", "Bingo", " bingo", "bingo ", '"bingo"', "not bingo"):
            self.assertFalse(parse_player_command(command).ok, command)
        parsed = parse_player_command("workspace cases")
        self.assertEqual(parsed.command.arguments[0], "cases")

    def test_help_is_generated_from_catalogue_and_only_catalogue_commands(self):
        help_text = render_command_help()
        for item in COMMAND_CATALOGUE:
            if item.token == "bingo":
                self.assertNotIn(item.token, help_text)
                continue
            self.assertIn(item.token, help_text)
            self.assertIn(item.purpose, help_text)
        self.assertNotIn("bingo", help_text)
        self.assertTrue(parse_player_command("bingo").ok)
        self.assertIn("workspace <id>", help_text)
        self.assertIn("find <type> <query>", help_text)
        self.assertIn("inspect <type> <id>", help_text)

    def test_tool_boundary_can_require_exact_canonical_surface(self):
        self.assertTrue(parse_player_command(
            "workspace cases", require_canonical_token=True,
            require_canonical_spacing=True,
        ).ok)
        for command in ("PROFILE", " profile", "profile ", "workspace  cases", 'workspace "cases"'):
            self.assertFalse(parse_player_command(
                command, require_canonical_token=True,
                require_canonical_spacing=True,
            ).ok)


if __name__ == "__main__":
    unittest.main()
