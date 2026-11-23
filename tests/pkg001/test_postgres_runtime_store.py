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
        self.assertEqual(kernel.status().lifecycle, Lifecycle.STOPPED)
        self.assertEqual(kernel.status().world_tick, 0)

        kernel.transition(Lifecycle.READY)
        self.assertEqual(kernel.status().lifecycle, Lifecycle.READY)
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
        reloaded.transition(Lifecycle.STOPPED)
        self.assertEqual(reloaded.status().lifecycle, Lifecycle.STOPPED)


if __name__ == "__main__":
    unittest.main()
