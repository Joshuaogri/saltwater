from __future__ import annotations

import unittest
from uuid import uuid4

from runtime.recovery import (
    CheckpointSource, ClaimReconciliation, PostgresRecoveryStore, RecoveryError,
)


class FakeCursor:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.current = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        self.current = self.responses.pop(0) if self.responses else None

    def fetchone(self):
        return self.current


class FakeConnection:
    def __init__(self, responses=()):
        self.cursor_value = FakeCursor(responses)
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def cursor(self):
        return self.cursor_value

    def close(self):
        self.closed = True


class RecoveryContractTests(unittest.TestCase):
    def test_checkpoint_source_requires_explicit_provenance(self):
        CheckpointSource("test", "saltwater", "main", "disposable", "test:actor", "approval:1").validate()
        with self.assertRaises(RecoveryError):
            CheckpointSource("", "saltwater", "main", "disposable", "test:actor", "approval:1").validate()

    def test_committed_effect_requires_outcome_reference(self):
        decision = ClaimReconciliation(
            7, uuid4(), "effect_committed", "geography", "owner:reconcile:7",
            None, "test:actor", "approval:1", "verified_committed", "recovery:7",
        )
        with self.assertRaises(RecoveryError):
            decision.validate()

    def test_absent_or_indeterminate_cannot_claim_outcome(self):
        for state in ("effect_absent", "indeterminate"):
            decision = ClaimReconciliation(
                7, uuid4(), state, "geography", "owner:reconcile:7", "invented:outcome",
                "test:actor", "approval:1", "owner_confirmed", "recovery:7",
            )
            with self.assertRaises(RecoveryError):
                decision.validate()

    def test_valid_reconciliation_contract(self):
        ClaimReconciliation(
            7, uuid4(), "effect_committed", "geography", "owner:reconcile:7",
            "domain:outcome:7", "test:actor", "approval:1", "verified_committed", "recovery:7",
        ).validate()

    def test_checkpoint_capture_uses_repeatable_read_and_explicit_source(self):
        checkpoint_id = uuid4()
        conn = FakeConnection([None, (checkpoint_id,)])
        store = PostgresRecoveryStore(lambda: conn)
        result = store.capture_checkpoint(
            CheckpointSource("disposable", "saltwater", "main", "saltwater_test",
                             "test:actor", "approval:bp39-01")
        )
        self.assertEqual(result, checkpoint_id)
        self.assertEqual(conn.cursor_value.calls[0][0],
                         "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        self.assertIn("capture_checkpoint_manifest", conn.cursor_value.calls[1][0])
        self.assertTrue(conn.closed)

    def test_recovery_decision_calls_authoritative_database_function(self):
        conn = FakeConnection([("completed",)])
        store = PostgresRecoveryStore(lambda: conn)
        decision = ClaimReconciliation(
            7, uuid4(), "effect_committed", "geography", "owner:reconcile:7",
            "domain:outcome:7", "test:actor", "approval:bp39-01",
            "verified_committed", "recovery:7",
        )
        self.assertEqual(store.reconcile_claim(decision), "completed")
        self.assertIn("reconcile_event_claim", conn.cursor_value.calls[0][0])
        self.assertEqual(conn.cursor_value.calls[0][1][0], 7)
        self.assertTrue(conn.closed)

    def test_checkpoint_validation_returns_separate_gates(self):
        expected = {"valid": False, "gates": {"schema_watermark": {"status": "pass"},
                                               "business_minimum": {"status": "not_executed"}}}
        conn = FakeConnection([(expected,)])
        result = PostgresRecoveryStore(lambda: conn).validate_checkpoint(uuid4())
        self.assertEqual(result["gates"]["schema_watermark"]["status"], "pass")
        self.assertEqual(result["gates"]["business_minimum"]["status"], "not_executed")

    def test_invalid_event_identity_rejected_before_database_access(self):
        with self.assertRaises(RecoveryError):
            ClaimReconciliation(
                0, uuid4(), "effect_absent", "geography", "owner:response",
                None, "actor", "approval", "confirmed_absent", "key",
            ).validate()


if __name__ == "__main__":
    unittest.main()
