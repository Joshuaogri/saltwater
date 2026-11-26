import unittest

from runtime.npc_dispatch import DispatchIncident
from runtime.postgres_npc_dispatch import PostgresNPCDispatchFactory


class Cursor:
    def __init__(self, row_sets):
        self.row_sets = [list(rows) for rows in row_sets]
        self.calls = []
    def execute(self, query, params=None):
        self.calls.append((query, params))
    def fetchall(self):
        return self.row_sets.pop(0)
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False


class Connection:
    def __init__(self, cursor):
        self._cursor = cursor
    def cursor(self):
        return self._cursor
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False


def staff_rows(count=8, *, unit_id="UNIT-PATROL", post_prefix="POST"):
    return [
        (
            f"PERSONNEL-{index:03d}", f"SW-{index:04d}",
            f"Officer{index}", "Example", "established", "active",
            "sworn_officer", unit_id, f"{post_prefix}-{index:03d}",
            "Police Sergeant" if index % 2 == 0 else "Patrol Officer", "sworn",
        )
        for index in range(1, count + 1)
    ]


def unit_rows(status="available"):
    return [("UNIT-PATROL", "frontline", True, 2, 4, status, ["patrol", "first_response"])]


class PostgresNPCDispatchFactoryTests(unittest.TestCase):
    def test_loads_canonical_personnel_and_membership_without_writes(self):
        cursor = Cursor([staff_rows(), unit_rows()])
        factory = PostgresNPCDispatchFactory(lambda: Connection(cursor), seed=3)
        console = factory.build(
            [DispatchIncident("INC-1", "Burglary", "patrol")],
            current_shift="Alpha",
        )
        rendered = console.execute()
        self.assertIn("INC-1", rendered)
        self.assertIn("UNIT-PATROL", rendered)
        assigned = console.execute(("assign", "INC-1"))
        self.assertIn("NPC dispatch assigned UNIT-PATROL", assigned)
        self.assertEqual(len(cursor.calls), 2)
        self.assertTrue(all(call[0].lstrip().upper().startswith("SELECT") for call in cursor.calls))
        self.assertIn("sw_police.personnel", cursor.calls[0][0])
        self.assertIn("sw_police.unit_membership", cursor.calls[0][0])
        self.assertIn("sw_player.identity_binding", cursor.calls[0][0])
        self.assertIn("NOT EXISTS", cursor.calls[0][0])
        self.assertNotIn("authorised_post p", cursor.calls[0][0])

    def test_recruits_without_post_membership_are_not_dispatchable(self):
        recruit = [(
            "PERSONNEL-RECRUIT", "SW-RECRUIT-0001", "Avery", "Recruit",
            "recruit", "active", "sworn_officer", None, None, None, None,
        )]
        cursor = Cursor([recruit, unit_rows()])
        console = PostgresNPCDispatchFactory(lambda: Connection(cursor)).build(
            [DispatchIncident("INC-RECRUIT", "Routine patrol", "patrol")],
            current_shift="Alpha",
        )
        self.assertEqual(console.process_dispatch_tick(), ())
        snapshot = console._simulator.snapshot()
        self.assertEqual(snapshot["workforce_count"], 1)
        self.assertEqual(snapshot["unassigned_npc_count"], 1)
        self.assertEqual(snapshot["available_npc_count"], 0)

    def test_no_status_history_does_not_make_staffed_unit_available(self):
        cursor = Cursor([staff_rows(), unit_rows(status="unavailable")])
        console = PostgresNPCDispatchFactory(lambda: Connection(cursor)).build(
            [DispatchIncident("INC-UNAVAILABLE", "Routine patrol", "patrol")],
            current_shift="Alpha",
        )
        self.assertEqual(console.process_dispatch_tick(), ())
        self.assertEqual(console._simulator.snapshot()["available_npc_count"], 2)

    def test_empty_personnel_does_not_invent_npc_staff_from_vacant_posts(self):
        cursor = Cursor([[], unit_rows()])
        console = PostgresNPCDispatchFactory(lambda: Connection(cursor)).build(
            [DispatchIncident("INC-EMPTY", "Routine patrol", "patrol")],
            current_shift="Alpha",
        )
        self.assertEqual(console.process_dispatch_tick(), ())
        snapshot = console._simulator.snapshot()
        self.assertEqual(snapshot["workforce_count"], 0)
        self.assertEqual(snapshot["unassigned_npc_count"], 0)
        self.assertEqual(snapshot["available_npc_count"], 0)

    def test_missing_unit_profiles_fails_as_source_configuration_problem(self):
        cursor = Cursor([[], []])
        factory = PostgresNPCDispatchFactory(lambda: Connection(cursor))
        with self.assertRaisesRegex(RuntimeError, "could not be loaded"):
            factory.build([])

    def test_database_failure_is_reported_without_writing(self):
        class BrokenConnection:
            def __enter__(self):
                raise OSError("database unavailable")
            def __exit__(self, *_):
                return False
        factory = PostgresNPCDispatchFactory(BrokenConnection)
        with self.assertRaisesRegex(RuntimeError, "could not be loaded"):
            factory.build([])


if __name__ == "__main__":
    unittest.main()
