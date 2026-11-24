import unittest

from runtime.kernel import InMemoryRuntimeStore, Lifecycle, RuntimeKernel
from runtime.player_interface import PlayerCommandInterface, PlayerProfile
from runtime.player_workspace import WORKSPACES, WORKSPACE_BY_ID, WorkspaceNavigation

class PlayerWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.kernel = RuntimeKernel(InMemoryRuntimeStore())
        self.kernel.transition(Lifecycle.READY)
        self.kernel.close_bootstrap()
        self.profile = PlayerProfile("player-α-000000000000000000000000", "Zoë O’Connor — Saltwater")
        self.interface = PlayerCommandInterface(self.kernel, self.profile)

    def test_catalogue_is_fixed_ordered_and_unique(self):
        ids = [item.id for item in WORKSPACES]
        self.assertEqual(len(ids), 10)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [
            "home", "operations", "cases", "people", "evidence-scenes",
            "department", "legal-custody", "resources-finance",
            "reports-notifications", "system-status",
        ])
        self.assertEqual(len(WORKSPACE_BY_ID), 10)

    def test_exact_selection_and_invalid_inputs_preserve_state(self):
        self.assertTrue(self.interface.execute("workspace cases").ok)
        self.assertEqual(self.interface.workspace_navigation.current, "cases")
        for command in ("workspace Case", "workspace evid", "workspace unknown", "workspace", "workspace cases extra"):
            before = self.interface.workspace_navigation
            result = self.interface.execute(command)
            self.assertFalse(result.ok, command)
            self.assertEqual(self.interface.workspace_navigation, before)

    def test_back_is_deterministic_and_history_is_bounded(self):
        for wid in ("operations", "cases", "people", "department"):
            self.assertTrue(self.interface.execute(f"workspace {wid}").ok)
        self.assertEqual(len(self.interface.workspace_navigation.history), 4)
        self.assertTrue(self.interface.execute("back").ok)
        self.assertEqual(self.interface.workspace_navigation.current, "people")
        self.assertTrue(self.interface.execute("back").ok)
        self.assertEqual(self.interface.workspace_navigation.current, "cases")

    def test_home_catalogue_and_where_are_plain_text_and_truthful(self):
        home = self.interface.execute("home")
        self.assertTrue(home.ok)
        for expected in ("SALTWATER", "Zoë O’Connor", "Player ID:", "Runtime: READY",
                         "Player present: no", "World tick: 0", "Current workspace:",
                         "NOT CONNECTED", "navigation only", "No simulation time advances"):
            self.assertIn(expected, home.message)
        self.assertIn("reports-notifications", self.interface.execute("workspaces").message)
        where = self.interface.execute("where")
        self.assertIn("Selected record: none", where.message)

    def test_navigation_commands_never_advance_world_tick_in_any_lifecycle(self):
        scenarios = (
            ("ready", lambda: None),
            ("running", lambda: self.interface.execute("start")),
            ("paused", lambda: (self.interface.execute("start"), self.interface.execute("pause"))),
            ("stopped", lambda: self.interface.execute("quit")),
        )
        for name, prepare in scenarios:
            with self.subTest(lifecycle=name):
                kernel = RuntimeKernel(InMemoryRuntimeStore())
                kernel.transition(Lifecycle.READY)
                kernel.close_bootstrap()
                interface = PlayerCommandInterface(kernel, self.profile)
                if name == "running":
                    interface.execute("start")
                elif name == "paused":
                    interface.execute("start")
                    interface.execute("pause")
                elif name == "stopped":
                    interface.execute("quit")
                before = kernel.status()
                for command in ("home", "workspaces", "workspace operations", "where", "back"):
                    result = interface.execute(command)
                    self.assertTrue(result.ok, result.message)
                after = kernel.status()
                self.assertEqual(after.world_tick, before.world_tick)
                self.assertEqual(after.lifecycle, before.lifecycle)
                self.assertEqual(after.player_present, before.player_present)

    def test_operational_workspaces_are_never_claimed_as_connected(self):
        for item in WORKSPACES:
            if item.id not in ("home", "system-status"):
                self.assertEqual(item.availability, "navigation_only")

if __name__ == "__main__":
    unittest.main()
