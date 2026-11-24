"""Disposable PostgreSQL race/rollback tests for the authoritative name registry."""
import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import psycopg


def connect():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
    )


class NamingPostgresConcurrencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entity_ids = []
        with connect() as conn:
            with conn.cursor() as cur:
                for _ in range(4):
                    cur.execute(
                        "INSERT INTO sw_geo.entity(entity_code,kind) VALUES (%s,7) RETURNING spatial_id",
                        (f"sw-nam-concurrency-{uuid4()}",),
                    )
                    cls.entity_ids.append(cur.fetchone()[0])

    def reserve(self, entity_id, name):
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT sw_names.reserve_name(
                             'GEOGRAPHY',%s,'canonical',%s,
                             'sw-nam-concurrency-test','ci-test',
                             'concurrent reservation acceptance',0)""",
                        (entity_id, name),
                    )
                    return ("ok", cur.fetchone()[0])
        except psycopg.errors.UniqueViolation:
            return ("collision", None)
        except psycopg.Error as exc:
            if exc.sqlstate in {"23505", "P0001"} and (
                "name is already permanently reserved" in str(exc)
                or exc.sqlstate == "23505"
            ):
                return ("collision", None)
            raise

    def test_two_concurrent_reservations_for_same_name_have_one_winner(self):
        barrier = threading.Barrier(2)

        def attempt(entity_id):
            barrier.wait(timeout=15)
            return self.reserve(entity_id, "Concurrent Registry Road")

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, self.entity_ids[:2]))
        self.assertEqual([x[0] for x in outcomes].count("ok"), 1, outcomes)
        self.assertEqual([x[0] for x in outcomes].count("collision"), 1, outcomes)

    def test_concurrent_different_names_both_succeed(self):
        barrier = threading.Barrier(2)

        def attempt(args):
            entity_id, name = args
            barrier.wait(timeout=15)
            return self.reserve(entity_id, name)

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, (
                (self.entity_ids[2], "Concurrent East Registry Road"),
                (self.entity_ids[3], "Concurrent West Registry Road"),
            )))
        self.assertEqual([x[0] for x in outcomes], ["ok", "ok"])

    def test_idempotent_retry_returns_original_reservation(self):
        entity_id = self.entity_ids[0]
        first = self.reserve(entity_id, "Idempotent Registry Road")
        second = self.reserve(entity_id, "Idempotent Registry Road")
        self.assertEqual(first, second)

    def test_failed_entity_creation_transaction_rolls_back_name_reservation(self):
        entity_id = self.entity_ids[1]
        with self.assertRaises(RuntimeError):
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT sw_names.reserve_name(
                             'GEOGRAPHY',%s,'canonical','Rollback Registry Road',
                             'sw-nam-rollback-test','ci-test','rollback acceptance',0)""",
                        (entity_id,),
                    )
                    raise RuntimeError("simulated domain creation failure")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT count(*) FROM sw_names.name_reservation WHERE normalized_key='rollback registry road'"
                )
                self.assertEqual(cur.fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
