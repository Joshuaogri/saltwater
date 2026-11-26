import unittest

from runtime.kernel import InMemoryRuntimeStore, Lifecycle, RuntimeKernel
from runtime.scheduling import InMemoryScheduleStore, TickScheduler
from runtime.npc_dispatch_scheduler import register_npc_dispatch_schedule
from runtime.npc_dispatch import DispatchIncident, NPCDispatchSimulator
from runtime.npc_dispatch_console import NPCDispatchConsole
from runtime.npc_workforce import NPCWorkforceGenerator
from runtime.player_interface import PlayerCommandInterface, PlayerProfile


def build_console():
    posts = [
        {"post_id": f"P-{i:03d}", "unit_id": "UNIT-PATROL",
         "position_title": "Police Sergeant" if i == 1 else "Patrol Officer"}
        for i in range(1, 17)
    ]
    officers = NPCWorkforceGenerator(seed=10).generate_shift_roster(posts)
    simulator = NPCDispatchSimulator(
        officers,
        [{"unit_id": "UNIT-PATROL", "functional_domain": "general_patrol",
          "minimum_crew_size": 2, "target_crew_size": 3}],
    )
    incidents = [DispatchIncident("SWINC-001", "Burglary", "general_patrol", 2, "ADDR-1")]
    return NPCDispatchConsole(simulator, incidents)


class NPCDispatchConsoleTests(unittest.TestCase):
    def test_player_can_assign_without_officer_or_membership_ids(self):
        console = build_console()
        result = console.execute(("assign", "SWINC-001"))
        self.assertIn("NPC dispatch assigned UNIT-PATROL", result)
        self.assertIn("Crew:", result)
        self.assertIn("Deployment: SWNPC-DEP-000001", result)

    def test_dispatch_tick_automatically_assigns_pending_incidents_by_priority(self):
        posts = [
            {"post_id": f"P-{i:03d}", "unit_id": "UNIT-PATROL",
             "position_title": "Police Sergeant" if i == 1 else "Patrol Officer"}
            for i in range(1, 17)
        ]
        officers = NPCWorkforceGenerator(seed=10).generate_shift_roster(posts)
        simulator = NPCDispatchSimulator(
            officers,
            [{"unit_id": "UNIT-PATROL", "functional_domain": "general_patrol",
              "minimum_crew_size": 2, "target_crew_size": 3}],
        )
        console = NPCDispatchConsole(simulator, [
            DispatchIncident("INC-LOW", "Theft", "general_patrol", 4),
            DispatchIncident("INC-HIGH", "Robbery", "general_patrol", 1),
        ])
        assigned = console.process_dispatch_tick(max_assignments=1)
        self.assertEqual(len(assigned), 1)
        self.assertEqual(assigned[0].incident_id, "INC-HIGH")
        self.assertEqual(console.process_dispatch_tick(), ())

    def test_authoritative_tick_scheduler_runs_recurring_npc_dispatch(self):
        kernel = RuntimeKernel(InMemoryRuntimeStore())
        kernel.transition(Lifecycle.READY)
        kernel.close_bootstrap()
        kernel.transition(Lifecycle.RUNNING, player_present=True)
        scheduler = TickScheduler(kernel, InMemoryScheduleStore(), {})
        console = build_console()
        schedule_id, handler = register_npc_dispatch_schedule(scheduler, console)

        kernel.advance_tick()
        self.assertTrue(scheduler.dispatch_one())
        self.assertEqual(handler.last_run_tick, 1)
        self.assertEqual(handler.last_assigned_count, 1)
        self.assertEqual(console._simulator.snapshot()["deployments"][0]["incident_id"], "SWINC-001")

        kernel.advance_tick()
        self.assertTrue(scheduler.dispatch_one())
        self.assertEqual(handler.last_run_tick, 2)
        self.assertEqual(handler.last_assigned_count, 0)
        self.assertGreater(schedule_id, 0)

    def test_console_shows_queue_units_and_deployments(self):
        console = build_console()
        view = console.execute()
        self.assertIn("SALTWATER NPC DISPATCH", view)
        self.assertIn("SWINC-001", view)
        self.assertIn("UNIT-PATROL", view)
        self.assertIn("No active deployments", view)

    def test_player_interface_routes_dispatch_assignment_to_npc_console(self):
        kernel = RuntimeKernel(InMemoryRuntimeStore())
        interface = PlayerCommandInterface(
            kernel, PlayerProfile("player-1", "Player One"),
            npc_dispatch_console=build_console(),
        )
        result = interface.execute("dispatch assign SWINC-001")
        self.assertTrue(result.ok, result.message)
        self.assertIn("NPC dispatch assigned", result.message)

    def test_player_interface_routes_deployment_progress(self):
        console = build_console()
        assigned = console.execute(("assign", "SWINC-001"))
        deployment_id = next(
            line.split(": ", 1)[1] for line in assigned.splitlines()
            if line.startswith("Deployment:")
        )
        kernel = RuntimeKernel(InMemoryRuntimeStore())
        interface = PlayerCommandInterface(
            kernel, PlayerProfile("player-1", "Player One"),
            npc_dispatch_console=console,
        )
        arrived = interface.execute(f"dispatch arrive {deployment_id}")
        self.assertTrue(arrived.ok, arrived.message)
        self.assertIn("on_scene", arrived.message)

    def test_unknown_incident_and_invalid_command_are_clear(self):
        console = build_console()
        with self.assertRaisesRegex(ValueError, "was not found"):
            console.execute(("assign", "MISSING"))
        with self.assertRaisesRegex(ValueError, "Use dispatch"):
            console.execute(("unknown", "MISSING"))


if __name__ == "__main__":
    unittest.main()
