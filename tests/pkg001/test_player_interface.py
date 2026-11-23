import unittest

from runtime.kernel import InMemoryRuntimeStore, Lifecycle, RuntimeKernel
from runtime.player_interface import PlayerCommandInterface, PlayerProfile


class PlayerCommandInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryRuntimeStore()
        self.kernel = RuntimeKernel(self.store)
        self.profile = PlayerProfile("player-1", "Saltwater Player")
        self.interface = PlayerCommandInterface(self.kernel, self.profile)
        self.kernel.transition(Lifecycle.READY)
        self.kernel.close_bootstrap()

    def test_help_and_unknown_commands(self):
        self.assertIn("status", self.interface.execute("help").message)
        result = self.interface.execute("launch")
        self.assertFalse(result.ok)
        self.assertIn("Unknown command", result.message)

    def test_profile_is_game_native_and_does_not_invent_officer(self):
        result = self.interface.execute("profile")
        self.assertTrue(result.ok)
        self.assertIn("not assigned", result.message)
        self.assertIn("not started", result.message)

    def test_start_pause_resume_and_quit_freeze_world(self):
        self.assertTrue(self.interface.execute("start").ok)
        self.assertEqual(self.kernel.status().lifecycle, Lifecycle.RUNNING)
        self.kernel.advance_tick()
        self.assertTrue(self.interface.execute("pause").ok)
        self.assertEqual(self.kernel.status().world_tick, 1)
        self.assertTrue(self.interface.execute("resume").ok)
        self.assertTrue(self.interface.execute("quit").quit_requested)
        self.assertEqual(self.kernel.status().lifecycle, Lifecycle.STOPPED)
        self.assertFalse(self.kernel.status().player_present)
        with self.assertRaises(Exception):
            self.kernel.advance_tick()

    def test_recruit_and_career_commands_fail_honestly_without_domain_adapter(self):
        recruit = self.interface.execute("recruit")
        career = self.interface.execute("career")
        self.assertFalse(recruit.ok)
        self.assertIn("not connected", recruit.message)
        self.assertFalse(career.ok)
        self.assertIn("not connected", career.message)

    def test_start_cannot_bypass_bootstrap_gate(self):
        store = InMemoryRuntimeStore()
        kernel = RuntimeKernel(store)
        kernel.transition(Lifecycle.READY)
        interface = PlayerCommandInterface(kernel, self.profile)
        result = interface.execute("start")
        self.assertFalse(result.ok)
        self.assertEqual(kernel.status().lifecycle, Lifecycle.READY)

    def test_explicit_start_reenters_after_quit_without_advancing_time(self):
        self.assertTrue(self.interface.execute("start").ok)
        self.assertEqual(self.kernel.status().world_tick, 0)

        self.assertTrue(self.interface.execute("quit").quit_requested)
        stopped = self.kernel.status()
        self.assertEqual(stopped.lifecycle, Lifecycle.STOPPED)
        self.assertFalse(stopped.player_present)
        self.assertEqual(stopped.world_tick, 0)

        self.assertTrue(self.interface.execute("status").ok)
        self.assertEqual(self.kernel.status().lifecycle, Lifecycle.STOPPED)
        self.assertFalse(self.kernel.status().player_present)
        self.assertEqual(self.kernel.status().world_tick, 0)

        restarted = self.interface.execute("start")
        self.assertTrue(restarted.ok, restarted.message)
        self.assertEqual(self.kernel.status().lifecycle, Lifecycle.RUNNING)
        self.assertTrue(self.kernel.status().player_present)
        self.assertEqual(self.kernel.status().world_tick, 0)

    def test_start_does_not_implicitly_resume_a_paused_simulation(self):
        self.assertTrue(self.interface.execute("start").ok)
        self.assertTrue(self.interface.execute("pause").ok)
        result = self.interface.execute("start")
        self.assertFalse(result.ok)
        self.assertIn("Use resume", result.message)
        self.assertEqual(self.kernel.status().lifecycle, Lifecycle.PAUSED)

    def test_commands_reject_arguments_and_malformed_quotes(self):
        self.assertFalse(self.interface.execute("status extra").ok)
        self.assertFalse(self.interface.execute('"unterminated').ok)

    def test_bingo_is_not_a_general_command(self):
        result = self.interface.execute("bingo")
        self.assertFalse(result.ok)
        self.assertIn("Unknown command", result.message)


if __name__ == "__main__":
    unittest.main()
