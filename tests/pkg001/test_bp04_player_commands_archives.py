"""End-to-end player command checks against the real archive-only BP04 release."""
import os
import unittest

import psycopg

from runtime.bp04_lookup import BP04Lookup
from runtime.kernel import InMemoryRuntimeStore, Lifecycle, RuntimeKernel
from runtime.player_interface import PlayerCommandInterface, PlayerProfile


class BP04ArchivedPlayerCommandIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = psycopg.connect(os.environ["DATABASE_URL"])
        cls.lookup = BP04Lookup(cls.connection)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def setUp(self):
        self.kernel = RuntimeKernel(InMemoryRuntimeStore())
        self.kernel.transition(Lifecycle.READY)
        self.kernel.close_bootstrap()
        self.interface = PlayerCommandInterface(
            self.kernel, PlayerProfile("archive-test-player", "Archive Test Player"),
            bp04_lookup=self.lookup,
        )

    def test_find_commands_use_real_property_address_and_business_archives(self):
        for entity_type, query, expected_key in (
            ("property", next(iter(self.lookup._by_id["property"])), "property_id"),
            ("address", "Saltwater", "address_id"),
            ("business", "SWBIZ", "business_id"),
        ):
            with self.subTest(entity_type=entity_type):
                result = self.interface.execute(f"find {entity_type} {query}")
                self.assertTrue(result.ok, result.message)
                self.assertIn("Matches:", result.message)
                self.assertIn(self.lookup.search(entity_type, query, limit=1)[0][expected_key],
                              result.message)

    def test_inspect_commands_resolve_every_supported_archive_entity_type(self):
        identities = {
            "property": "property_id", "address": "address_id",
            "building": "building_id", "premises": "premises_id",
            "unit": "unit_id", "access_point": "access_point_id",
            "business": "business_id", "establishment": "establishment_id",
        }
        for entity_type, id_field in identities.items():
            with self.subTest(entity_type=entity_type):
                records = self.lookup._by_id[entity_type]
                identifier = next(iter(records))
                result = self.interface.execute(f"inspect {entity_type} {identifier}")
                self.assertTrue(result.ok, result.message)
                self.assertIn(identifier, result.message)

    def test_read_only_lookup_does_not_advance_world_time(self):
        before = self.kernel.status()
        self.assertTrue(self.interface.execute("find address Saltwater").ok)
        self.assertTrue(self.interface.execute(
            f"inspect building {next(iter(self.lookup._by_id['building']))}"
        ).ok)
        after = self.kernel.status()
        self.assertEqual(after.world_tick, before.world_tick)
        self.assertEqual(after.lifecycle, before.lifecycle)
        self.assertEqual(after.player_present, before.player_present)

    def test_malformed_and_missing_records_fail_without_mutating_runtime(self):
        before = self.kernel.status()
        malformed = self.interface.execute("inspect building")
        missing = self.interface.execute("inspect building SWBLD-NOT-FOUND")
        self.assertFalse(malformed.ok)
        self.assertTrue(missing.ok)
        self.assertIn("not found", missing.message.casefold())
        self.assertEqual(self.kernel.status(), before)


if __name__ == "__main__":
    unittest.main()
