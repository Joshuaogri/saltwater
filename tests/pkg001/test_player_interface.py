import unittest

from runtime.kernel import InMemoryRuntimeStore, Lifecycle, RuntimeKernel
from runtime.player_interface import PlayerCommandInterface, PlayerProfile



class FakeBP04Lookup:
    def search(self, kind, query, limit=20):
        if kind == "address":
            return [{"address_id": "SWADDR-1", "address_label": "10 Harbour Avenue", "property_id": "SWPROP-1"}]
        if kind == "business":
            return [{"business_id": "SWBIZ-1", "trading_name": "Harbour Bank", "sector": "finance"}]
        return [{"property_id": "SWPROP-1", "primary_use": "commercial", "source_district_id": "SW-D01", "source_neighbourhood_id": "SW-D01-N1"}]

    def property_detail(self, identifier):
        if identifier != "SWPROP-1":
            return None
        return {
            "property": {"property_id": identifier, "primary_use": "commercial", "source_district_id": "SW-D01", "source_neighbourhood_id": "SW-D01-N1"},
            "address": {"address_label": "10 Harbour Avenue", "address_id": "SWADDR-1"},
            "buildings": [{"building_id": "SWBLD-1"}],
            "businesses": [{"business_id": "SWBIZ-1", "trading_name": "Harbour Bank"}],
            "geography_binding": "source_geography_reference_only",
        }

    def address_detail(self, identifier):
        if identifier != "SWADDR-1":
            return None
        return {"address": {"address_id": identifier, "address_label": "10 Harbour Avenue", "property_id": "SWPROP-1", "road_id": "SW-R01", "district_id": "SW-D01", "neighbourhood_id": "SW-D01-N1"}, "geography_binding": "source_geography_reference_only"}

    def business_detail(self, identifier):
        if identifier != "SWBIZ-1":
            return None
        return {"business": {"business_id": identifier, "trading_name": "Harbour Bank", "sector": "finance", "status": "active"}, "establishments": [{"establishment_id": "SWEST-1", "establishment_name": "Harbour Bank HQ", "address": {"address_label": "10 Harbour Avenue"}, "property_id": "SWPROP-1"}]}

    def get(self, kind, identifier):
        if identifier != "SWBLD-1":
            return None
        return {"record_type": kind, "building_id": identifier, "property_id": "SWPROP-1", "building_use": "office"}


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
        self.assertNotIn("bingo", self.interface.execute("help").message)
        result = self.interface.execute("launch")
        self.assertFalse(result.ok)
        self.assertIn("Unknown command", result.message)

    def test_read_only_queries_do_not_mutate_runtime_state_or_event_history(self):
        commands = (
            "help", "status", "profile", "career", "where", "workspaces",
            "find address Harbour Avenue", "inspect property SWPROP-1",
        )
        before = self.kernel.status()
        events_before = tuple(self.store.events)
        for command in commands:
            with self.subTest(command=command):
                self.interface.execute(command)
                self.assertEqual(self.kernel.status(), before)
                self.assertEqual(tuple(self.store.events), events_before)

    def test_bingo_requires_injected_trusted_revealer_and_returns_its_result(self):
        unavailable = self.interface.execute("bingo")
        self.assertFalse(unavailable.ok)
        self.assertIn("not connected", unavailable.message)

        calls = []
        interface = PlayerCommandInterface(
            self.kernel, self.profile,
            hidden_truth_revealer=lambda player_id: calls.append(player_id) or "Hidden case truth.",
        )
        result = interface.execute("bingo")
        self.assertTrue(result.ok)
        self.assertEqual(result.message, "Hidden case truth.")
        self.assertEqual(calls, [self.profile.player_id])

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


    def test_find_address_and_business_are_connected_to_lookup(self):
        interface = PlayerCommandInterface(self.kernel, self.profile, bp04_lookup=FakeBP04Lookup())
        address = interface.execute("find address Harbour Avenue")
        business = interface.execute('find business "Harbour Bank"')
        self.assertTrue(address.ok)
        self.assertIn("SWADDR-1", address.message)
        self.assertIn("10 Harbour Avenue", address.message)
        self.assertTrue(business.ok)
        self.assertIn("SWBIZ-1", business.message)
        self.assertIn("Harbour Bank", business.message)

    def test_inspect_property_address_business_and_building(self):
        interface = PlayerCommandInterface(self.kernel, self.profile, bp04_lookup=FakeBP04Lookup())
        prop = interface.execute("inspect property SWPROP-1")
        address = interface.execute("inspect address SWADDR-1")
        business = interface.execute("inspect business SWBIZ-1")
        building = interface.execute("inspect building SWBLD-1")
        self.assertIn("source_geography_reference_only", prop.message)
        self.assertIn("SWPROP-1", address.message)
        self.assertIn("SWEST-1", business.message)
        self.assertIn("office", building.message)

    def test_lookup_commands_fail_honestly_without_lookup_provider(self):
        result = self.interface.execute("find address Harbour Avenue")
        self.assertFalse(result.ok)
        self.assertIn("not connected", result.message)

    def test_dispatch_command_uses_injected_authorised_console(self):
        class Console:
            def __init__(self):
                self.called = False
            def snapshot(self, incident_limit=25):
                self.called = True
                return {
                    "incidents": [{"incident_ref": "SWINC-100", "priority": 1,
                                   "severity_code": "high", "status": "OPEN"}],
                    "dispatchable_unit_profiles": [{"unit_id": "SWPS-UNIT-PATROL",
                        "official_name": "Patrol Unit", "dispatch_eligible": False,
                        "readiness_reason": "resources_not_ready"}],
                    "eligible_unit_count": 0,
                }
            def render(self, snapshot):
                from runtime.bp11_dispatcher_console import PostgresDispatcherConsole
                return PostgresDispatcherConsole.render(snapshot)

        console = Console()
        interface = PlayerCommandInterface(self.kernel, self.profile, dispatch_console=console)
        result = interface.execute("dispatch")
        self.assertTrue(result.ok)
        self.assertTrue(console.called)
        self.assertIn("SWINC-100", result.message)
        self.assertIn("NOT ELIGIBLE", result.message)
        self.assertIn("read-only", result.message.lower())

    def test_dispatch_command_fails_honestly_without_console(self):
        result = self.interface.execute("dispatch")
        self.assertFalse(result.ok)
        self.assertIn("not connected", result.message)

    def test_bingo_is_recognised_but_requires_the_authorised_reveal_service(self):
        result = self.interface.execute("bingo")
        self.assertFalse(result.ok)
        self.assertIn("Hidden-truth reveal service is not connected", result.message)


if __name__ == "__main__":
    unittest.main()
