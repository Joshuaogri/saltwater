"""Materialise the BP03 9,000-resident dwelling allocation in a disposable SW-DB-001 world.

This fixture links existing canonical test people to active BP02 addresses. It does not
create households, infer demographics, or write to production.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import psycopg

from runtime.opening_resident_dwelling_allocation import (
    build_opening_resident_dwelling_allocation,
)

EXPECTED_RESIDENTS = 9000
ACTOR = "disposable-ci-generator"
REASON = (
    "BP03 disposable resident-to-dwelling allocation; no household composition "
    "or additional demographics inferred"
)


def materialise(database_url: str) -> dict:
    allocation = build_opening_resident_dwelling_allocation()
    records = allocation["records"]
    if allocation["dataset_id"] != "SW-OPENING-RESIDENT-DWELLING-ALLOCATION-V1":
        raise ValueError("unexpected BP03 dwelling allocation dataset")
    if allocation["candidate_count"] != EXPECTED_RESIDENTS or len(records) != EXPECTED_RESIDENTS:
        raise ValueError("BP03 resident allocation must contain exactly 9,000 candidates")
    if allocation["production_seed_authorized"] is not False:
        raise ValueError("disposable materializer refuses a production-authorized candidate package")
    if allocation["materialisation_status"] != (
        "CANDIDATE_DWELLING_MATCHES_ONLY_NO_CANONICAL_PERSON_RESIDENCE_OR_HOUSEHOLD_ROWS"
    ):
        raise ValueError("unexpected source allocation materialisation status")
    if len({r["unit_id"] for r in records}) != EXPECTED_RESIDENTS:
        raise ValueError("dwelling allocation reuses a unit")
    if len({r["candidate_ref"] for r in records}) != EXPECTED_RESIDENTS:
        raise ValueError("dwelling allocation reuses a civilian candidate")

    with psycopg.connect(database_url) as conn:
        with conn.transaction():
            dbname = conn.execute("SELECT current_database()").fetchone()[0]
            if dbname != "saltwater_test":
                raise RuntimeError(f"refusing non-disposable database {dbname!r}")

            conn.execute("""
                UPDATE sw_runtime.state
                SET state=1,player_present=false
                WHERE singleton=1 AND state=0 AND bootstrap_open=true AND world_tick=0
            """)
            conn.execute("""
                UPDATE sw_runtime.state
                SET state=2,player_present=true,bootstrap_open=false
                WHERE singleton=1 AND state=1 AND bootstrap_open=true
                  AND player_present=false AND world_tick=0
            """)
            runtime = conn.execute("""
                SELECT state,player_present,bootstrap_open,world_tick
                FROM sw_runtime.state WHERE singleton=1
            """).fetchone()
            if runtime != (2, True, False, 0):
                raise RuntimeError(f"runtime must be running at tick zero before residence materialisation: {runtime!r}")

            batch_id = conn.execute("""
                SELECT batch_id FROM sw_ops.world_provisioning_batch
                WHERE config_version='saltwater-opening-fixture-v2'
            """).fetchone()
            if not batch_id:
                raise RuntimeError("SW-DB-001 opening batch is missing")
            batch_id = batch_id[0]

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sw_test.opening_resident_dwelling_assignment (
                    allocation_ref text PRIMARY KEY,
                    batch_id bigint NOT NULL REFERENCES sw_ops.world_provisioning_batch(batch_id),
                    fixture_person_key text NOT NULL UNIQUE REFERENCES sw_test.person_cohort(fixture_person_key),
                    person_id integer NOT NULL UNIQUE REFERENCES sw_people.person(person_id),
                    candidate_ref text NOT NULL UNIQUE,
                    unit_id text NOT NULL UNIQUE,
                    bp04_address_id text NOT NULL,
                    bp02_address_source_id text NOT NULL REFERENCES sw_geo.bp02_address(source_id),
                    neighbourhood_id text NOT NULL,
                    residence_id bigint NOT NULL UNIQUE REFERENCES sw_people.person_residence(residence_id),
                    source_ref text NOT NULL UNIQUE,
                    fixture_only boolean NOT NULL DEFAULT true CHECK (fixture_only)
                )
            """)

            existing = conn.execute("""
                SELECT count(*) FROM sw_test.opening_resident_dwelling_assignment
                WHERE batch_id=%s
            """, (batch_id,)).fetchone()[0]
            if existing == EXPECTED_RESIDENTS:
                counts = conn.execute("""
                    SELECT count(*),count(DISTINCT person_id),count(DISTINCT unit_id),
                           count(DISTINCT bp02_address_source_id)
                    FROM sw_test.opening_resident_dwelling_assignment
                    WHERE batch_id=%s
                """, (batch_id,)).fetchone()
                if counts[:3] != (EXPECTED_RESIDENTS, EXPECTED_RESIDENTS, EXPECTED_RESIDENTS):
                    raise RuntimeError(f"existing residence allocation is inconsistent: {counts!r}")
                return {
                    "status": "already_materialised_idempotently",
                    "batch_id": batch_id,
                    "residents": counts[0],
                    "distinct_addresses": counts[3],
                }
            if existing != 0:
                raise RuntimeError(f"partial residence allocation exists ({existing} rows); refusing unsafe repair")

            residents = conn.execute("""
                SELECT count(*) FROM sw_test.person_cohort
                WHERE batch_id=%s AND cohort='RESIDENT'
            """, (batch_id,)).fetchone()[0]
            if residents != EXPECTED_RESIDENTS:
                raise RuntimeError(f"expected 9,000 resident fixture people, found {residents}")

            address_ids = [r["bp02_address_source_id"] for r in records]
            expected_addresses = len(set(address_ids))
            available = conn.execute("""
                SELECT count(DISTINCT source_id) FROM sw_geo.bp02_address
                WHERE source_id = ANY(%s) AND operational_status='ACTIVE_IN_GAME'
            """, (address_ids,)).fetchone()[0]
            if available != expected_addresses:
                raise RuntimeError(
                    f"only {available} of {expected_addresses} distinct allocation address references resolve to active BP02 addresses"
                )

            rows_json = json.dumps([
                {
                    "allocation_ref": r["allocation_ref"],
                    "candidate_ref": r["candidate_ref"],
                    "unit_id": r["unit_id"],
                    "bp04_address_id": r["bp04_address_id"],
                    "bp02_address_source_id": r["bp02_address_source_id"],
                    "neighbourhood_id": r["neighbourhood_id"],
                }
                for r in records
            ], separators=(",", ":"), sort_keys=True)

            inserted = conn.execute("""
                WITH allocation AS MATERIALIZED (
                    SELECT row_number() OVER (ORDER BY allocation_ref) AS seq,
                           a.*
                    FROM jsonb_to_recordset(%s::jsonb) AS a(
                        allocation_ref text,candidate_ref text,unit_id text,
                        bp04_address_id text,bp02_address_source_id text,
                        neighbourhood_id text
                    )
                ),
                residents AS MATERIALIZED (
                    SELECT row_number() OVER (ORDER BY fixture_person_key) AS seq,
                           fixture_person_key,person_id
                    FROM sw_test.person_cohort
                    WHERE batch_id=%s AND cohort='RESIDENT'
                ),
                joined AS MATERIALIZED (
                    SELECT a.*,r.fixture_person_key,r.person_id,
                           'SW-BP03:DISPOSABLE-RESIDENCE:'||a.allocation_ref AS source_ref
                    FROM allocation a JOIN residents r USING(seq)
                ),
                assigned AS MATERIALIZED (
                    SELECT j.*,
                           sw_people.set_person_residence(
                             j.person_id,j.bp02_address_source_id,'permanent',
                             j.source_ref,%s,%s
                           ) AS residence_id
                    FROM joined j
                )
                INSERT INTO sw_test.opening_resident_dwelling_assignment(
                    allocation_ref,batch_id,fixture_person_key,person_id,candidate_ref,
                    unit_id,bp04_address_id,bp02_address_source_id,neighbourhood_id,
                    residence_id,source_ref
                )
                SELECT allocation_ref,%s,fixture_person_key,person_id,candidate_ref,
                       unit_id,bp04_address_id,bp02_address_source_id,neighbourhood_id,
                       residence_id,source_ref
                FROM assigned
                RETURNING allocation_ref
            """, (rows_json, batch_id, ACTOR, REASON, batch_id)).fetchall()

            if len(inserted) != EXPECTED_RESIDENTS:
                raise RuntimeError(f"materialised {len(inserted)} residence links, expected 9,000")

            counts = conn.execute("""
                SELECT count(*),count(DISTINCT a.person_id),count(DISTINCT a.unit_id),
                       count(DISTINCT a.bp02_address_source_id),
                       count(*) FILTER (WHERE r.residence_status='current'),
                       count(*) FILTER (WHERE p.usual_resident)
                FROM sw_test.opening_resident_dwelling_assignment a
                JOIN sw_people.person_residence r USING(residence_id)
                JOIN sw_people.population_state p USING(person_id)
                WHERE a.batch_id=%s
            """, (batch_id,)).fetchone()
            if counts != (9000, 9000, 9000, expected_addresses, 9000, 9000):
                raise RuntimeError(f"residence materialisation failed reconciliation: {counts!r}")
            return {
                "status": "materialised",
                "batch_id": batch_id,
                "residents": counts[0],
                "distinct_people": counts[1],
                "distinct_dwelling_units": counts[2],
                "distinct_site_addresses": counts[3],
                "current_residences": counts[4],
                "usual_resident_flags": counts[5],
                "household_rows_created": 0,
                "production_database_written": False,
                "allocation_manifest_sha256": allocation["manifest_sha256"],
                "fixture_person_identity_matches_candidate_identity": False,
            }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    args = parser.parse_args()
    if not args.database_url:
        parser.error("DATABASE_URL or --database-url is required")
    print(json.dumps(materialise(args.database_url), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
