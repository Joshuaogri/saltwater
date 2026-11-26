"""Disposable PostgreSQL check of the 500 opening police candidate names.

Creates temporary canonical person rows and reserves their names inside one
transaction, then rolls everything back. This tests the real SW-UNS registry
against geography and business reservations without seeding production data.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

import psycopg


ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / "data/people/saltwater-opening-police-person-seed-v1.json"


def connect():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
    )


class OpeningPolicePersonNameRegistryPostgresTests(unittest.TestCase):
    def test_all_500_candidates_reserve_against_current_global_registry(self):
        payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        rows = payload["records"]
        self.assertEqual(payload["dataset_id"], "SW-OPENING-POLICE-PERSON-SEED-V1")
        self.assertEqual(len(rows), 500)

        conn = connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE sw_runtime.state
                       SET state=1,player_present=false
                       WHERE singleton=1 AND state=0
                         AND bootstrap_open=true AND world_tick=0"""
                )
                cur.execute(
                    """SELECT 1 FROM sw_runtime.state
                       WHERE singleton=1 AND state=1 AND player_present=false
                         AND bootstrap_open=true AND world_tick=0"""
                )
                self.assertIsNotNone(cur.fetchone(), "tick-zero bootstrap must be ready")

                cur.execute(
                    """SELECT sw_names.record_generation_batch(
                         'PERSON',%s,%s,%s,%s,decode(%s,'hex'),%s,
                         %s,'ci-opening-person-seed',
                         'Verify opening person names against the full SW-UNS registry')""",
                    (
                        payload["generator_version"],
                        payload["normalizer_version"],
                        payload["config_version"],
                        payload["seed"],
                        payload["manifest_sha256"],
                        payload["candidate_count"],
                        payload["dataset_id"],
                    ),
                )
                batch_id = cur.fetchone()[0]
                # The person-name AFTER INSERT trigger creates the canonical
                # reservation before the explicit idempotent call below. Supply
                # the manifest in transaction-local context so that first write
                # receives the batch provenance.
                cur.execute(
                    "SELECT set_config('sw_names.generation_batch_id', %s, true)",
                    (str(batch_id),),
                )

                cur.execute(
                    "SELECT event_type_id FROM sw_core.event_type WHERE event_code='PERSON_CREATED'"
                )
                event_type = cur.fetchone()
                self.assertIsNotNone(event_type, "PERSON_CREATED event type must exist")
                event_type_id = event_type[0]

                created_ids = []
                reservation_ids = []
                for row in rows:
                    cur.execute(
                        """INSERT INTO sw_core.simulation_event(
                             event_type_id,occurred_at,world_tick,subject_kind,subject_id,
                             source_ref,attributes,idempotency_key
                           ) VALUES (
                             %s,clock_timestamp(),0,'person',NULL,%s,
                             jsonb_build_object('seed_candidate_ref',%s::text),
                             %s
                           ) RETURNING event_id""",
                        (
                            event_type_id,
                            row["source_ref"],
                            row["candidate_ref"],
                            row["source_ref"],
                        ),
                    )
                    event_id = cur.fetchone()[0]
                    cur.execute(
                        """INSERT INTO sw_people.person(
                             given_name,middle_name,family_name,created_tick,
                             source_ref,last_event_id
                           ) VALUES (%s,%s,%s,0,%s,%s)
                           RETURNING person_id""",
                        (
                            row["given_name"],
                            row["middle_name"],
                            row["family_name"],
                            row["source_ref"],
                            event_id,
                        ),
                    )
                    person_id = cur.fetchone()[0]
                    created_ids.append(person_id)
                    cur.execute(
                        """SELECT sw_names.reserve_name(
                             'PERSON',%s,'canonical',%s,%s,
                             'ci-opening-person-seed',
                             'Opening police person seed SW-UNS collision preflight',
                             0,%s)""",
                        (
                            person_id,
                            row["display_name"],
                            row["source_ref"],
                            batch_id,
                        ),
                    )
                    reservation_ids.append(cur.fetchone()[0])

                self.assertEqual(len(created_ids), 500)
                self.assertEqual(len(set(created_ids)), 500)
                self.assertEqual(len(reservation_ids), 500)
                self.assertEqual(len(set(reservation_ids)), 500)

                cur.execute(
                    """SELECT count(*)
                       FROM sw_names.name_reservation
                       WHERE entity_type='PERSON'
                         AND generation_batch_id=%s""",
                    (batch_id,),
                )
                self.assertEqual(cur.fetchone()[0], 500)

                cur.execute(
                    """SELECT count(*) FROM sw_names.name_reservation r
                       WHERE r.generation_batch_id=%s
                         AND r.normalized_key IN (
                           SELECT normalized_key FROM sw_names.name_reservation
                           WHERE generation_batch_id=%s
                           GROUP BY normalized_key HAVING count(*)>1
                         )""",
                    (batch_id, batch_id),
                )
                self.assertEqual(cur.fetchone()[0], 0)
        finally:
            # The acceptance is a registry preflight, not a persistent import.
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    unittest.main()
