import unittest
from uuid import uuid4

from runtime.postgres_deployment_port import PostgresDeploymentPort


class Cursor:
    def __init__(self, row):
        self.row = row
        self.calls = []

    def execute(self, query, params=None):
        self.calls.append((query, params))

    def fetchone(self):
        return self.row

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class Connection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class BP08PostgresDeploymentPortTests(unittest.TestCase):
    def test_get_deployment_returns_canonical_bp08_record(self):
        deployment_id = uuid4()
        cursor = Cursor((deployment_id, "issued", "SWPS-UNIT-PATROL", "CALL-1", "SWADDR-1"))
        port = PostgresDeploymentPort(lambda: Connection(cursor))
        result = port.get_deployment(deployment_id)
        self.assertEqual(result["status"], "issued")
        self.assertEqual(result["unit_id"], "SWPS-UNIT-PATROL")
        self.assertEqual(cursor.calls[0][1], (deployment_id,))

    def test_transition_calls_atomic_database_function(self):
        deployment_id = uuid4()
        cursor = Cursor((deployment_id, "acknowledged", 901))
        port = PostgresDeploymentPort(lambda: Connection(cursor))
        result = port.transition_deployment(
            deployment_id=deployment_id, expected_status="issued",
            resulting_status="acknowledged", event_kind="acknowledged",
            actor_ref="officer-person:19", reason="Radio acknowledgement",
            source_ref="CAD:CALL-1", idempotency_key="dispatch:CALL-1:ack",
            effective_tick=52,
        )
        self.assertEqual(result["event_id"], 901)
        self.assertIn("sw_police.transition_unit_deployment", cursor.calls[0][0])
        self.assertEqual(cursor.calls[0][1][0], deployment_id)

    def test_transition_rejects_extra_or_missing_fields(self):
        port = PostgresDeploymentPort(lambda: Connection(Cursor(None)))
        with self.assertRaises(ValueError):
            port.transition_deployment(deployment_id=uuid4())


if __name__ == "__main__":
    unittest.main()
