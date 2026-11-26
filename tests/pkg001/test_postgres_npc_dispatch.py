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


class PostgresNPCDispatchFactoryTests(unittest.TestCase):
    def test_loads_canonical_posts_and_units_without_writes(self):
        posts = [
            (f"P-{i:03d}", "UNIT-PATROL", "Police Sergeant" if i == 1 else "Patrol Officer")
            for i in range(1, 17)
        ]
        units = [
            ("UNIT-PATROL", "frontline", True, 2, 4, "available", ["patrol", "first_response"])
        ]
        cursor = Cursor([posts, units])
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

    def test_missing_posts_fails_as_source_configuration_problem(self):
        cursor = Cursor([[], [("UNIT-PATROL", "frontline", True, 2, 4, "available", ["patrol"]) ]])
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
