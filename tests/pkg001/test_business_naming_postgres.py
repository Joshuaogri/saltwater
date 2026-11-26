"""Disposable PostgreSQL acceptance for BP04 stable text-ID business names."""
import hashlib
import json
import os
import unittest
from pathlib import Path

import psycopg


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
        document = json.loads(
            (ROOT / "data/business/saltwater-business-registry-v1.json").read_text(encoding="utf-8")
        )
        table = document["tables"]["businesses"]
        columns = table["columns"]
        cls.rows = [dict(zip(columns, values)) for values in table["rows"]]
        cls.by_id = {row["business_id"]: row for row in cls.rows}
        naming = document["metadata"]["naming"]
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
                         'BUSINESS',1,1,%s,20261126,%s,10000,
                         'SW-BUSINESS-REGISTRY-V1','ci-business-naming',
                         'BP04 bulk naming acceptance')""",
                    (naming["vocabulary_config_version"], cls.manifest_digest),
                )
                cls.batch_id = cur.fetchone()[0]

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

    def test_bulk_reserves_10000_trading_and_legal_names(self):
        with connect() as conn:
            with conn.cursor() as cur:
                for row in self.rows:
                    cur.execute(
                        """SELECT sw_names.reserve_business_name(
                             %s,'trading',%s,'SW-BUSINESS-REGISTRY-V1',
                             'ci-business-naming','bulk trading-name acceptance',0,%s)""",
                        (row["business_id"], row["trading_name"], self.batch_id),
                    )
                    self.assertIsNotNone(cur.fetchone()[0])
                    cur.execute(
                        """SELECT sw_names.reserve_business_name(
                             %s,'legal',%s,'SW-BUSINESS-REGISTRY-V1',
                             'ci-business-naming','bulk legal-name acceptance',0,%s)""",
                        (row["business_id"], row["registered_name"], self.batch_id),
                    )
                    self.assertIsNotNone(cur.fetchone()[0])
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
        self.reserve(self.rows[5]["business_id"], "Cobalt Harbour Logistics Review")
        with self.assertRaises(psycopg.Error):
            self.reserve(self.rows[6]["business_id"], "Cobalt Harbor Logistics Review")

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
