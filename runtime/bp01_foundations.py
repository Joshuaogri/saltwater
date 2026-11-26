"""BP01 machine-readable global canon and reveal-trigger contract.

Domain-specific enforcement remains with the owning BP divisions. This module
provides the shared immutable values and exact global trigger semantics.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FoundationalCanon:
    game_name: str = "Saltwater"
    playable_city_count: int = 1
    sovereign_jurisdiction_count: int = 1
    population_cap: int = 10_000
    opening_civilian_population: int = 9_000
    opening_police_population: int = 500
    opening_population: int = 9_500
    opening_headroom: int = 500
    minimum_distinct_businesses: int = 10_000
    human_player_count: int = 1
    universal_naming_standard: str = "SW-UNS-001"
    text_first: bool = True
    offline_time_advancement: bool = False

    def __post_init__(self) -> None:
        if self.playable_city_count != 1 or self.sovereign_jurisdiction_count != 1:
            raise ValueError("Saltwater has exactly one playable city and jurisdiction")
        if self.opening_civilian_population + self.opening_police_population != self.opening_population:
            raise ValueError("opening population cohorts do not reconcile")
        if self.opening_population + self.opening_headroom != self.population_cap:
            raise ValueError("opening population and headroom do not reconcile")
        if self.population_cap != 10_000 or self.minimum_distinct_businesses < 10_000:
            raise ValueError("foundational Saltwater population/business limits changed")
        if self.human_player_count != 1 or not self.text_first or self.offline_time_advancement:
            raise ValueError("foundational single-player/time/interface rules changed")
        if self.universal_naming_standard != "SW-UNS-001":
            raise ValueError("SW-UNS-001 is the mandatory universal naming authority")


FOUNDATIONAL_CANON = FoundationalCanon()
HIDDEN_TRUTH_REVEAL_COMMAND = "bingo"


def is_exact_hidden_truth_reveal_trigger(command_text: object) -> bool:
    """Return true only for the exact, standalone, lowercase reveal command."""
    return type(command_text) is str and command_text == HIDDEN_TRUTH_REVEAL_COMMAND
