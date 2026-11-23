import unittest

from runtime.kernel import (
    InMemoryRuntimeStore, KernelError, Lifecycle, RuntimeKernel,
)


class RuntimeKernelTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryRuntimeStore()
        self.kernel = RuntimeKernel(self.store)

    def start(self):
        self.kernel.transition(Lifecycle.READY)
        self.kernel.close_bootstrap()
        self.kernel.transition(Lifecycle.RUNNING, player_present=True)

    def test_stopped_and_paused_time_never_advances(self):
        with self.assertRaises(KernelError):
            self.kernel.advance_tick()
        self.start()
        self.kernel.transition(Lifecycle.PAUSED)
        with self.assertRaises(KernelError):
            self.kernel.advance_tick()
        self.assertEqual(self.kernel.status().world_tick, 0)

    def test_bootstrap_must_close_before_start_and_cannot_reopen(self):
        self.kernel.transition(Lifecycle.READY)
        with self.assertRaises(KernelError):
            self.kernel.transition(Lifecycle.RUNNING, player_present=True)
        self.kernel.close_bootstrap()
        self.kernel.transition(Lifecycle.RUNNING, player_present=True)
        self.assertFalse(self.kernel.close_bootstrap().bootstrap_open)
        self.assertFalse(self.kernel.status().bootstrap_open)

    def test_valid_transitions_and_tick(self):
        self.start()
        state = self.kernel.advance_tick(idempotency_key="tick-1")
        self.assertEqual(state.world_tick, 1)
        self.kernel.transition(Lifecycle.PAUSED)
        self.kernel.transition(Lifecycle.RUNNING, player_present=True)
        self.assertEqual(self.kernel.advance_tick().world_tick, 2)

    def test_invalid_transition_rejected(self):
        with self.assertRaises(KernelError):
            self.kernel.transition(Lifecycle.RUNNING, player_present=True)

    def test_event_causation_and_idempotency(self):
        self.start()
        first = self.kernel.record("INCIDENT_CREATED", idempotency_key="i-1")
        second = self.kernel.record("CASE_OPENED", causation_id=first.event_id)
        self.assertEqual(second.causation_id, first.event_id)
        with self.assertRaises(KernelError):
            self.kernel.record("INCIDENT_CREATED", idempotency_key="i-1")

    def test_event_tick_must_match_committed_tick(self):
        self.start()
        self.kernel.advance_tick()
        self.assertEqual(self.kernel.status().world_tick, 1)
        self.assertEqual(self.kernel.store.events[-1].world_tick, 1)


if __name__ == "__main__":
    unittest.main()
