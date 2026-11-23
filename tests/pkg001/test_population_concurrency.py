import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

import psycopg


class PopulationCapConcurrencyTests(unittest.TestCase):
    def test_two_simultaneous_admissions_at_9999_allow_exactly_one(self):
        def connect():
            return psycopg.connect(
                host=os.environ["PGHOST"],
                port=os.environ["PGPORT"],
                user=os.environ["PGUSER"],
                password=os.environ["PGPASSWORD"],
                dbname=os.environ["PGDATABASE"],
            )

        barrier = threading.Barrier(2)

        def attempt(number):
            conn = connect()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick) "
                            "SELECT event_type_id,now(),0 FROM sw_core.event_type "
                            "WHERE event_code='PERSON_CREATED' RETURNING event_id"
                        )
                        created_event = cur.fetchone()[0]
                        cur.execute(
                            "INSERT INTO sw_people.person(given_name,family_name,created_tick,last_event_id) "
                            "VALUES ('Concurrent','Attempt-'||%s,0,%s) RETURNING person_id",
                            (number, created_event),
                        )
                        person_id = cur.fetchone()[0]
                        cur.execute(
                            "INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick) "
                            "SELECT event_type_id,now(),0 FROM sw_core.event_type "
                            "WHERE event_code='POPULATION_STATE_CHANGED' RETURNING event_id"
                        )
                        population_event = cur.fetchone()[0]
                        barrier.wait(timeout=15)
                        cur.execute(
                            "INSERT INTO sw_people.population_state "
                            "(person_id,life_status,scope_status,effective_tick,last_event_id) "
                            "VALUES (%s,1,1,0,%s)",
                            (person_id, population_event),
                        )
                return "admitted"
            except psycopg.Error as exc:
                return f"rejected:{exc.sqlstate}"
            finally:
                conn.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, (1, 2)))

        self.assertEqual(outcomes.count("admitted"), 1, outcomes)
        self.assertEqual(sum(x.startswith("rejected:") for x in outcomes), 1, outcomes)
        conn = connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT living_included FROM sw_people.population_counter WHERE singleton=1")
                self.assertEqual(cur.fetchone()[0], 10000)
                cur.execute("SELECT count(*) FROM sw_people.population_state WHERE life_status=1 AND scope_status=1")
                self.assertEqual(cur.fetchone()[0], 10000)
                cur.execute("SELECT count(*) FROM sw_people.person")
                self.assertEqual(cur.fetchone()[0], 10000)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
