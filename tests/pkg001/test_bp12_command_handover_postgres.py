import json
import unittest
from datetime import datetime, timezone

from runtime.bp12_incident_operational_events import (
    PostgresIncidentCommandHandoverHistoryReader,
    PostgresIncidentCommandHandoverWriter,
)


class FakeCursor:
    def __init__(self, result=None, rows=None):
        self.result = result
        self.rows = rows or []
        self.calls = []

    def execute(self, query, params=None):
        self.calls.append((query, params))

    def fetchone(self):
        return self.result

    def fetchall(self):
        return self.rows

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_value = cursor
        self.committed = False

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.committed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def document():
    return {
        "handover_ref": "HANDOVER-1",
        "incident_id": 7,
        "outgoing_commander_ref": "commander:out",
        "incoming_commander_ref": "commander:in",
        "prepared_by_ref": "supervisor:1",
        "authority_ref": "command:authority",
        "source_ref": "command-room:1",
        "effective_world_tick": 10,
        "assignment_reconciliation": {"handover_ready": True},
        "commander_decisions": [],
        "outstanding_actions": [],
        "responsibility_transfers": [{
            "record_ref": "transfer:1", "from_ref": "commander:out",
            "to_ref": "commander:in", "responsibility_ref": "incident-command",
            "actor_ref": "commander:out", "source_ref": "command-room:1",
            "world_tick": 10,
        }],
        "acknowledgements": [{
            "record_ref": "ack:1", "handover_ref": "HANDOVER-1",
            "recipient_ref": "commander:in", "acknowledgement": "ACCEPTED",
            "actor_ref": "commander:in", "source_ref": "command-room:1",
            "world_tick": 10,
        }],
        "handover_ready": True,
        "record_status": "PROJECTED_NOT_PERSISTED",
        "read_only": True,
    }


class CommandHandoverPostgresAdapterTests(unittest.TestCase):
    def test_writer_persists_projection_with_parameterised_sql(self):
        cursor = FakeCursor(result=(41,))
        connection = FakeConnection(cursor)
        writer = PostgresIncidentCommandHandoverWriter(lambda: connection)
        self.assertEqual(writer.record(document(), idempotency_key="handover:1"), 41)
        query, params = cursor.calls[0]
        self.assertIn("sw_incident.record_command_handover", query)
        self.assertEqual(params[0], 7)
        self.assertEqual(json.loads(params[8])["handover_ref"], "HANDOVER-1")
        self.assertEqual(params[9], "handover:1")
        self.assertTrue(connection.committed)

    def test_writer_rejects_unready_or_already_persisted_projection_before_database(self):
        cursor = FakeCursor(result=(41,))
        connection = FakeConnection(cursor)
        writer = PostgresIncidentCommandHandoverWriter(lambda: connection)
        invalid = document()
        invalid["handover_ready"] = False
        with self.assertRaises(ValueError):
            writer.record(invalid, idempotency_key="handover:2")
        invalid = document()
        invalid["record_status"] = "PERSISTED"
        with self.assertRaises(ValueError):
            writer.record(invalid, idempotency_key="handover:3")
        self.assertEqual(cursor.calls, [])

    def test_history_reader_validates_identity_and_persisted_provenance(self):
        doc = document()
        doc["record_status"] = "PERSISTED"
        row = (
            41, "HANDOVER-1", 7, "commander:out", "commander:in",
            "supervisor:1", "command:authority", "command-room:1", 10,
            doc, 91, datetime.now(timezone.utc), 12,
        )
        cursor = FakeCursor(rows=[row])
        reader = PostgresIncidentCommandHandoverHistoryReader(lambda: FakeConnection(cursor))
        result = reader.read(7)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["handover_document"]["record_status"], "PERSISTED")
        self.assertEqual(cursor.calls[0][1], (7,))

    def test_history_reader_rejects_cross_incident_result(self):
        doc = document()
        doc["record_status"] = "PERSISTED"
        row = (
            41, "HANDOVER-1", 8, "commander:out", "commander:in",
            "supervisor:1", "command:authority", "command-room:1", 10,
            doc, 91, datetime.now(timezone.utc), 12,
        )
        reader = PostgresIncidentCommandHandoverHistoryReader(
            lambda: FakeConnection(FakeCursor(rows=[row]))
        )
        with self.assertRaises(ValueError):
            reader.read(7)


if __name__ == "__main__":
    unittest.main()
