"""Deterministic single-player NPC workforce generation for Saltwater.

NPCs are world actors, not player accounts. This module creates an in-memory
roster from the existing authorised-post catalogue; persistence is a separate
adapter so roster generation never writes to Neon implicitly.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import random
from typing import Iterable
from uuid import NAMESPACE_URL, uuid5


_GIVEN_NAMES = (
    "Avery", "Amara", "Anika", "Aria", "Beatrice", "Caleb", "Callum", "Chloe",
    "Daniel", "Darius", "Eleanor", "Elijah", "Elliot", "Esme", "Felix", "Freya",
    "Gabriel", "Hannah", "Harriet", "Isaac", "Imogen", "Iris", "Jamal", "Jasmine",
    "Jonah", "Josephine", "Kieran", "Leah", "Lena", "Lucas", "Maya", "Miriam",
    "Naomi", "Nathan", "Nia", "Noah", "Oliver", "Olivia", "Priya", "Rafael",
    "Rebecca", "Rhea", "Samuel", "Sanaa", "Theo", "Tobias", "Victoria", "Zara",
)
_FAMILY_NAMES = (
    "Abbott", "Adebayo", "Ainsworth", "Akinwale", "Alder", "Bennett", "Bishop",
    "Campbell", "Carter", "Clarke", "Cole", "Dawson", "Ellis", "Fletcher",
    "Ford", "Grant", "Griffin", "Hale", "Hart", "Hayes", "Hughes", "Ibrahim",
    "James", "Khan", "Knight", "Lawson", "Lewis", "Mensah", "Morgan", "Nwosu",
    "Okafor", "Owens", "Patel", "Quinn", "Reed", "Roberts", "Shaw", "Sinclair",
    "Smith", "Taylor", "Thomas", "Walker", "Ward", "Williams", "Wright", "Young",
)
_SHIFT_GROUPS = ("Alpha", "Bravo", "Charlie", "Delta")


@dataclass(frozen=True, slots=True)
class NPCOfficer:
    npc_id: str
    service_number: str
    given_name: str
    family_name: str
    display_name: str
    unit_id: str | None
    post_id: str | None
    position_title: str
    shift_group: str
    actor_kind: str = "npc"
    player_controlled: bool = False
    service_state: str = "active"
    service_standing: str = "established"
    position_type: str = "sworn"


class NPCWorkforceError(ValueError):
    """The NPC workforce could not be generated from the post catalogue."""


class NPCWorkforceGenerator:
    """Create a stable NPC occupant for each supplied authorised post."""

    def __init__(self, *, seed: int = 20261126):
        if type(seed) is not int:
            raise ValueError("seed must be an integer")
        self.seed = seed

    def generate(self, posts: Iterable[dict]) -> tuple[NPCOfficer, ...]:
        rows = list(posts)
        if not rows:
            return ()
        required = {"post_id", "unit_id", "position_title"}
        seen = set()
        normalized = []
        for row in rows:
            if not isinstance(row, dict) or not required.issubset(row):
                raise NPCWorkforceError("Every post requires post_id, unit_id and position_title.")
            values = {key: row[key] for key in required}
            position_type = row.get("position_type", "sworn")
            if any(not isinstance(value, str) or not value.strip() for value in values.values()):
                raise NPCWorkforceError("Post identity, unit and title must be non-empty text.")
            if position_type not in {"sworn", "civilian", "mixed"}:
                raise NPCWorkforceError("position_type must be sworn, civilian or mixed.")
            post_id = values["post_id"].strip()
            if post_id in seen:
                raise NPCWorkforceError(f"Duplicate authorised post: {post_id}")
            seen.add(post_id)
            normalized.append({
                "post_id": post_id,
                "unit_id": values["unit_id"].strip(),
                "position_title": values["position_title"].strip(),
                "position_type": position_type,
            })
        normalized.sort(key=lambda item: item["post_id"])
        name_pool = [
            (given, family)
            for given in _GIVEN_NAMES
            for family in _FAMILY_NAMES
        ]
        if len(normalized) > len(name_pool):
            raise NPCWorkforceError("Name pool is too small for the requested NPC workforce.")
        rng = random.Random(self.seed)
        selected_names = rng.sample(name_pool, len(normalized))
        officers = []
        for index, (post, name) in enumerate(zip(normalized, selected_names), start=1):
            post_id = post["post_id"]
            npc_id = str(uuid5(NAMESPACE_URL, f"saltwater:npc:{self.seed}:{post_id}"))
            shift = _SHIFT_GROUPS[(index - 1) % len(_SHIFT_GROUPS)]
            given, family = name
            officers.append(NPCOfficer(
                npc_id=npc_id,
                service_number=f"SWNPC-{index:06d}",
                given_name=given,
                family_name=family,
                display_name=f"{given} {family}",
                unit_id=post["unit_id"],
                post_id=post_id,
                position_title=post["position_title"],
                shift_group=shift,
                position_type=post["position_type"],
            ))
        return tuple(officers)


    @staticmethod
    def assign_shift_groups(officers: Iterable[NPCOfficer]) -> tuple[NPCOfficer, ...]:
        """Assign existing people to four shifts without creating new identities."""
        rows = sorted(tuple(officers), key=lambda item: (
            item.unit_id or "", item.post_id or "", item.service_number
        ))
        counts: dict[str, int] = {}
        result = []
        for officer in rows:
            group = officer.unit_id or "__unassigned__"
            index = counts.get(group, 0)
            counts[group] = index + 1
            result.append(replace(officer, shift_group=_SHIFT_GROUPS[index % len(_SHIFT_GROUPS)]))
        return tuple(result)

    def generate_shift_roster(self, posts: Iterable[dict]) -> tuple[NPCOfficer, ...]:
        """Assign one distinct NPC per authorised post to one of four shifts.

        The shift groups rotate coverage; they do not multiply the number of
        people represented by an authorised post. This preserves the BP01/BP03
        population ledger: 500 authorised posts yield 500 distinct police NPCs,
        not 2,000 additional people. Within each unit, occupants are distributed
        round-robin across Alpha, Bravo, Charlie and Delta.
        """
        return self.assign_shift_groups(self.generate(posts))

    @staticmethod
    def as_records(officers: Iterable[NPCOfficer]) -> list[dict]:
        return [asdict(officer) for officer in officers]
