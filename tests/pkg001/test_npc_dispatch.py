import unittest

from runtime.npc_dispatch import DispatchIncident, NPCDispatchError, NPCDispatchSimulator
from runtime.npc_workforce import NPCWorkforceGenerator


def roster():
    posts = []
    for index in range(1, 25):
        posts.append({
            "post_id": f"POST-{index:03d}",
            "unit_id": "UNIT-PATROL" if index <= 16 else "UNIT-TRAFFIC",
            "position_title": (
                "Police Sergeant" if index in {1, 17}
                else "Patrol Officer" if index <= 16
                else "Traffic Officer"
            ),
        })
    return NPCWorkforceGenerator(seed=5).generate(posts)


def simulator():
    return NPCDispatchSimulator(
        roster(),
        [
            {"unit_id": "UNIT-PATROL", "functional_domain": "general_patrol",
             "minimum_crew_size": 2, "target_crew_size": 3},
            {"unit_id": "UNIT-TRAFFIC", "functional_domain": "traffic",
             "minimum_crew_size": 2, "target_crew_size": 2},
        ],
        current_shift="Alpha",
    )


class NPCDispatchSimulatorTests(unittest.TestCase):
    def test_dispatcher_selects_unit_and_creates_crew_without_personnel_ids(self):
        engine = simulator()
        deployment = engine.assign_best_unit(
            DispatchIncident("INC-1", "burglary", "general_patrol", 2, "ADDR-1")
        )
        self.assertEqual(deployment.unit_id, "UNIT-PATROL")
        self.assertGreaterEqual(len(deployment.crew_ids), 2)
        self.assertEqual(deployment.status, "responding")
        self.assertIsNotNone(deployment.supervisor_id)

    def test_specialist_unit_preferred_over_general_patrol(self):
        engine = simulator()
        deployment = engine.assign_best_unit(
            DispatchIncident("INC-2", "road collision", "traffic", 2)
        )
        self.assertEqual(deployment.unit_id, "UNIT-TRAFFIC")

    def test_unit_and_crew_become_unavailable_until_returned(self):
        engine = simulator()
        deployment = engine.assign_best_unit(DispatchIncident("INC-3", "theft", "general_patrol"))
        self.assertEqual(engine.snapshot()["assigned_npc_count"], len(deployment.crew_ids))
        self.assertEqual(engine.transition(deployment.deployment_id, "arrive").status, "on_scene")
        self.assertEqual(engine.transition(deployment.deployment_id, "begin_work").status, "busy")
        self.assertEqual(engine.transition(deployment.deployment_id, "finish_work").status, "on_scene")
        self.assertEqual(engine.transition(deployment.deployment_id, "clear_scene").status, "returning")
        self.assertEqual(engine.transition(deployment.deployment_id, "available").status, "available")
        self.assertEqual(engine.snapshot()["assigned_npc_count"], 0)

    def test_same_incident_replays_same_deployment(self):
        engine = simulator()
        incident = DispatchIncident("INC-4", "assault")
        first = engine.assign_best_unit(incident)
        self.assertEqual(first, engine.assign_best_unit(incident))

    def test_no_eligible_crew_returns_playable_dispatch_message(self):
        engine = NPCDispatchSimulator(
            roster(), [{"unit_id": "UNIT-PATROL", "functional_domain": "general_patrol",
                        "minimum_crew_size": 99}], current_shift="Alpha"
        )
        with self.assertRaisesRegex(NPCDispatchError, "No available NPC unit"):
            engine.assign_best_unit(DispatchIncident("INC-5", "incident"))

    def test_shift_rotation_cycles_four_groups(self):
        engine = simulator()
        self.assertEqual(engine.rotate_shift(), "Bravo")
        self.assertEqual(engine.rotate_shift(), "Charlie")
        self.assertEqual(engine.rotate_shift(), "Delta")
        self.assertEqual(engine.rotate_shift(), "Alpha")

    def test_dispatch_lifecycle_rejects_invalid_transition(self):
        engine = simulator()
        deployment = engine.assign_best_unit(DispatchIncident("INC-6", "incident"))
        with self.assertRaises(NPCDispatchError):
            engine.transition(deployment.deployment_id, "finish_work")


if __name__ == "__main__":
    unittest.main()
