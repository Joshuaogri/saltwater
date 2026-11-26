import unittest

from runtime.npc_workforce import NPCWorkforceError, NPCWorkforceGenerator


def posts(count=500):
    return [
        {
            "post_id": f"SWPS-POST-{i:04d}",
            "unit_id": f"SWPS-UNIT-{(i % 31) + 1:02d}",
            "position_title": "Police Officer" if i % 3 else "Police Sergeant",
        }
        for i in range(1, count + 1)
    ]


class NPCWorkforceGeneratorTests(unittest.TestCase):
    def test_generates_one_npc_per_authorised_post(self):
        roster = NPCWorkforceGenerator().generate(posts())
        self.assertEqual(len(roster), 500)
        self.assertEqual(len({person.npc_id for person in roster}), 500)
        self.assertEqual(len({person.service_number for person in roster}), 500)
        self.assertEqual(len({person.post_id for person in roster}), 500)
        self.assertTrue(all(person.actor_kind == "npc" for person in roster))
        self.assertTrue(all(person.player_controlled is False for person in roster))
        self.assertTrue(all(person.position_type == "sworn" for person in roster))

    def test_shift_roster_assigns_one_person_per_post_across_four_shifts(self):
        source = posts(8)
        for index, row in enumerate(source):
            row["unit_id"] = "UNIT-A" if index < 4 else "UNIT-B"
        roster = NPCWorkforceGenerator(seed=4).generate_shift_roster(source)
        self.assertEqual(len(roster), 8)
        self.assertEqual({person.shift_group for person in roster},
                         {"Alpha", "Bravo", "Charlie", "Delta"})
        self.assertEqual(len({person.post_id for person in roster}), 8)
        self.assertEqual(len({person.npc_id for person in roster}), 8)
        for unit_id in ("UNIT-A", "UNIT-B"):
            unit_roster = [person for person in roster if person.unit_id == unit_id]
            self.assertEqual({person.shift_group for person in unit_roster},
                             {"Alpha", "Bravo", "Charlie", "Delta"})
            self.assertEqual(len(unit_roster), 4)

    def test_generation_is_deterministic_and_seeded(self):
        source = posts(30)
        first = NPCWorkforceGenerator(seed=17).generate(source)
        second = NPCWorkforceGenerator(seed=17).generate(reversed(source))
        other = NPCWorkforceGenerator(seed=18).generate(source)
        self.assertEqual(first, second)
        self.assertNotEqual(first, other)

    def test_roster_covers_source_units_and_post_titles(self):
        source = posts(62)
        roster = NPCWorkforceGenerator().generate(source)
        self.assertEqual({person.unit_id for person in roster},
                         {row["unit_id"] for row in source})
        self.assertEqual({person.position_title for person in roster},
                         {row["position_title"] for row in source})

    def test_duplicate_post_identity_fails(self):
        source = posts(2)
        source[1]["post_id"] = source[0]["post_id"]
        with self.assertRaises(NPCWorkforceError):
            NPCWorkforceGenerator().generate(source)

    def test_incomplete_post_fails(self):
        with self.assertRaises(NPCWorkforceError):
            NPCWorkforceGenerator().generate([{"post_id": "P1", "unit_id": "U1"}])

    def test_position_type_preserves_civilian_and_mixed_roles(self):
        source = [
            {"post_id": "P1", "unit_id": "U1", "position_title": "Dispatcher",
             "position_type": "civilian"},
            {"post_id": "P2", "unit_id": "U1", "position_title": "Training Officer",
             "position_type": "mixed"},
        ]
        roster = NPCWorkforceGenerator().generate(source)
        self.assertEqual([person.position_type for person in roster], ["civilian", "mixed"])

    def test_empty_catalogue_returns_empty_roster(self):
        self.assertEqual(NPCWorkforceGenerator().generate([]), ())


if __name__ == "__main__":
    unittest.main()
