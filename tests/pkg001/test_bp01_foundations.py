"""BP01 global canon and hidden-truth trigger contract tests."""
import unittest
from dataclasses import FrozenInstanceError

from runtime.bp01_foundations import (
    FOUNDATIONAL_CANON,
    HIDDEN_TRUTH_REVEAL_COMMAND,
    FoundationalCanon,
    is_exact_hidden_truth_reveal_trigger,
)


class BP01FoundationalCanonTests(unittest.TestCase):
    def test_machine_readable_canon_matches_adopted_saltwater_baseline(self):
        canon = FOUNDATIONAL_CANON
        self.assertEqual(canon.game_name, "Saltwater")
        self.assertEqual(canon.playable_city_count, 1)
        self.assertEqual(canon.sovereign_jurisdiction_count, 1)
        self.assertEqual(canon.population_cap, 10_000)
        self.assertEqual(canon.opening_civilian_population, 9_000)
        self.assertEqual(canon.opening_police_population, 500)
        self.assertEqual(canon.opening_population, 9_500)
        self.assertEqual(canon.opening_headroom, 500)
        self.assertEqual(canon.minimum_distinct_businesses, 10_000)
        self.assertEqual(canon.human_player_count, 1)
        self.assertEqual(canon.universal_naming_standard, "SW-UNS-001")
        self.assertTrue(canon.text_first)
        self.assertFalse(canon.offline_time_advancement)

    def test_canon_is_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            FOUNDATIONAL_CANON.population_cap = 10_001

    def test_inconsistent_canon_cannot_be_constructed(self):
        with self.assertRaises(ValueError):
            FoundationalCanon(opening_population=9_499)
        with self.assertRaises(ValueError):
            FoundationalCanon(playable_city_count=2)
        with self.assertRaises(ValueError):
            FoundationalCanon(offline_time_advancement=True)

    def test_only_exact_standalone_bingo_triggers_reveal(self):
        self.assertEqual(HIDDEN_TRUTH_REVEAL_COMMAND, "bingo")
        self.assertTrue(is_exact_hidden_truth_reveal_trigger("bingo"))
        for value in (
            "Bingo", "BINGO", " bingo", "bingo ", "bingo!", '"bingo"',
            "'bingo'", "not bingo", "bingo please", "bingo\\n", None, 1, True,
        ):
            with self.subTest(value=value):
                self.assertFalse(is_exact_hidden_truth_reveal_trigger(value))


if __name__ == "__main__":
    unittest.main()
