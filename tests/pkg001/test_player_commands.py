"""BP40-02 canonical player command catalogue and typed parser tests."""
import unittest

from runtime.player_commands import (
    COMMAND_BY_TOKEN,
    COMMAND_CATALOGUE,
    COMMAND_IDS,
    CommandClass,
    ParseErrorCode,
    parse_player_command,
    render_command_help,
)


class PlayerCommandCatalogueTests(unittest.TestCase):
    def test_all_existing_commands_are_registered_once_with_stable_metadata(self):
        expected = {
            "help", "status", "profile", "recruit", "career", "start",
            "pause", "resume", "quit", "home", "workspaces", "workspace",
            "back", "where",
        }
        self.assertEqual(set(COMMAND_BY_TOKEN), expected)
        self.assertEqual(len(COMMAND_CATALOGUE), len(expected))
        self.assertEqual(len(COMMAND_IDS), len(expected))
        for item in COMMAND_CATALOGUE:
            self.assertTrue(item.command_id.startswith("player."))
            self.assertTrue(item.owner)
            self.assertEqual(item.permission_action, f"player.command.{item.token}")
            self.assertTrue(item.argument_grammar)
            self.assertIsInstance(item.classification, CommandClass)
            self.assertFalse(item.may_advance_time)

    def test_catalogue_order_and_ids_are_deterministic(self):
        first = [(x.token, x.command_id) for x in COMMAND_CATALOGUE]
        second = [(x.token, x.command_id) for x in COMMAND_CATALOGUE]
        self.assertEqual(first, second)
        self.assertEqual(first[0], ("help", "player.help.v1"))
        self.assertEqual(first[-1], ("where", "player.where.v1"))

    def test_classification_distinguishes_reads_navigation_and_mutations(self):
        self.assertEqual(COMMAND_BY_TOKEN["status"].classification, CommandClass.READ_ONLY)
        self.assertEqual(COMMAND_BY_TOKEN["workspace"].classification, CommandClass.PRESENTATION_STATE)
        self.assertEqual(COMMAND_BY_TOKEN["recruit"].classification, CommandClass.DOMAIN_MUTATION)
        self.assertEqual(COMMAND_BY_TOKEN["start"].classification, CommandClass.DOMAIN_MUTATION)
        self.assertFalse(COMMAND_BY_TOKEN["recruit"].may_advance_time)

    def test_exact_forms_parse_and_preserve_workspace_identifier(self):
        for token in COMMAND_BY_TOKEN:
            if token == "workspace":
                continue
            result = parse_player_command(token)
            self.assertTrue(result.ok, token)
            self.assertEqual(result.command.token, token)
        result = parse_player_command("workspace reports-notifications")
        self.assertTrue(result.ok)
        self.assertEqual(result.command.arguments, ("reports-notifications",))
        self.assertEqual(result.command.original_text, "workspace reports-notifications")

    def test_distinct_typed_parse_errors(self):
        cases = (
            ("", ParseErrorCode.EMPTY_INPUT),
            ('workspace "unterminated', ParseErrorCode.MALFORMED_SYNTAX),
            ("bingo", ParseErrorCode.UNKNOWN_COMMAND),
            ("workspace", ParseErrorCode.MISSING_ARGUMENT),
            ("workspace cases extra", ParseErrorCode.INVALID_ARGUMENT_COUNT),
            ("status extra", ParseErrorCode.INVALID_ARGUMENT_COUNT),
            ("workspace Cases", ParseErrorCode.INVALID_VALUE),
        )
        for command, expected in cases:
            with self.subTest(command=command):
                result = parse_player_command(command)
                self.assertFalse(result.ok)
                self.assertEqual(result.error.code, expected)

    def test_no_fuzzy_matching_case_guessing_or_silent_substitution(self):
        for command in ("statuz", "workspac cases", "workspace Cases", "workspace case", "workspace unknown"):
            self.assertFalse(parse_player_command(command).ok, command)
        parsed = parse_player_command("workspace cases")
        self.assertEqual(parsed.command.arguments[0], "cases")

    def test_help_is_generated_from_catalogue_and_only_catalogue_commands(self):
        help_text = render_command_help()
        for item in COMMAND_CATALOGUE:
            self.assertIn(item.token, help_text)
            self.assertIn(item.purpose, help_text)
        self.assertNotIn("bingo", help_text)
        self.assertIn("workspace <id>", help_text)

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
