"""BP35-01 deterministic event intake and dispatch tests."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from runtime.event_engine import (
    EventEngine, EventEngineError, EventWorkDefinition, HandlerReceipt,
    HandlerSpec, InMemoryEventWorkStore,
)
from runtime.kernel import InMemoryRuntimeStore, Lifecycle, RuntimeKernel


class EventEngineTests(unittest.TestCase):
    def setUp(self):
        self.kernel = RuntimeKernel(InMemoryRuntimeStore())
        self.store = InMemoryEventWorkStore()
        self.calls = []
        self.engine = EventEngine(self.kernel, self.store, lambda work, spec: True)
        self.engine.register(HandlerSpec(
            owner_domain="geography", handler_key="geo.create", handler_version=1,
            event_codes=frozenset({"GEO_CREATED", "GEO_VERSIONED"}),
            schema_versions=frozenset({1}),
            permission_action="geography.event.execute", handle=self.handler,
        ))

    def start(self):
        self.kernel.transition(Lifecycle.READY)
        self.kernel.close_bootstrap()
        self.kernel.transition(Lifecycle.RUNNING, player_present=True)

    def handler(self, work, world_tick):
        self.calls.append((work.event_id, work.idempotency_key, world_tick))
        return HandlerReceipt(True, outcome_ref=f"geo-record:{work.event_id}")

    def definition(self, key, **kwargs):
        return EventWorkDefinition(
            event_code=kwargs.pop("event_code", "GEO_CREATED"),
            owner_domain="geography", handler_key="geo.create",
            handler_version=1, schema_version=1, due_tick=0,
            idempotency_key=key, **kwargs,
        )

    def test_intake_requires_running_present_runtime(self):
        with self.assertRaises(EventEngineError):
            self.engine.submit(self.definition("before-start"))
        self.start()
        event_id = self.engine.submit(self.definition("accepted"))
        self.assertGreater(event_id, 0)

    def test_registered_type_version_and_owner_contract_are_enforced(self):
        self.start()
        with self.assertRaisesRegex(EventEngineError, "unregistered"):
            self.engine.submit(replace(self.definition("unknown"), handler_key="missing"))
        with self.assertRaisesRegex(EventEngineError, "does not match"):
            self.engine.submit(replace(self.definition("wrong-version"), schema_version=2))
        with self.assertRaises(EventEngineError):
            self.engine.register(self.engine._handlers["geo.create"])

    def test_idempotent_submission_and_conflicting_definition(self):
        self.start()
        definition = self.definition("stable-key")
        first = self.engine.submit(definition)
        self.assertEqual(self.engine.submit(definition), first)
        with self.assertRaisesRegex(EventEngineError, "conflicts"):
            self.engine.submit(replace(definition, priority=4))

    def test_due_order_is_priority_then_stable_event_id(self):
        self.start()
        low = self.engine.submit(self.definition("low", priority=1))
        high1 = self.engine.submit(self.definition("high1", priority=5))
        high2 = self.engine.submit(self.definition("high2", priority=5))
        self.assertEqual(self.engine.dispatch_one().event_id, high1)
        self.assertEqual(self.engine.dispatch_one().event_id, high2)
        self.assertEqual(self.engine.dispatch_one().event_id, low)
        self.assertEqual([x[0] for x in self.calls], [high1, high2, low])

    def test_causal_child_waits_for_parent_commit(self):
        self.start()
        parent = self.engine.submit(self.definition("parent", priority=0))
        child = self.engine.submit(self.definition(
            "child", event_code="GEO_VERSIONED", priority=100,
            prerequisite_event_ids=(parent,),
        ))
        self.assertEqual(self.engine.dispatch_one().event_id, parent)
        self.assertEqual(self.engine.dispatch_one().event_id, child)
        self.assertEqual(self.store.inspect(child)["status"], "completed")

    def test_success_is_effectively_once_and_has_a_durable_receipt(self):
        self.start()
        event_id = self.engine.submit(self.definition("once"))
        result = self.engine.dispatch_one()
        self.assertEqual(result.status, "completed")
        self.assertIsNone(self.engine.dispatch_one())
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.store.inspect(event_id)["outcome_ref"], f"geo-record:{event_id}")

    def test_permission_denial_quarantines_without_invoking_domain_handler(self):
        self.start()
        denied = EventEngine(self.kernel, self.store, lambda work, spec: False)
        denied.register(self.engine._handlers["geo.create"])
        event_id = denied.submit(self.definition("denied"))
        result = denied.dispatch_one()
        self.assertEqual(result.status, "quarantined")
        self.assertEqual(self.store.inspect(event_id)["error_code"], "permission_denied")
        self.assertEqual(self.calls, [])

    def test_handler_exception_retries_then_quarantines_at_attempt_limit(self):
        self.start()
        def broken(work, tick):
            raise RuntimeError("private handler detail")
        failing = EventEngine(self.kernel, self.store, lambda work, spec: True)
        failing.register(replace(self.engine._handlers["geo.create"], handle=broken))
        event_id = failing.submit(self.definition("broken", max_attempts=2))
        self.assertEqual(failing.dispatch_one().status, "failed")
        self.kernel.advance_tick()
        self.assertEqual(failing.dispatch_one().status, "quarantined")
        self.assertEqual(self.store.inspect(event_id)["attempt_count"], 2)
        self.assertEqual(self.store.inspect(event_id)["error_code"], "owner_handler_error")
        self.assertNotIn("private", str(self.store.attempts(event_id)))

    def test_invalid_handler_result_is_quarantined(self):
        self.start()
        invalid = EventEngine(self.kernel, self.store, lambda work, spec: True)
        invalid.register(replace(
            self.engine._handlers["geo.create"],
            handle=lambda work, tick: {"success": True},
        ))
        event_id = invalid.submit(self.definition("invalid-result"))
        self.assertEqual(invalid.dispatch_one().status, "quarantined")
        self.assertEqual(self.store.inspect(event_id)["error_code"], "invalid_handler_result")

    def test_stale_claim_token_cannot_finalize_work(self):
        self.start()
        event_id = self.engine.submit(self.definition("claim-token"))
        work = self.store.claim_due(0)
        with self.assertRaisesRegex(EventEngineError, "stale"):
            self.store.finish(replace(work, claim_token=__import__("uuid").uuid4()),
                              HandlerReceipt(True, outcome_ref="fake"), 0)
        self.assertEqual(self.store.inspect(event_id)["status"], "claimed")
        self.assertEqual(self.store.finish(
            work, HandlerReceipt(True, outcome_ref="valid"), 0
        ), "completed")

    def test_concurrent_claims_never_return_the_same_event_twice(self):
        self.start()
        event_id = self.engine.submit(self.definition("concurrent"))
        with ThreadPoolExecutor(max_workers=8) as pool:
            claims = list(pool.map(lambda _: self.store.claim_due(0), range(8)))
        claimed = [x for x in claims if x is not None]
        self.assertEqual(len(claimed), 1)
        self.assertEqual(claimed[0].event_id, event_id)

    def test_paused_absent_and_recovering_runtime_freeze_dispatch(self):
        self.start()
        event_id = self.engine.submit(self.definition("paused"))
        self.kernel.transition(Lifecycle.PAUSED)
        self.assertIsNone(self.engine.dispatch_one())
        self.assertEqual(self.store.inspect(event_id)["status"], "pending")
        self.kernel.transition(Lifecycle.RUNNING, player_present=True)
        self.kernel.transition(Lifecycle.RECOVERING)
        self.assertIsNone(self.engine.dispatch_one())
        self.kernel.transition(Lifecycle.READY)
        self.assertIsNone(self.engine.dispatch_one())

    def test_invalid_success_receipt_is_not_committed(self):
        self.start()
        invalid = EventEngine(self.kernel, self.store, lambda work, spec: True)
        invalid.register(replace(
            self.engine._handlers["geo.create"],
            handle=lambda work, tick: HandlerReceipt(True),
        ))
        event_id = invalid.submit(self.definition("no-outcome"))
        self.assertEqual(invalid.dispatch_one().status, "quarantined")
        self.assertNotEqual(self.store.inspect(event_id)["status"], "completed")


if __name__ == "__main__":
    unittest.main()
