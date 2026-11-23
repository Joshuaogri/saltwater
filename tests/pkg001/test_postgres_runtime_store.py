import os
import unittest

import psycopg

from runtime.kernel import KernelError, Lifecycle, PostgresRuntimeStore, RuntimeKernel


class PostgresRuntimeStoreTests(unittest.TestCase):
    def test_persistent_pause_safe_runtime_and_idempotent_events(self):
        def connect():
            return psycopg.connect(
                host=os.environ["PGHOST"],
                port=os.environ["PGPORT"],
                user=os.environ["PGUSER"],
                password=os.environ["PGPASSWORD"],
                dbname=os.environ["PGDATABASE"],
            )

        kernel = RuntimeKernel(PostgresRuntimeStore(connect))
        self.assertEqual(kernel.status().lifecycle, Lifecycle.READY)
        self.assertEqual(kernel.status().world_tick, 0)

        self.assertTrue(kernel.status().bootstrap_open)
        kernel.close_bootstrap()
        self.assertFalse(kernel.status().bootstrap_open)
        kernel.transition(Lifecycle.RUNNING, player_present=True)

        first = kernel.record("PERSON_CREATED", idempotency_key="pkg001-person-event")
        repeated = kernel.record("PERSON_CREATED", idempotency_key="pkg001-person-event")
        self.assertEqual(first.event_id, repeated.event_id)
        child = kernel.record("PERSON_PROFILE_CHANGED", causation_id=first.event_id)
        self.assertEqual(child.causation_id, first.event_id)

        state = kernel.advance_tick(idempotency_key="pkg001-tick-1")
        self.assertEqual(state.world_tick, 1)
        repeated_tick = kernel.advance_tick(idempotency_key="pkg001-tick-1")
        self.assertEqual(repeated_tick.world_tick, 1)

        # A new adapter instance proves that state is database-backed, not process-local.
        reloaded = RuntimeKernel(PostgresRuntimeStore(connect))
        self.assertEqual(reloaded.status().world_tick, 1)
        self.assertEqual(reloaded.status().last_event_id, state.last_event_id)

        reloaded.transition(Lifecycle.PAUSED)
        with self.assertRaises(KernelError):
            reloaded.advance_tick()
        self.assertEqual(reloaded.status().world_tick, 1)
        reloaded.transition(Lifecycle.RUNNING, player_present=True)

        # A failed command after event insertion must roll back the event.
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM sw_core.simulation_event")
                before = cur.fetchone()[0]
        with self.assertRaises(RuntimeError):
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT event_type_id FROM sw_core.event_type WHERE event_code='PERSON_PROFILE_CHANGED'"
                    )
                    event_type_id = cur.fetchone()[0]
                    cur.execute(
                        "INSERT INTO sw_core.simulation_event "
                        "(event_type_id,occurred_at,world_tick,idempotency_key) "
                        "VALUES (%s,now(),1,'pkg001-rollback-check')",
                        (event_type_id,),
                    )
                    raise RuntimeError("simulated domain-write failure")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM sw_core.simulation_event")
                self.assertEqual(cur.fetchone()[0], before)
                cur.execute("SELECT count(*) FROM sw_core.simulation_event WHERE idempotency_key='pkg001-rollback-check'")
                self.assertEqual(cur.fetchone()[0], 0)

        # Recovery and safe-halt transitions freeze time until ready/running.
        reloaded.transition(Lifecycle.RECOVERING)
        self.assertEqual(reloaded.status().world_tick, 1)
        with self.assertRaises(KernelError):
            reloaded.advance_tick()
        reloaded.transition(Lifecycle.SAFE_HALT)
        with self.assertRaises(KernelError):
            reloaded.advance_tick()
        reloaded.transition(Lifecycle.RECOVERING)
        reloaded.transition(Lifecycle.READY)
        reloaded.transition(Lifecycle.RUNNING, player_present=True)
        self.assertEqual(reloaded.advance_tick().world_tick, 2)
        reloaded.transition(Lifecycle.STOPPED)
        self.assertEqual(reloaded.status().lifecycle, Lifecycle.STOPPED)


if __name__ == "__main__":
    unittest.main()
