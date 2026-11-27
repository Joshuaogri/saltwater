"""Disposable PostgreSQL preflight of all 9,000 opening civilian names.

The canonical person rows and SW-UNS reservations are created inside one
transaction and rolled back. The 500-person police cohort is checked for exact
normalized-name overlap in memory; its separate PostgreSQL preflight remains
in the same workflow.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
import unittest

import psycopg

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / "data/people/saltwater-opening-civilian-resident-seed-v1.json.gz"
POLICE_PATH = ROOT / "data/people/saltwater-opening-police-person-seed-v1.json"


def connect():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
    )


class OpeningCivilianPersonNameRegistryPostgresTests(unittest.TestCase):
    def test_all_9000_candidates_reserve_against_global_registry(self):
        with gzip.open(SEED_PATH, "rt", encoding="utf-8") as stream:
            payload = json.load(stream)
        police = json.loads(POLICE_PATH.read_text(encoding="utf-8"))
        rows = payload["records"]
        police_rows = police["records"]
        self.assertEqual(payload["dataset_id"], "SW-OPENING-CIVILIAN-RESIDENT-SEED-V1")
        self.assertEqual(len(rows), 9000)
        self.assertEqual(payload["candidate_count"], 9000)
        self.assertEqual(len(police_rows), 500)

        # Verify the source manifest before it is registered in SW-UNS.
        manifest = dict(payload)
        digest = manifest.pop("manifest_sha256")
        canonical = json.dumps(
            manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), digest)

        def key(value):
            return " ".join(value.casefold().split())

        civilian_keys = [key(row["display_name"]) for row in rows]
        police_keys = {key(row["display_name"]) for row in police_rows}
        self.assertEqual(len(set(civilian_keys)), 9000)
        self.assertFalse(set(civilian_keys) & police_keys)
        self.assertEqual(
            payload["population_reconciliation"],
            {
                "civilian_usual_residents": 9000,
                "active_police_service_people": 500,
                "distinct_opening_people_target": 9500,
                "hard_population_cap": 10000,
                "unused_opening_headroom": 500,
            },
        )

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
                         %s,'ci-opening-civilian-seed',
                         'Verify all 9,000 opening civilian names against SW-UNS')""",
                    (
                        payload["generator_version"],
                        payload["normalizer_version"],
                        payload["config_version"],
                        payload["seed"],
                        digest,
                        payload["candidate_count"],
                        payload["dataset_id"],
                    ),
                )
                batch_id = cur.fetchone()[0]
                cur.execute(
                    "SELECT set_config('sw_names.generation_batch_id', %s, true)",
                    (str(batch_id),),
                )
                cur.execute(
                    "SELECT event_type_id FROM sw_core.event_type WHERE event_code='PERSON_CREATED'"
                )
                event_type = cur.fetchone()
                self.assertIsNotNone(event_type, "PERSON_CREATED event type must exist")

                cur.execute(
                    """CREATE TEMP TABLE bp03_civilian_seed_stage (
                         candidate_ref text PRIMARY KEY,
                         source_ref text UNIQUE NOT NULL,
                         given_name text NOT NULL,
                         middle_name text NOT NULL,
                         family_name text NOT NULL,
                         normalized_name text GENERATED ALWAYS AS
                           (sw_names.normalize_name(concat_ws(' ',given_name,middle_name,family_name))) STORED
                       ) ON COMMIT DROP"""
                )
                cur.executemany(
                    """INSERT INTO bp03_civilian_seed_stage
                       (candidate_ref,source_ref,given_name,middle_name,family_name)
                       VALUES (%s,%s,%s,%s,%s)""",
                    [
                        (
                            row["candidate_ref"], row["source_ref"],
                            row["given_name"], row["middle_name"], row["family_name"],
                        )
                        for row in rows
                    ],
                )
                # Validate the complete generated cohort once before any reservations.
                # The trigger then checks the existing global registry without repeatedly
                # comparing each new row to all earlier rows from this same manifest.
                cur.execute("CREATE INDEX bp03_civilian_seed_trgm_idx ON bp03_civilian_seed_stage USING gin(normalized_name sw_names.gin_trgm_ops)")
                cur.execute("SET LOCAL pg_trgm.similarity_threshold='0.90'")
                cur.execute(
                    """SELECT EXISTS (
                         SELECT 1
                         FROM bp03_civilian_seed_stage a
                         JOIN bp03_civilian_seed_stage b
                           ON a.candidate_ref < b.candidate_ref
                          AND a.normalized_name % b.normalized_name
                       )"""
                )
                self.assertFalse(cur.fetchone()[0], "civilian batch contains near-duplicate canonical names")
                cur.execute(
                    """SELECT EXISTS (
                         SELECT 1
                         FROM bp03_civilian_seed_stage c
                         JOIN sw_names.name_reservation r
                           ON r.normalized_key % c.normalized_name
                         WHERE r.normalized_key <> c.normalized_name
                       )"""
                )
                self.assertFalse(cur.fetchone()[0], "civilian names conflict with existing global SW-UNS reservations")
                cur.execute(
                    """CREATE TEMP TABLE bp03_civilian_seed_event_map (
                         source_ref text PRIMARY KEY,
                         event_id bigint UNIQUE NOT NULL
                       ) ON COMMIT DROP"""
                )
                cur.execute(
                    """WITH created AS (
                         INSERT INTO sw_core.simulation_event(
                           event_type_id,occurred_at,world_tick,subject_kind,subject_id,
                           source_ref,attributes,idempotency_key
                         )
                         SELECT %s,clock_timestamp(),0,'person',NULL,s.source_ref,
                           jsonb_build_object('seed_candidate_ref',s.candidate_ref),
                           s.source_ref
                         FROM bp03_civilian_seed_stage s
                         ORDER BY s.candidate_ref
                         RETURNING event_id,source_ref
                       )
                       INSERT INTO bp03_civilian_seed_event_map(source_ref,event_id)
                       SELECT source_ref,event_id FROM created""",
                    (event_type[0],),
                )
                cur.execute(
                    """INSERT INTO sw_people.person(
                         given_name,middle_name,family_name,created_tick,source_ref,last_event_id
                       )
                       SELECT s.given_name,s.middle_name,s.family_name,0,s.source_ref,e.event_id
                       FROM bp03_civilian_seed_stage s
                       JOIN bp03_civilian_seed_event_map e USING(source_ref)
                       ORDER BY s.candidate_ref"""
                )
                self.assertEqual(cur.rowcount, 9000)

                cur.execute(
                    """SELECT count(*),count(DISTINCT entity_id),count(DISTINCT normalized_key)
                       FROM sw_names.name_reservation
                       WHERE entity_type='PERSON' AND generation_batch_id=%s""",
                    (batch_id,),
                )
                reserved, identities, distinct_names = cur.fetchone()
                self.assertEqual((reserved, identities, distinct_names), (9000, 9000, 9000))

                cur.execute(
                    """SELECT count(*)
                       FROM sw_people.person p
                       JOIN bp03_civilian_seed_stage s USING(source_ref)
                       LEFT JOIN sw_names.name_reservation r
                         ON r.entity_type='PERSON' AND r.entity_id=p.person_id
                        AND r.generation_batch_id=%s
                       WHERE r.reservation_id IS NULL""",
                    (batch_id,),
                )
                self.assertEqual(cur.fetchone()[0], 0, "every candidate must have a canonical SW-UNS reservation")

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
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    unittest.main()
