import unittest
from uuid import uuid4

from runtime.bp11_dispatcher_console import PostgresDispatcherConsole


class Board:
    def snapshot(self, credential, *, incident_limit=25):
        return {
            "incidents": [{"incident_ref": "SWINC-1", "priority": 1,
                           "severity_code": "high", "status": "OPEN"}],
            "dispatchable_unit_profiles": [{"unit_id": "SWPS-UNIT-PATROL",
                "official_name": "Patrol", "dispatch_eligible": True,
                "readiness_reason": "ready"}],
            "eligible_unit_count": 1,
        }


class Lifecycle:
    def __init__(self):
        self.args = None
    def transition(self, credential, deployment_id, **kwargs):
        self.args = (credential, deployment_id, kwargs)
        return {"status": "acknowledged"}


class BP11DispatcherConsoleTests(unittest.TestCase):
    def test_snapshot_uses_trusted_credential_and_renders_queue(self):
        console = PostgresDispatcherConsole(Board(), Lifecycle(), "trusted-session")
        snapshot = console.snapshot()
        rendered = console.render(snapshot)
        self.assertIn("SWINC-1", rendered)
        self.assertIn("SWPS-UNIT-PATROL", rendered)
        self.assertIn("ELIGIBLE", rendered)

    def test_transition_delegates_without_exposing_credential_to_command(self):
        lifecycle = Lifecycle()
        console = PostgresDispatcherConsole(Board(), lifecycle, "trusted-session")
        deployment_id = uuid4()
        result = console.transition(
            deployment_id, command="acknowledge", expected_status="issued",
            reason="Radio acknowledgement", source_ref="CAD:1",
            idempotency_key="ack:1", effective_tick=4,
        )
        self.assertEqual(result["status"], "acknowledged")
        self.assertEqual(lifecycle.args[0], "trusted-session")
        self.assertEqual(lifecycle.args[1], deployment_id)

    def test_render_rejects_incomplete_snapshot(self):
        with self.assertRaises(Exception):
            PostgresDispatcherConsole.render({"incidents": []})


if __name__ == "__main__":
    unittest.main()
