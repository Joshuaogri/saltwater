"""Disposable PostgreSQL integration test for the canonical NPC dispatch source."""
import unittest
import psycopg

from runtime.npc_dispatch import DispatchIncident
from runtime.postgres_npc_dispatch import PostgresNPCDispatchFactory


class PostgresNPCDispatchIntegrationTests(unittest.TestCase):
    def test_canonical_500_post_establishment_builds_a_playable_npc_dispatch(self):
        with psycopg.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT count(*) FROM sw_police.authorised_post WHERE post_status <> 'abolished'"
                )
                post_count = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM sw_police.unit_profile WHERE lifecycle_state='active' AND dispatchable")
                dispatchable_units = cursor.fetchone()[0]
        self.assertEqual(post_count, 500)
        self.assertGreater(dispatchable_units, 0)

        factory = PostgresNPCDispatchFactory(lambda: psycopg.connect())
        console = factory.build([
            DispatchIncident("CI-NPC-INC-001", "routine patrol call", "patrol", 3, "CI-LOCATION-1")
        ], current_shift="Alpha")
        result = console.execute(("assign", "CI-NPC-INC-001"))
        self.assertIn("NPC dispatch assigned", result)
        self.assertIn("SWPS-UNIT-PATROL", result)
        self.assertIn("Crew:", result)


if __name__ == "__main__":
    unittest.main()
