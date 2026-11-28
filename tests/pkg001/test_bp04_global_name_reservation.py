"""Disposable PostgreSQL acceptance for persistent BP04 text-ID name reservations."""
import gzip
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


def read_archive(relative_path):
    with gzip.open(ROOT / relative_path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def rows(document, collection):
    table = document.get("tables", {}).get(collection)
    if table is None:
        return []
    columns = table["columns"]
    return [dict(zip(columns, values)) for values in table["rows"]]


def first_value(row, fields):
    return next((row.get(field) for field in fields if row.get(field)), None)


class BP04GlobalNameReservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = read_archive("data/property/saltwater-property-world-v1.json.gz")
        cls.tenure = read_archive("data/property/saltwater-property-tenure-v1.json.gz")
        cls.services = read_archive("data/property/saltwater-building-services-v1.json.gz")

        cls.property_rows = rows(cls.world, "properties")
        cls.building_rows = rows(cls.world, "buildings")
        cls.premises_rows = rows(cls.world, "premises")

        cls.named = {
            "PROPERTY": [
                (str(row["property_id"]), str(name))
                for row in cls.property_rows
                if (name := first_value(row, ("display_name", "property_name", "name")))
            ],
            "BUILDING": [
                (str(row["building_id"]), str(name))
                for row in cls.building_rows
                if (name := first_value(row, ("display_name", "building_name", "name")))
            ],
            "PREMISES": [
                (str(row["premises_id"]), str(name))
                for row in cls.premises_rows
                if (name := first_value(row, ("display_name", "premises_name", "name")))
            ],
        }

        organisations = {}
        for source, collection in (
            (cls.tenure, "organisations"),
            (cls.services, "utility_providers"),
        ):
            for row in rows(source, collection):
                entity_id = str(row["organisation_id"])
                display_name = str(row["display_name"]).strip()
                if not display_name:
                    raise AssertionError(f"{entity_id} has an empty canonical organisation name")
                prior = organisations.get(entity_id)
                if prior and prior["display_name"] != display_name:
                    raise AssertionError(f"conflicting source names for organisation {entity_id}")
                organisations[entity_id] = {
                    "organisation_id": entity_id,
                    "display_name": display_name,
                    "organisation_type": row.get("organisation_type") or "UTILITY_OR_PROPERTY",
                    "source_dataset": (
                        "SW-PROPERTY-TENURE-V1"
                        if collection == "organisations"
                        else "SW-BUILDING-SERVICES-V1"
                    ),
                    "source_record": row,
                }
        cls.organisations = list(organisations.values())
        cls.named["ORGANISATION"] = [
            (row["organisation_id"], row["display_name"]) for row in cls.organisations
        ]

        with connect() as conn:
            with conn.cursor() as cur:
                for row in cls.property_rows:
                    entity_id = str(row["property_id"])
                    display_name = first_value(row, ("display_name", "property_name", "name")) or entity_id
                    cur.execute(
                        """INSERT INTO sw_property.property_site
                           (property_id,display_name,source_dataset,source_record)
                           VALUES (%s,%s,'SW-PROPERTY-WORLD-V1',%s::jsonb)
                           ON CONFLICT (property_id) DO NOTHING""",
                        (entity_id, display_name, json.dumps(row, ensure_ascii=False)),
                    )
                for row in cls.building_rows:
                    entity_id = str(row["building_id"])
                    property_id = str(row["property_id"])
                    display_name = first_value(row, ("display_name", "building_name", "name")) or entity_id
                    cur.execute(
                        """INSERT INTO sw_property.building
                           (building_id,property_id,display_name,source_dataset,source_record)
                           VALUES (%s,%s,%s,'SW-PROPERTY-WORLD-V1',%s::jsonb)
                           ON CONFLICT (building_id) DO NOTHING""",
                        (entity_id, property_id, display_name, json.dumps(row, ensure_ascii=False)),
                    )
                for row in cls.premises_rows:
                    entity_id = str(row["premises_id"])
                    property_id = str(row["property_id"])
                    building_id = row.get("building_id")
                    display_name = first_value(row, ("display_name", "premises_name", "name")) or entity_id
                    cur.execute(
                        """INSERT INTO sw_property.premises
                           (premises_id,property_id,building_id,display_name,source_dataset,source_record)
                           VALUES (%s,%s,%s,%s,'SW-PROPERTY-WORLD-V1',%s::jsonb)
                           ON CONFLICT (premises_id) DO NOTHING""",
                        (entity_id, property_id, building_id, display_name, json.dumps(row, ensure_ascii=False)),
                    )
                for row in cls.organisations:
                    cur.execute(
                        """INSERT INTO sw_property.organisation
                           (organisation_id,display_name,organisation_type,source_dataset,source_record)
                           VALUES (%s,%s,%s,%s,%s::jsonb)
                           ON CONFLICT (organisation_id) DO NOTHING""",
                        (
                            row["organisation_id"], row["display_name"],
                            row["organisation_type"], row["source_dataset"],
                            json.dumps(row["source_record"], ensure_ascii=False),
                        ),
                    )

    def _reserve_domain(self, entity_type):
        records = sorted(self.named[entity_type])
        names = [name for _, name in records]
        manifest = {
            "domain": entity_type,
            "normalizer_version": 1,
            "records": records,
        }
        digest = hashlib.sha256(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).digest()
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT sw_names.record_generation_batch(
                         %s::text,1::smallint,1::smallint,'SW-UNS-001-v1'::text,
                         20261128::bigint,%s::bytea,%s::integer,
                         'BP04-global-canon-name-inventory'::text,'ci-bp04-global-name'::text,
                         'BP04 global persistent canonical-name reservation'::text)""",
                    (entity_type, digest, len(records)),
                )
                batch_id = cur.fetchone()[0]
                cur.execute(
                    "SELECT sw_names.preflight_generation_batch(%s,%s::text[])",
                    (batch_id, names),
                )
                self.assertEqual(cur.fetchone()[0], len(records))
                for entity_id, display_name in records:
                    cur.execute(
                        """SELECT sw_names.reserve_text_entity_name(
                             %s,%s,'canonical',%s,
                             'BP04-global-canon-name-inventory','ci-bp04-global-name',
                             'BP04 global persistent canonical-name reservation',0,%s)""",
                        (entity_type, entity_id, display_name, batch_id),
                    )
                cur.execute(
                    """SELECT count(*) FROM sw_names.name_reservation
                       WHERE entity_type=%s AND generation_batch_id=%s""",
                    (entity_type, batch_id),
                )
                self.assertEqual(cur.fetchone()[0], len(records))
        return batch_id

    def test_property_building_premises_and_organisation_names_are_persistently_reserved(self):
        expected = {}
        for entity_type in ("PROPERTY", "BUILDING", "PREMISES", "ORGANISATION"):
            expected[entity_type] = len(self.named[entity_type])
            self.assertGreater(expected[entity_type], 0, entity_type)
            self._reserve_domain(entity_type)

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT entity_type,count(*)
                       FROM sw_names.name_reservation
                       WHERE entity_type IN ('PROPERTY','BUILDING','PREMISES','ORGANISATION')
                       GROUP BY entity_type ORDER BY entity_type"""
                )
                actual = dict(cur.fetchall())
        self.assertEqual(actual, expected)

    def test_text_entity_reservation_is_idempotent_and_searchable(self):
        entity_id, display_name = self.named["ORGANISATION"][0]
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT reservation_id FROM sw_names.name_reservation
                       WHERE entity_type='ORGANISATION' AND entity_ref=%s
                         AND name_form='canonical'""",
                    (entity_id,),
                )
                existing = cur.fetchone()
        if existing is None:
            self._reserve_domain("ORGANISATION")
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT reservation_id FROM sw_names.name_reservation
                           WHERE entity_type='ORGANISATION' AND entity_ref=%s
                             AND name_form='canonical'""",
                        (entity_id,),
                    )
                    existing = cur.fetchone()
        self.assertIsNotNone(existing)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT sw_names.reserve_text_entity_name(
                         'ORGANISATION',%s,'canonical',%s,
                         'BP04-global-canon-name-inventory','ci-bp04-global-name',
                         'idempotent retry',0)""",
                    (entity_id, display_name),
                )
                self.assertEqual(cur.fetchone()[0], existing[0])
                cur.execute(
                    "SELECT entity_ref,display_name,status FROM sw_names.search_text_entity_name('ORGANISATION',%s)",
                    (display_name,),
                )
                self.assertEqual(cur.fetchone(), (entity_id, display_name, "active"))

    def test_shared_namespace_rejects_exact_and_near_duplicates_across_business_and_organisation(self):
        business_id = "SWBIZ-AC-A04-CROSSDOMAIN-001"
        organisation_id = "SWORG-AC-A04-CROSSDOMAIN-001"
        exact_name = "Qzvra Xylophonic Test Domain"
        near_name = "Qzvra Xylophonic Test Domains"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO sw_property.business
                       (business_id,display_name,sector,primary_activity,status,source_dataset,source_record)
                       VALUES (%s,%s,'Professional Services','Synthetic test','active','SW-AC-A04-TEST','{}'::jsonb)""",
                    (business_id, exact_name),
                )
                cur.execute(
                    """INSERT INTO sw_property.organisation
                       (organisation_id,display_name,organisation_type,source_dataset,source_record)
                       VALUES (%s,%s,'TEST','SW-AC-A04-TEST','{}'::jsonb)""",
                    (organisation_id, exact_name),
                )
                cur.execute(
                    """SELECT sw_names.reserve_business_name(
                         %s,'trading',%s,'SW-AC-A04-TEST','ci-bp04-global-name',
                         'shared namespace exact-conflict fixture',0)""",
                    (business_id, exact_name),
                )
        with self.assertRaises(psycopg.Error):
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT sw_names.reserve_text_entity_name(
                             'ORGANISATION',%s,'canonical',%s,
                             'SW-AC-A04-TEST','ci-bp04-global-name',
                             'exact cross-domain conflict must be rejected',0)""",
                        (organisation_id, exact_name),
                    )

        near_business_id = "SWBIZ-AC-A04-CROSSDOMAIN-002"
        near_organisation_id = "SWORG-AC-A04-CROSSDOMAIN-002"
        near_business_name = "Mellifluous Quartz Holdings"
        near_name = "Mellifluous Quartz Holdinngs"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO sw_property.business
                       (business_id,display_name,sector,primary_activity,status,source_dataset,source_record)
                       VALUES (%s,%s,'Professional Services',
                               'Synthetic test','active','SW-AC-A04-TEST','{}'::jsonb)""",
                    (near_business_id, near_business_name),
                )
                cur.execute(
                    """INSERT INTO sw_property.organisation
                       (organisation_id,display_name,organisation_type,source_dataset,source_record)
                       VALUES (%s,%s,'TEST','SW-AC-A04-TEST','{}'::jsonb)""",
                    (near_organisation_id, near_name),
                )
                cur.execute(
                    """SELECT sw_names.similarity(
                         sw_names.normalize_name(%s),sw_names.normalize_name(%s))""",
                    (near_business_name, near_name),
                )
                self.assertGreaterEqual(cur.fetchone()[0], 0.90)
                cur.execute(
                    """SELECT sw_names.reserve_business_name(
                         %s,'trading',%s,
                         'SW-AC-A04-TEST','ci-bp04-global-name',
                         'shared namespace near-conflict fixture',0)""",
                    (near_business_id, near_business_name),
                )
        with self.assertRaises(psycopg.Error):
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT sw_names.reserve_text_entity_name(
                             'ORGANISATION',%s,'canonical',%s,
                             'SW-AC-A04-TEST','ci-bp04-global-name',
                             'near-duplicate cross-domain conflict must be rejected',0)""",
                        (near_organisation_id, near_name),
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
