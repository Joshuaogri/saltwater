"""BP37-01 deterministic clock scheduling tests."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from runtime.kernel import InMemoryRuntimeStore, Lifecycle, RuntimeKernel
from runtime.scheduling import (
    InMemoryScheduleStore,
    ScheduleDefinition,
    ScheduleExecutionResult,
    SchedulingError,
    TickScheduler,
)


class TickSchedulerTests(unittest.TestCase):
    def setUp(self):
        self.kernel = RuntimeKernel(InMemoryRuntimeStore())
        self.store = InMemoryScheduleStore()
        self.calls = []
        self.scheduler = TickScheduler(
            self.kernel, self.store,
            {"police": self.owner_handler, "world": self.world_handler},
        )

    def start(self):
        self.kernel.transition(Lifecycle.READY)
        self.kernel.close_bootstrap()
        self.kernel.transition(Lifecycle.RUNNING, player_present=True)

    def owner_handler(self, schedule, *, world_tick):
        self.calls.append(("police", schedule.schedule_id, world_tick, schedule.idempotency_key))
        return ScheduleExecutionResult(True)

    def world_handler(self, schedule, *, world_tick):
        self.calls.append(("world", schedule.schedule_id, world_tick, schedule.idempotency_key))
        return ScheduleExecutionResult(True)

    def test_clock_is_authoritative_and_schedule_waits_for_due_tick(self):
        self.start()
        sid = self.scheduler.register(ScheduleDefinition(
            "police", "shift:alpha", 2, "shift-alpha"
        ))
        self.assertFalse(self.scheduler.dispatch_one())
        self.kernel.advance_tick()
        self.assertFalse(self.scheduler.dispatch_one())
        self.kernel.advance_tick()
        self.assertTrue(self.scheduler.dispatch_one())
        self.assertEqual(self.calls[0][1], sid)
        self.assertEqual(self.calls[0][2], 2)
        self.assertEqual(self.store.inspect(sid)["status"], "completed")

    def test_paused_absent_recovering_safe_halt_and_stopped_freeze(self):
        with self.assertRaises(SchedulingError):
            self.scheduler.register(ScheduleDefinition("police", "x", 0, "x"))
        self.start()
        sid = self.scheduler.register(ScheduleDefinition("police", "x", 0, "paused-x"))
        self.kernel.transition(Lifecycle.PAUSED)
        self.assertFalse(self.scheduler.dispatch_one())
        self.assertEqual(self.store.inspect(sid)["status"], "pending")
        self.kernel.transition(Lifecycle.RUNNING, player_present=True)
        self.kernel.transition(Lifecycle.RECOVERING)
        self.assertFalse(self.scheduler.dispatch_one())
        self.kernel.transition(Lifecycle.SAFE_HALT)
        self.assertFalse(self.scheduler.dispatch_one())
        self.kernel.transition(Lifecycle.RECOVERING)
        self.kernel.transition(Lifecycle.READY)
        self.assertFalse(self.scheduler.dispatch_one())

    def test_deterministic_due_priority_and_id_order(self):
        self.start()
        low = self.scheduler.register(ScheduleDefinition("police", "low", 0, "low", priority=1))
        high1 = self.scheduler.register(ScheduleDefinition("police", "high1", 0, "high1", priority=5))
        high2 = self.scheduler.register(ScheduleDefinition("world", "high2", 0, "high2", priority=5))
        self.assertTrue(self.scheduler.dispatch_one())
        self.assertTrue(self.scheduler.dispatch_one())
        self.assertTrue(self.scheduler.dispatch_one())
        self.assertEqual([x[1] for x in self.calls], [high1, high2, low])

    def test_owner_domain_handler_is_required_and_failure_is_retryable(self):
        self.start()
        missing = self.scheduler.register(ScheduleDefinition("unknown", "x", 0, "missing"))
        self.assertTrue(self.scheduler.dispatch_one())
        self.assertEqual(self.store.inspect(missing)["status"], "failed")
        self.assertEqual(self.store.inspect(missing)["last_error_code"], "owner_handler_missing")
        self.assertFalse(self.scheduler.dispatch_one())
        self.kernel.advance_tick()
        self.assertTrue(self.scheduler.dispatch_one())
        self.assertEqual(self.store.inspect(missing)["attempt_count"], 2)

    def test_handler_exception_does_not_create_false_completion(self):
        self.start()
        def broken(schedule, *, world_tick):
            raise RuntimeError("private detail")
        self.scheduler.handlers["police"] = broken
        sid = self.scheduler.register(ScheduleDefinition("police", "x", 0, "broken"))
        self.assertTrue(self.scheduler.dispatch_one())
        row = self.store.inspect(sid)
        self.assertEqual(row["status"], "failed")
        self.assertIsNone(row["completed_at_tick"])
        self.assertEqual(row["last_error_code"], "owner_handler_error")

    def test_repeating_schedule_advances_from_due_tick_not_host_time(self):
        self.start()
        sid = self.scheduler.register(ScheduleDefinition(
            "police", "recurring", 1, "recurring", interval_ticks=3
        ))
        self.kernel.advance_tick()
        self.assertTrue(self.scheduler.dispatch_one())
        row = self.store.inspect(sid)
        self.assertEqual(row["status"], "pending")
        self.assertEqual(row["definition"].due_tick, 4)
        self.assertFalse(self.scheduler.dispatch_one())
        self.kernel.advance_tick()
        self.kernel.advance_tick()
        self.kernel.advance_tick()
        self.assertTrue(self.scheduler.dispatch_one())
        self.assertEqual(self.store.inspect(sid)["attempt_count"], 2)

    def test_concurrent_claims_never_return_the_same_schedule_twice(self):
        self.start()
        sid = self.scheduler.register(ScheduleDefinition("police", "one", 0, "one"))
        with ThreadPoolExecutor(max_workers=8) as pool:
            claims = list(pool.map(lambda _: self.store.claim_due(0), range(8)))
        claimed = [claim for claim in claims if claim is not None]
        self.assertEqual(len(claimed), 1)
        self.assertEqual(claimed[0].schedule_id, sid)

    def test_registration_idempotency_and_definition_conflict(self):
        self.start()
        definition = ScheduleDefinition("police", "same", 0, "same-key")
        first = self.scheduler.register(definition)
        self.assertEqual(self.scheduler.register(definition), first)
        with self.assertRaises(SchedulingError):
            self.scheduler.register(ScheduleDefinition("police", "changed", 0, "same-key"))

    def test_expired_schedule_is_never_dispatched(self):
        self.start()
        sid = self.scheduler.register(ScheduleDefinition(
            "police", "expired", 0, "expired", expires_at_tick=0
        ))
        self.kernel.advance_tick()
        self.assertFalse(self.scheduler.dispatch_one())
        self.assertEqual(self.store.inspect(sid)["status"], "expired")


if __name__ == "__main__":
    unittest.main()
