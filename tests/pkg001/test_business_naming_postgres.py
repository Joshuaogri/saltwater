"""Disposable PostgreSQL acceptance for BP04 stable text-ID business names."""
import gzip
import hashlib
import json
import math
import os
import time
import unittest
from pathlib import Path

import psycopg

from runtime.naming import pg_trgm_similarity
from runtime.naming_inventory import inventory_geography_names
from runtime.postgres_naming import PostgresNameRegistry


ROOT = Path(__file__).resolve().parents[2]


def connect():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
    )


class BusinessNamingPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with gzip.open(
            ROOT / "data/business/saltwater-business-registry-v1.json.gz",
            "rt", encoding="utf-8",
        ) as handle:
            document = json.load(handle)
        table = document["tables"]["businesses"]
        columns = table["columns"]
        cls.rows = [dict(zip(columns, values)) for values in table["rows"]]
        cls.by_id = {row["business_id"]: row for row in cls.rows}
        naming = document["metadata"]["naming"]
        if naming.get("similarity_algorithm") != "POSTGRES_PG_TRGM_COMPATIBLE":
            raise AssertionError("business registry must use PostgreSQL-compatible similarity screening")
        if naming.get("public_name_count") != 20000:
            raise AssertionError("all 20,000 business public names must be screened")
        manifest = {
            "dataset_id": "SW-BUSINESS-REGISTRY-V1",
            "generator_version": naming["generator_version"],
            "normalizer_version": 1,
            "config_version": naming["vocabulary_config_version"],
            "seed": naming["seed"],
            "trading_names": [row["trading_name"] for row in cls.rows],
            "registered_names": [row["registered_name"] for row in cls.rows],
        }
        cls.manifest_digest = hashlib.sha256(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).digest()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """INSERT INTO sw_property.business
                       (business_id,display_name,sector,primary_activity,status,
                        source_dataset,source_record)
                       VALUES (%s,%s,%s,%s,%s,'SW-BUSINESS-REGISTRY-V1',%s::jsonb)""",
                    [
                        (
                            row["business_id"], row["trading_name"], row["sector"],
                            row["primary_activity"], row["status"], json.dumps(row, ensure_ascii=False),
                        )
                        for row in cls.rows
                    ],
                )
                cur.execute(
                    """SELECT sw_names.record_generation_batch(
                         'BUSINESS'::text,1::smallint,1::smallint,%s::text,
                         20261126::bigint,%s::bytea,10000::integer,
                         'SW-BUSINESS-REGISTRY-V1'::text,'ci-business-naming'::text,
                         'BP04 bulk naming acceptance'::text)""",
                    (naming["vocabulary_config_version"], cls.manifest_digest),
                )
                cls.batch_id = cur.fetchone()[0]
                # Diagnose the exact source of any database near-duplicate
                # rejection before attempting the expensive reservation batch.
                cur.execute(
                    """CREATE TEMP TABLE bp04_name_preflight (
                         ordinal integer NOT NULL,
                         business_id text NOT NULL,
                         name_form text NOT NULL,
                         display_name text NOT NULL,
                         normalized_key text NOT NULL
                       ) ON COMMIT DROP"""
                )
                preflight_rows = []
                for row in cls.rows:
                    preflight_rows.extend((
                        (len(preflight_rows) + 1, row["business_id"], "trading",
                         row["trading_name"], row["trading_name"]),
                        (len(preflight_rows) + 2, row["business_id"], "legal",
                         row["registered_name"], row["registered_name"]),
                    ))
                cur.executemany(
                    """INSERT INTO bp04_name_preflight
                       (ordinal,business_id,name_form,display_name,normalized_key)
                       VALUES (%s,%s,%s,%s,sw_names.normalize_name(%s))""",
                    preflight_rows,
                )
                cur.execute(
                    "CREATE INDEX bp04_name_preflight_trgm_idx "
                    "ON bp04_name_preflight USING gin(normalized_key sw_names.gin_trgm_ops)"
                )
                cur.execute("ANALYZE bp04_name_preflight")
                cur.execute(
                    """SELECT c.business_id,c.name_form,c.display_name,
                              r.entity_type,r.entity_ref,r.entity_id,r.display_name,
                              sw_names.similarity(c.normalized_key,r.normalized_key)
                       FROM bp04_name_preflight c
                       JOIN LATERAL (
                         SELECT r.entity_type,r.entity_ref,r.entity_id,r.display_name,
                                r.normalized_key
                         FROM sw_names.name_reservation r
                         WHERE r.normalized_key OPERATOR(sw_names.%) c.normalized_key
                           AND r.normalized_key <> c.normalized_key
                         ORDER BY sw_names.similarity(c.normalized_key,r.normalized_key) DESC
                         LIMIT 1
                       ) r ON sw_names.similarity(c.normalized_key,r.normalized_key)>0.90
                       ORDER BY 8 DESC LIMIT 20"""
                )
                existing_conflicts = cur.fetchall()
                cur.execute(
                    """SELECT a.business_id,a.name_form,a.display_name,
                              b.business_id,b.name_form,b.display_name,
                              sw_names.similarity(a.normalized_key,b.normalized_key)
                       FROM bp04_name_preflight a
                       JOIN bp04_name_preflight b
                         ON a.ordinal < b.ordinal
                        AND b.normalized_key OPERATOR(sw_names.%) a.normalized_key
                       WHERE sw_names.similarity(a.normalized_key,b.normalized_key)>0.90
                       ORDER BY 7 DESC LIMIT 20"""
                )
                batch_conflicts = cur.fetchall()
                if existing_conflicts or batch_conflicts:
                    raise AssertionError(
                        "PostgreSQL near-duplicate preflight failed; "
                        f"existing_namespace_conflicts={existing_conflicts!r}; "
                        f"within_business_batch_conflicts={batch_conflicts!r}"
                    )
                # Refresh pg_trgm GIN selectivity statistics before the 20,000
                # reservation acceptance; stale stats can force repeated scans.
                cur.execute("ANALYZE sw_names.name_reservation")

    def reserve(self, business_id, name, name_form="trading", batch_id=None):
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT sw_names.reserve_business_name(
                         %s,%s,%s,'SW-BUSINESS-REGISTRY-V1','ci-business-naming',
                         'BP04 disposable name reservation',0,%s)""",
                    (business_id, name_form, name, batch_id),
                )
                return cur.fetchone()[0]


    def test_opening_person_business_and_geography_names_share_one_collision_screen(self):
        """Preflight the committed opening cohorts together, not just within each source."""
        police_path = ROOT / "data/people/saltwater-opening-police-person-seed-v1.json"
        civilian_path = ROOT / "data/people/saltwater-opening-civilian-resident-seed-v1.json.gz"
        geography_path = ROOT / "data/geography/saltwater-geography-v1.json"

        police = json.loads(police_path.read_text(encoding="utf-8"))["records"]
        with gzip.open(civilian_path, "rt", encoding="utf-8") as handle:
            civilians = json.load(handle)["records"]
        geography_payload = json.loads(geography_path.read_text(encoding="utf-8"))
        geography = inventory_geography_names(geography_payload).candidates

        self.assertEqual(len(police), 500)
        self.assertEqual(len(civilians), 9000)
        self.assertEqual(len(geography), 102)
        self.assertEqual(len(self.rows), 10000)

        entries = []
        for item in geography:
            entries.append(("GEOGRAPHY", item.source_id, "canonical", item.display_name))
        for item in police:
            entries.append(("PERSON", item["candidate_ref"], "canonical", item["display_name"]))
        for item in civilians:
            entries.append(("PERSON", item["candidate_ref"], "canonical", item["display_name"]))
        for item in self.rows:
            entries.append(("BUSINESS", item["business_id"], "trading", item["trading_name"]))
            entries.append(("BUSINESS", item["business_id"], "legal", item["registered_name"]))

        self.assertEqual(len(entries), 29602)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SET LOCAL pg_trgm.similarity_threshold='0.90'")
                cur.execute(
                    """CREATE TEMP TABLE bp04_global_name_preflight (
                         ordinal integer PRIMARY KEY,
                         entity_type text NOT NULL,
                         entity_ref text NOT NULL,
                         name_form text NOT NULL,
                         display_name text NOT NULL,
                         normalized_key text NOT NULL
                       ) ON COMMIT DROP"""
                )
                cur.executemany(
                    """INSERT INTO bp04_global_name_preflight
                       (ordinal,entity_type,entity_ref,name_form,display_name,normalized_key)
                       VALUES (%s,%s,%s,%s,%s,sw_names.normalize_name(%s))""",
                    [
                        (index, entity_type, entity_ref, name_form, display_name, display_name)
                        for index, (entity_type, entity_ref, name_form, display_name)
                        in enumerate(entries, start=1)
                    ],
                )
                cur.execute(
                    "CREATE INDEX bp04_global_name_preflight_key_idx "
                    "ON bp04_global_name_preflight(normalized_key)"
                )
                cur.execute(
                    "CREATE INDEX bp04_global_name_preflight_trgm_idx "
                    "ON bp04_global_name_preflight USING gin(normalized_key sw_names.gin_trgm_ops)"
                )
                cur.execute("ANALYZE bp04_global_name_preflight")
                cur.execute(
                    """SELECT entity_type,count(*)
                       FROM bp04_global_name_preflight
                       GROUP BY entity_type ORDER BY entity_type"""
                )
                counts = dict(cur.fetchall())
                self.assertEqual(counts, {"BUSINESS": 20000, "GEOGRAPHY": 102, "PERSON": 9500})

                cur.execute(
                    """SELECT a.entity_type,a.entity_ref,a.display_name,
                              b.entity_type,b.entity_ref,b.display_name
                       FROM bp04_global_name_preflight a
                       JOIN bp04_global_name_preflight b
                         ON a.ordinal < b.ordinal
                        AND a.normalized_key=b.normalized_key
                       WHERE NOT (
                         a.normalized_key='saltwater'
                         AND a.entity_type='GEOGRAPHY' AND b.entity_type='GEOGRAPHY'
                         AND a.entity_ref IN ('saltwater-state','saltwater-city')
                         AND b.entity_ref IN ('saltwater-state','saltwater-city')
                         AND a.entity_ref<>b.entity_ref
                       )
                       ORDER BY a.ordinal,b.ordinal LIMIT 20"""
                )
                exact_conflicts = cur.fetchall()
                self.assertEqual(exact_conflicts, [], f"global exact-name collisions: {exact_conflicts!r}")

                cur.execute(
                    """SELECT a.entity_type,a.entity_ref,a.display_name,
                              b.entity_type,b.entity_ref,b.display_name,
                              sw_names.similarity(a.normalized_key,b.normalized_key)
                       FROM bp04_global_name_preflight a
                       JOIN bp04_global_name_preflight b
                         ON a.entity_type < b.entity_type
                        AND b.normalized_key<>a.normalized_key
                        AND b.normalized_key OPERATOR(sw_names.%) a.normalized_key
                       WHERE sw_names.similarity(a.normalized_key,b.normalized_key)>0.90
                       ORDER BY 7 DESC LIMIT 20"""
                )
                near_conflicts = cur.fetchall()
                self.assertEqual(near_conflicts, [], f"global near-duplicate review cases: {near_conflicts!r}")

    def test_business_reservation_uses_advisory_lock_before_owner_row_lock(self):
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT pg_get_functiondef(
                         'sw_names.reserve_business_name(text,text,text,text,text,text,bigint,bigint)'::regprocedure
                       )"""
                )
                definition = cur.fetchone()[0]
        advisory_lock = definition.find("pg_advisory_xact_lock")
        owner_row_lock = definition.find("FOR UPDATE")
        self.assertGreaterEqual(advisory_lock, 0)
        self.assertGreater(owner_row_lock, advisory_lock)
        self.assertNotIn("LOCK TABLE sw_names.name_reservation", definition)

    def test_source_business_ids_remain_stable_text_keys(self):
        ids = [row["business_id"] for row in self.rows]
        self.assertEqual(len(ids), 10000)
        self.assertTrue(all(isinstance(value, str) for value in ids))
        self.assertEqual(ids[0], "SWBIZ-000001")
        self.assertEqual(ids[-1], "SWBIZ-010000")
        self.assertEqual(len(ids), len(set(ids)))

    def test_bulk_reserves_10000_trading_and_legal_names(self):
        reservations = []
        for row in self.rows:
            reservations.extend((
                (row["business_id"], "trading", row["trading_name"], self.batch_id),
                (row["business_id"], "legal", row["registered_name"], self.batch_id),
            ))
        with connect() as conn:
            registry = PostgresNameRegistry(conn)
            reservation_count = 0
            # PostgreSQL advisory/name locks are transaction-scoped. Keep each
            # write transaction bounded, as a resumable production importer must.
            chunk_size = 500
            write_started = time.perf_counter()
            for offset in range(0, len(reservations), chunk_size):
                chunk = reservations[offset:offset + chunk_size]
                reservation_count += registry.reserve_business_batch(
                    ((business_id, form, display_name) for business_id, form, display_name, _ in chunk),
                    source_ref="SW-BUSINESS-REGISTRY-V1",
                    actor_ref="ci-business-naming",
                    reason="BP04 bulk name reservation acceptance",
                    effective_tick=0,
                    generation_batch_id=self.batch_id,
                )
                if offset == 0:
                    with conn.cursor() as cur:
                        cur.execute(
                            """SELECT count(*) FROM pg_locks
                               WHERE pid=pg_backend_pid() AND locktype='advisory' AND granted"""
                        )
                        self.assertGreaterEqual(cur.fetchone()[0], 1)
                        cur.execute(
                            """SELECT count(*) FROM pg_locks
                               WHERE pid=pg_backend_pid()
                                 AND relation='sw_names.name_reservation'::regclass
                                 AND mode='ShareRowExclusiveLock'"""
                        )
                        self.assertEqual(cur.fetchone()[0], 0)
                conn.commit()
            self.assertEqual(reservation_count, 20000)
            write_elapsed = time.perf_counter() - write_started
            print(
                "BP04 persistent business-name writes: "
                f"{reservation_count} reservations in {write_elapsed:.3f}s "
                f"({reservation_count / write_elapsed:.1f} reservations/s)"
            )
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT count(*) FILTER (WHERE name_form='trading'),
                              count(*) FILTER (WHERE name_form='legal'),
                              count(DISTINCT entity_ref),
                              count(*) FILTER (WHERE entity_id IS NOT NULL)
                       FROM sw_names.name_reservation
                       WHERE entity_type='BUSINESS'""",
                )
                trading, legal, owners, numeric_ids = cur.fetchone()
                self.assertEqual(trading, 10000)
                self.assertEqual(legal, 10000)
                self.assertEqual(owners, 10000)
                self.assertEqual(numeric_ids, 0)
                cur.execute(
                    """SELECT count(*) FROM sw_names.search_business_name(%s)""",
                    (self.rows[0]["trading_name"],),
                )
                self.assertEqual(cur.fetchone()[0], 1)

    def test_database_business_name_and_identity_lookup_performance_budget(self):
        """Measure indexed database lookups after the 20,000-name reservation batch."""
        name_latencies_ms = []
        business_latencies_ms = []
        with connect() as conn:
            with conn.cursor() as cur:
                for index in range(1000):
                    business = self.rows[(index * 7919) % len(self.rows)]
                    started = time.perf_counter_ns()
                    cur.execute(
                        "SELECT * FROM sw_names.search_business_name(%s)",
                        (business["trading_name"],),
                    )
                    result = cur.fetchone()
                    name_latencies_ms.append((time.perf_counter_ns() - started) / 1_000_000)
                    self.assertIsNotNone(result)
                    self.assertEqual(result[1], "BUSINESS")
                    self.assertEqual(result[2], business["business_id"])
                    self.assertEqual(result[3], "trading")
                    self.assertFalse(result[6])

                    started = time.perf_counter_ns()
                    cur.execute(
                        """SELECT business_id,display_name,sector,status
                           FROM sw_property.business WHERE business_id=%s""",
                        (business["business_id"],),
                    )
                    business_result = cur.fetchone()
                    business_latencies_ms.append((time.perf_counter_ns() - started) / 1_000_000)
                    self.assertIsNotNone(business_result)
                    self.assertEqual(business_result[0], business["business_id"])

        def percentile(values, quantile):
            ordered = sorted(values)
            return ordered[math.ceil(quantile * len(ordered)) - 1]

        name_p95 = percentile(name_latencies_ms, 0.95)
        name_p99 = percentile(name_latencies_ms, 0.99)
        business_p95 = percentile(business_latencies_ms, 0.95)
        business_p99 = percentile(business_latencies_ms, 0.99)
        print(
            "BP04 PostgreSQL exact-name search, 1,000 queries: "
            f"p50={percentile(name_latencies_ms, 0.50):.3f}ms "
            f"p95={name_p95:.3f}ms p99={name_p99:.3f}ms "
            f"max={max(name_latencies_ms):.3f}ms"
        )
        print(
            "BP04 PostgreSQL business-ID lookup, 1,000 queries: "
            f"p50={percentile(business_latencies_ms, 0.50):.3f}ms "
            f"p95={business_p95:.3f}ms p99={business_p99:.3f}ms "
            f"max={max(business_latencies_ms):.3f}ms"
        )
        self.assertLessEqual(name_p95, 25.0)
        self.assertLessEqual(name_p99, 50.0)
        self.assertLessEqual(business_p95, 25.0)
        self.assertLessEqual(business_p99, 50.0)

    def test_python_similarity_matches_postgresql_pg_trgm(self):
        pairs = (
            ("Cobalt Harbour Logistics Review", "Cobalt Harbour Logistics Reviews"),
            ("Amber Meridian Trading", "Amber Meridian Trading Limited"),
            ("Northbank Civic Services", "Northbank Civic Service"),
            ("Quayside Orchard House", "Quayside Orchard House"),
        )
        with connect() as conn:
            with conn.cursor() as cur:
                for left, right in pairs:
                    cur.execute(
                        """SELECT sw_names.similarity(sw_names.normalize_name(%s),sw_names.normalize_name(%s)),
                                  sw_names.show_trgm(sw_names.normalize_name(%s)),
                                  sw_names.show_trgm(sw_names.normalize_name(%s))""",
                        (left, right, left, right),
                    )
                    database_similarity, left_trigrams, right_trigrams = cur.fetchone()
                    self.assertAlmostEqual(
                        pg_trgm_similarity(left, right), database_similarity, places=6,
                        msg=(
                            f"similarity mismatch for {left!r} / {right!r}; "
                            f"database_trigrams={left_trigrams!r}/{right_trigrams!r}"
                        ),
                    )

    def test_unknown_business_identity_fails_closed(self):
        with self.assertRaises(psycopg.Error):
            self.reserve("SWBIZ-NOT-REGISTERED", "Unregistered Meridian Trading")

    def test_exact_name_collision_between_businesses_is_rejected(self):
        name = "Civic Quayside Registry Test"
        self.reserve(self.rows[1]["business_id"], name)
        with self.assertRaises(psycopg.Error):
            self.reserve(self.rows[2]["business_id"], name)

    def test_idempotent_retry_returns_same_reservation(self):
        business_id = self.rows[3]["business_id"]
        name = "Harbour Lantern Idempotency Test"
        first = self.reserve(business_id, name)
        second = self.reserve(business_id, name)
        self.assertEqual(first, second)

    def test_trading_and_legal_names_cannot_reuse_one_global_key(self):
        business_id = self.rows[4]["business_id"]
        name = "Westgate Orchard Single Key Test"
        self.reserve(business_id, name, "trading")
        with self.assertRaises(psycopg.Error):
            self.reserve(business_id, name, "legal")

    def test_near_duplicate_requires_review(self):
        original = "Cobalt Harbour Logistics Review"
        candidate = "Cobalt Harbour Logistics Reviews"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT sw_names.similarity(sw_names.normalize_name(%s),sw_names.normalize_name(%s))",
                    (original, candidate),
                )
                similarity = cur.fetchone()[0]
        self.assertGreaterEqual(similarity, 0.90)
        self.reserve(self.rows[5]["business_id"], original)
        with self.assertRaises(psycopg.Error):
            self.reserve(self.rows[6]["business_id"], candidate)

    def test_transaction_rollback_removes_business_and_its_reservation(self):
        business_id = "SWBIZ-ROLLBACK-TEST"
        name = "Rollback Only Meridian Trading"
        conn = connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO sw_property.business
                       (business_id,display_name,sector,status,source_dataset,source_record)
                       VALUES (%s,%s,'test','active','SW-NAM-ROLLBACK','{}'::jsonb)""",
                    (business_id, name),
                )
                cur.execute(
                    """SELECT sw_names.reserve_business_name(
                         %s,'trading',%s,'SW-NAM-ROLLBACK','ci-test',
                         'rollback acceptance',0,NULL)""",
                    (business_id, name),
                )
                self.assertIsNotNone(cur.fetchone()[0])
            conn.rollback()
        finally:
            conn.close()
        with connect() as check:
            with check.cursor() as cur:
                cur.execute("SELECT count(*) FROM sw_property.business WHERE business_id=%s", (business_id,))
                self.assertEqual(cur.fetchone()[0], 0)
                cur.execute("SELECT count(*) FROM sw_names.name_reservation WHERE entity_ref=%s", (business_id,))
                self.assertEqual(cur.fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
