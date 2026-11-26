"""Disposable PostgreSQL integration test for the canonical NPC dispatch source."""
import unittest
import psycopg

from runtime.npc_dispatch import DispatchIncident
from runtime.postgres_npc_dispatch import PostgresNPCDispatchFactory


class PostgresNPCDispatchIntegrationTests(unittest.TestCase):
    def test_vacant_establishment_does_not_fabricate_npc_dispatch_crew(self):
        with psycopg.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM sw_police.authorised_post WHERE post_status='vacant'")
                vacant_posts = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM sw_police.career_post_appointment WHERE effective_to_tick IS NULL")
                active_appointments = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM sw_police.unit_membership WHERE actual_end_tick IS NULL")
                active_memberships = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT count(*) FROM sw_police.personnel_service_current "
                    "WHERE life_status=1 AND scope_status=1"
                )
                personnel_count = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT count(*) FROM sw_police.unit_profile "
                    "WHERE lifecycle_state='active' AND dispatchable"
                )
                dispatchable_units = cursor.fetchone()[0]

        self.assertEqual(vacant_posts, 500)
        self.assertEqual(active_appointments, 0)
        self.assertEqual(active_memberships, 0)
        self.assertGreater(personnel_count, 0)
        self.assertGreater(dispatchable_units, 0)

        factory = PostgresNPCDispatchFactory(lambda: psycopg.connect())
        console = factory.build([
            DispatchIncident("CI-NPC-INC-001", "routine patrol call", "patrol", 3, "CI-LOCATION-1")
        ], current_shift="Alpha")
        deployments = console.process_dispatch_tick()
        snapshot = console._simulator.snapshot()

        self.assertEqual(deployments, ())
        self.assertEqual(snapshot["workforce_count"], personnel_count)
        self.assertEqual(snapshot["unassigned_npc_count"], personnel_count)
        self.assertEqual(snapshot["available_npc_count"], 0)
        self.assertEqual(snapshot["deployments"], [])
        self.assertTrue(all(unit["operational_status"] == "unavailable" for unit in snapshot["units"]))
        self.assertTrue(all(unit["available_crew"] == 0 for unit in snapshot["units"]))


if __name__ == "__main__":
    unittest.main()
