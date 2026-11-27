"""Materialise BP03's exact 9,000-person identity and dwelling allocation in disposable SW-DB-001.

Candidate identities are crosswalked by stable fixture keys, then linked to their
manifested BP02 addresses. No households or demographics are inferred; production is untouched.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from pathlib import Path

import psycopg

from runtime.opening_resident_dwelling_allocation import (
    build_opening_resident_dwelling_allocation,
)

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/people/saltwater-opening-civilian-resident-seed-v1.json.gz"
EXPECTED_RESIDENTS = 9000
ACTOR = "disposable-ci-generator"
REASON = (
    "BP03 disposable resident-to-dwelling allocation; no household composition "
    "or additional demographics inferred"
)



def _assert_exact_allocation_manifest(conn, batch_id: int) -> tuple[int, int]:
    """Require every persisted assignment and residence to match its source manifest."""
    total = conn.execute("""
        SELECT count(*) FROM sw_test.opening_resident_dwelling_assignment
        WHERE batch_id=%s
    """, (batch_id,)).fetchone()[0]
    exact = conn.execute("""
        SELECT count(*)
        FROM sw_test.opening_resident_dwelling_assignment a
        JOIN bp03_allocation_expected x
          ON x.allocation_ref=a.allocation_ref
         AND x.candidate_ref=a.candidate_ref
         AND x.unit_id=a.unit_id
         AND x.bp04_address_id=a.bp04_address_id
         AND x.bp02_address_source_id=a.bp02_address_source_id
         AND x.neighbourhood_id=a.neighbourhood_id
        JOIN bp03_candidate_stage s
          ON s.candidate_ref=a.candidate_ref
         AND s.source_ref=x.person_source_ref
         AND s.display_name=x.display_name
         AND s.fixture_person_key=a.fixture_person_key
        JOIN sw_people.person p
          ON p.person_id=a.person_id AND p.source_ref=x.person_source_ref
         AND concat_ws(' ',p.given_name,p.middle_name,p.family_name)=x.display_name
        JOIN sw_people.person_residence r
          ON r.residence_id=a.residence_id AND r.person_id=a.person_id
         AND r.address_source_id=x.bp02_address_source_id
         AND r.residence_kind='permanent' AND r.residence_status='current'
        WHERE a.batch_id=%s
          AND a.source_ref='SW-BP03:DISPOSABLE-RESIDENCE:'||a.allocation_ref
    """, (batch_id,)).fetchone()[0]
    if total != EXPECTED_RESIDENTS or exact != EXPECTED_RESIDENTS:
        raise RuntimeError(
            f"allocation manifest mismatch: assignment_rows={total}, "
            f"exact_manifest_identity_and_residence_matches={exact}, expected={EXPECTED_RESIDENTS}"
        )
    return total, exact


def _assert_negative_replay_rejected(conn, batch_id: int) -> None:
    """Prove a tampered dwelling reference fails reconciliation, then restore it."""
    conn.execute("SAVEPOINT bp03_negative_replay")
    try:
        changed = conn.execute("""
            UPDATE sw_test.opening_resident_dwelling_assignment
            SET unit_id=unit_id||':TAMPERED'
            WHERE batch_id=%s AND allocation_ref=(
                SELECT min(allocation_ref)
                FROM sw_test.opening_resident_dwelling_assignment WHERE batch_id=%s
            )
            RETURNING allocation_ref
        """, (batch_id, batch_id)).fetchone()
        if not changed:
            raise RuntimeError("negative replay test could not locate an assignment to tamper")
        try:
            _assert_exact_allocation_manifest(conn, batch_id)
        except RuntimeError as exc:
            if "allocation manifest mismatch" not in str(exc):
                raise
        else:
            raise RuntimeError("negative replay test failed: altered dwelling assignment was accepted")
    finally:
        conn.execute("ROLLBACK TO SAVEPOINT bp03_negative_replay")
        conn.execute("RELEASE SAVEPOINT bp03_negative_replay")


def materialise(database_url: str, negative_replay_test: bool = False) -> dict:
    started = time.perf_counter()

    def progress(label: str) -> None:
        print(f"BP03 materialiser: {label} (+{time.perf_counter() - started:.1f}s)", flush=True)

    progress("loading and validating candidate manifests")
    allocation = build_opening_resident_dwelling_allocation()
    with gzip.open(CANDIDATE_PATH, "rt", encoding="utf-8") as stream:
        candidate_payload = json.load(stream)
    candidates = candidate_payload["records"]
    if candidate_payload.get("dataset_id") != "SW-OPENING-CIVILIAN-RESIDENT-SEED-V1":
        raise ValueError("unexpected BP03 civilian identity candidate dataset")
    if len(candidates) != EXPECTED_RESIDENTS or candidate_payload.get("candidate_count") != EXPECTED_RESIDENTS:
        raise ValueError("BP03 civilian identity dataset must contain exactly 9,000 candidates")
    if len({row["candidate_ref"] for row in candidates}) != EXPECTED_RESIDENTS:
        raise ValueError("BP03 civilian identity dataset contains reused candidate references")
    if len({row["source_ref"] for row in candidates}) != EXPECTED_RESIDENTS:
        raise ValueError("BP03 civilian identity dataset contains reused source references")
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

            # Stable candidate_ref -> fixture key mapping; never use row-number pairing.
            staged = []
            for candidate in candidates:
                suffix = candidate["candidate_ref"].removeprefix("SWCIV-")
                if not suffix.isdigit():
                    raise ValueError(f"invalid civilian candidate reference: {candidate['candidate_ref']!r}")
                staged.append((
                    candidate["candidate_ref"], candidate["source_ref"], candidate["given_name"],
                    candidate.get("middle_name"), candidate["family_name"], candidate["display_name"],
                    "SWDB001-P-" + str(int(suffix)).zfill(5),
                ))
            conn.execute("""
                CREATE TEMP TABLE bp03_candidate_stage (
                    candidate_ref text PRIMARY KEY, source_ref text NOT NULL UNIQUE,
                    given_name text NOT NULL, middle_name text, family_name text NOT NULL,
                    display_name text NOT NULL, fixture_person_key text NOT NULL UNIQUE,
                    normalized_name text NOT NULL
                ) ON COMMIT DROP
            """)
            with conn.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO bp03_candidate_stage(
                        candidate_ref,source_ref,given_name,middle_name,family_name,
                        display_name,fixture_person_key,normalized_name
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,sw_names.normalize_name(%s))
                """, [(*row, row[5]) for row in staged])
            if conn.execute("SELECT count(*) FROM bp03_candidate_stage").fetchone()[0] != EXPECTED_RESIDENTS:
                raise RuntimeError("candidate identity staging did not reconcile to 9,000")
            if conn.execute("""
                SELECT count(*) FROM (
                    SELECT normalized_name FROM bp03_candidate_stage
                    GROUP BY normalized_name HAVING count(*)>1
                ) d
            """).fetchone()[0]:
                raise RuntimeError("civilian candidate cohort contains duplicate normalized names")
            conn.execute("""
                CREATE TEMP TABLE bp03_allocation_expected (
                    allocation_ref text PRIMARY KEY,
                    candidate_ref text NOT NULL UNIQUE,
                    person_source_ref text NOT NULL UNIQUE,
                    display_name text NOT NULL,
                    unit_id text NOT NULL UNIQUE,
                    bp04_address_id text NOT NULL,
                    bp02_address_source_id text NOT NULL,
                    neighbourhood_id text NOT NULL
                ) ON COMMIT DROP
            """)
            with conn.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO bp03_allocation_expected(
                        allocation_ref,candidate_ref,person_source_ref,display_name,
                        unit_id,bp04_address_id,bp02_address_source_id,neighbourhood_id
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, [
                    (
                        row["allocation_ref"], row["candidate_ref"], row["person_source_ref"],
                        row["display_name"], row["unit_id"], row["bp04_address_id"],
                        row["bp02_address_source_id"], row["neighbourhood_id"],
                    )
                    for row in records
                ])

            existing = conn.execute("""
                SELECT count(*) FROM sw_test.opening_resident_dwelling_assignment
                WHERE batch_id=%s
            """, (batch_id,)).fetchone()[0]
            if existing == EXPECTED_RESIDENTS:
                counts = conn.execute("""
                    SELECT count(*),
                           count(DISTINCT a.person_id),
                           count(DISTINCT a.unit_id),
                           count(DISTINCT a.bp02_address_source_id),
                           count(DISTINCT a.candidate_ref),
                           count(*) FILTER (WHERE r.residence_status='current'),
                           count(*) FILTER (WHERE ps.usual_resident),
                           count(*) FILTER (WHERE p.source_ref=s.source_ref
                             AND p.given_name=s.given_name
                             AND p.middle_name IS NOT DISTINCT FROM s.middle_name
                             AND p.family_name=s.family_name
                             AND concat_ws(' ',p.given_name,p.middle_name,p.family_name)=s.display_name),
                           count(*) FILTER (WHERE pc.cohort='RESIDENT'
                             AND pc.fixture_person_key=s.fixture_person_key),
                           count(*) FILTER (WHERE nr.reservation_id IS NOT NULL)
                    FROM sw_test.opening_resident_dwelling_assignment a
                    JOIN bp03_allocation_expected x
                      ON x.allocation_ref=a.allocation_ref
                     AND x.candidate_ref=a.candidate_ref
                     AND x.unit_id=a.unit_id
                     AND x.bp04_address_id=a.bp04_address_id
                     AND x.bp02_address_source_id=a.bp02_address_source_id
                     AND x.neighbourhood_id=a.neighbourhood_id
                    JOIN bp03_candidate_stage s
                      ON s.candidate_ref=a.candidate_ref
                     AND s.source_ref=x.person_source_ref
                     AND s.display_name=x.display_name
                     AND s.fixture_person_key=a.fixture_person_key
                    JOIN sw_people.person p ON p.person_id=a.person_id
                    JOIN sw_people.person_residence r
                      ON r.residence_id=a.residence_id AND r.person_id=a.person_id
                     AND r.address_source_id=a.bp02_address_source_id
                     AND r.residence_kind='permanent'
                    JOIN sw_geo.bp02_address ad
                      ON ad.source_id=a.bp02_address_source_id
                     AND ad.operational_status='ACTIVE_IN_GAME'
                    JOIN sw_people.population_state ps ON ps.person_id=a.person_id
                    JOIN sw_test.person_cohort pc
                      ON pc.person_id=a.person_id AND pc.batch_id=a.batch_id
                    LEFT JOIN sw_names.name_reservation nr
                      ON nr.entity_type='PERSON' AND nr.entity_id=p.person_id
                     AND nr.name_form='canonical'
                     AND nr.normalized_key=s.normalized_name
                     AND sw_names.latest_status(nr.reservation_id)='active'
                    WHERE a.batch_id=%s
                """, (batch_id,)).fetchone()
                police_count = conn.execute("""
                    SELECT count(*)
                    FROM sw_test.person_cohort pc
                    JOIN sw_people.person p ON p.person_id=pc.person_id
                    WHERE pc.batch_id=%s AND pc.cohort='POLICE_SUBSET'
                      AND p.source_ref LIKE 'SW-DB-001:person:%%'
                """, (batch_id,)).fetchone()[0]
                expected = (
                    EXPECTED_RESIDENTS, EXPECTED_RESIDENTS, EXPECTED_RESIDENTS,
                    len({row['bp02_address_source_id'] for row in records}),
                    EXPECTED_RESIDENTS, EXPECTED_RESIDENTS, EXPECTED_RESIDENTS,
                    EXPECTED_RESIDENTS, EXPECTED_RESIDENTS, EXPECTED_RESIDENTS,
                )
                if counts != expected or police_count != 500:
                    raise RuntimeError(
                        'existing residence allocation failed full BP03 idempotency '
                        f'reconciliation: counts={counts!r}, expected={expected!r}, '
                        f'police_subset={police_count}'
                    )
                _assert_exact_allocation_manifest(conn, batch_id)
                if negative_replay_test:
                    _assert_negative_replay_rejected(conn, batch_id)
                return {
                    'status': 'already_materialised_idempotently',
                    'batch_id': batch_id,
                    'residents': counts[0],
                    'distinct_people': counts[1],
                    'distinct_dwelling_units': counts[2],
                    'distinct_addresses': counts[3],
                    'current_residences': counts[5],
                    'candidate_person_identity_matches': counts[7],
                    'canonical_name_reservations_active': counts[9],
                    'police_subset_preserved': police_count,
                    'identity_crosswalk_verified': True,
                }
            if existing != 0:
                raise RuntimeError(f"partial residence allocation exists ({existing} rows); refusing unsafe repair")

            residents = conn.execute("""
                SELECT count(*) FROM sw_test.person_cohort
                WHERE batch_id=%s AND cohort='RESIDENT'
            """, (batch_id,)).fetchone()[0]
            if residents != EXPECTED_RESIDENTS:
                raise RuntimeError(f"expected 9,000 resident fixture people, found {residents}")

            mapped = conn.execute("""
                SELECT count(*),count(DISTINCT p.person_id),
                       count(*) FILTER (WHERE pc.cohort='RESIDENT'),
                       count(*) FILTER (WHERE p.source_ref='SW-DB-001:person:'||split_part(s.fixture_person_key,'-',3)::integer)
                FROM bp03_candidate_stage s
                JOIN sw_test.person_cohort pc ON pc.fixture_person_key=s.fixture_person_key AND pc.batch_id=%s
                JOIN sw_people.person p ON p.person_id=pc.person_id
            """, (batch_id,)).fetchone()
            if mapped != (9000,9000,9000,9000):
                raise RuntimeError(f"explicit candidate-to-fixture identity crosswalk failed: {mapped!r}")
            police_count = conn.execute("""
                SELECT count(*) FROM sw_test.person_cohort pc
                JOIN sw_people.person p USING(person_id)
                WHERE pc.batch_id=%s AND pc.cohort='POLICE_SUBSET'
                  AND p.source_ref LIKE 'SW-DB-001:person:%%'
            """, (batch_id,)).fetchone()[0]
            if police_count != 500:
                raise RuntimeError(f"separate 500-person police cohort changed: {police_count}")

            # The authoritative SW-UNS function performs one locked, set-based
            # exact/near-duplicate preflight and records the approved batch keys.
            conn.execute("SET LOCAL search_path = pg_catalog, sw_names, public")

            progress("starting SW-UNS manifest registration and duplicate preflight")
            name_batch_id = conn.execute("""
                SELECT sw_names.record_generation_batch(
                    'PERSON'::text,1::smallint,1::smallint,
                    'saltwater-opening-civilian-resident-seed-v1'::text,
                    %s::bigint,%s::bytea,9000::integer,
                    'SW-OPENING-CIVILIAN-RESIDENT-SEED-V1'::text,%s::text,
                    'BP03 disposable identity materialisation; exact 9,000-person civilian cohort'::text
                )
            """, (candidate_payload["seed"], bytes.fromhex(candidate_payload["manifest_sha256"]), ACTOR)).fetchone()[0]
            preflighted = conn.execute("""
                SELECT sw_names.preflight_generation_batch(%s,array_agg(display_name))
                FROM bp03_candidate_stage
            """, (name_batch_id,)).fetchone()[0]
            if preflighted != EXPECTED_RESIDENTS:
                raise RuntimeError(f"SW-UNS preflighted {preflighted} names, expected 9,000")
            progress("SW-UNS duplicate preflight complete: 9,000 names")
            # The canonical person-name trigger reads this transaction-local
            # manifest ID so its reservation is linked to the approved batch.
            conn.execute(
                "SELECT set_config('sw_names.generation_batch_id', %s, true)",
                (str(name_batch_id),),
            )
            conn.execute("""
                INSERT INTO sw_core.simulation_event(
                    event_type_id,occurred_at,world_tick,subject_kind,subject_id,
                    source_ref,attributes,idempotency_key
                )
                SELECT et.event_type_id,clock_timestamp(),0,'person',p.person_id,
                       s.source_ref||':profile-materialised',
                       jsonb_build_object('operation','opening_civilian_identity_materialised',
                         'candidate_ref',s.candidate_ref,'actor_ref',%s::text),
                       'SW-BP03:PERSON_PROFILE:'||p.person_id||':'||s.source_ref
                FROM bp03_candidate_stage s
                JOIN sw_test.person_cohort pc ON pc.fixture_person_key=s.fixture_person_key
                  AND pc.batch_id=%s AND pc.cohort='RESIDENT'
                JOIN sw_people.person p ON p.person_id=pc.person_id
                CROSS JOIN sw_core.event_type et
                WHERE et.event_code='PERSON_PROFILE_CHANGED'
            """, (ACTOR,batch_id))
            progress("updating canonical person profiles; SW-UNS trigger creates canonical reservations")
            updated = conn.execute("""
                UPDATE sw_people.person p
                SET given_name=s.given_name,middle_name=s.middle_name,
                    family_name=s.family_name,source_ref=s.source_ref,last_event_id=e.event_id
                FROM bp03_candidate_stage s
                JOIN sw_test.person_cohort pc ON pc.fixture_person_key=s.fixture_person_key
                  AND pc.batch_id=%s AND pc.cohort='RESIDENT'
                JOIN sw_core.simulation_event e ON e.source_ref=s.source_ref||':profile-materialised'
                WHERE p.person_id=pc.person_id
                RETURNING p.person_id
            """, (batch_id,)).fetchall()
            if len(updated) != EXPECTED_RESIDENTS:
                raise RuntimeError(f"materialised {len(updated)} canonical civilian profiles, expected 9,000")
            progress("person profiles updated; verifying trigger-created canonical reservations")
            reserved = conn.execute("""
                SELECT count(*)
                FROM bp03_candidate_stage s
                JOIN sw_people.person p ON p.source_ref=s.source_ref
                JOIN sw_names.name_reservation nr
                  ON nr.entity_type='PERSON' AND nr.entity_id=p.person_id
                 AND nr.name_form='canonical'
                 AND nr.normalized_key=s.normalized_name
                 AND nr.generation_batch_id=%s
                 AND nr.source_ref=s.source_ref
                WHERE sw_names.latest_status(nr.reservation_id)='active'
            """, (name_batch_id,)).fetchone()[0]
            if reserved != EXPECTED_RESIDENTS:
                raise RuntimeError(f"found {reserved} active trigger-created canonical civilian names, expected 9,000")
            progress("canonical name reservations verified: 9,000")

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
                    "person_source_ref": r["person_source_ref"],
                    "display_name": r["display_name"],
                    "unit_id": r["unit_id"],
                    "bp04_address_id": r["bp04_address_id"],
                    "bp02_address_source_id": r["bp02_address_source_id"],
                    "neighbourhood_id": r["neighbourhood_id"],
                }
                for r in records
            ], separators=(",", ":"), sort_keys=True)

            progress("starting 9,000 residence assignments; each uses the authoritative residence lifecycle function")
            inserted = conn.execute("""
                WITH allocation AS MATERIALIZED (
                    SELECT a.*
                    FROM jsonb_to_recordset(%s::jsonb) AS a(
                        allocation_ref text,candidate_ref text,person_source_ref text,
                        display_name text,unit_id text,bp04_address_id text,
                        bp02_address_source_id text,neighbourhood_id text
                    )
                ),
                joined AS MATERIALIZED (
                    SELECT a.*,pc.fixture_person_key,p.person_id,
                           'SW-BP03:DISPOSABLE-RESIDENCE:'||a.allocation_ref AS source_ref
                    FROM allocation a
                    JOIN bp03_candidate_stage s ON s.candidate_ref=a.candidate_ref
                      AND s.source_ref=a.person_source_ref AND s.display_name=a.display_name
                    JOIN sw_people.person p ON p.source_ref=s.source_ref
                    JOIN sw_test.person_cohort pc ON pc.person_id=p.person_id
                      AND pc.fixture_person_key=s.fixture_person_key
                      AND pc.cohort='RESIDENT' AND pc.batch_id=%s
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
            progress("residence lifecycle function completed: 9,000 links")

            progress("running full identity, dwelling and population reconciliation")
            counts = conn.execute("""
                SELECT count(*) AS assignment_rows,
                       count(DISTINCT a.person_id),
                       count(DISTINCT a.unit_id),
                       count(DISTINCT a.bp02_address_source_id),
                       count(DISTINCT a.candidate_ref),
                       count(*) FILTER (WHERE r.residence_status='current'
                         AND r.person_id=a.person_id
                         AND r.address_source_id=a.bp02_address_source_id
                         AND r.residence_kind='permanent'),
                       count(*) FILTER (WHERE ps.usual_resident),
                       count(*) FILTER (WHERE p.source_ref=s.source_ref
                         AND concat_ws(' ',p.given_name,p.middle_name,p.family_name)=s.display_name),
                       count(*) FILTER (WHERE a.source_ref=
                         'SW-BP03:DISPOSABLE-RESIDENCE:'||a.allocation_ref)
                FROM sw_test.opening_resident_dwelling_assignment a
                LEFT JOIN sw_people.person_residence r ON r.residence_id=a.residence_id
                LEFT JOIN sw_people.population_state ps ON ps.person_id=a.person_id
                LEFT JOIN sw_people.person p ON p.person_id=a.person_id
                LEFT JOIN bp03_candidate_stage s
                  ON s.candidate_ref=a.candidate_ref AND s.source_ref=p.source_ref
                WHERE a.batch_id=%s
            """, (batch_id,)).fetchone()
            total, exact = _assert_exact_allocation_manifest(conn, batch_id)
            progress("exact manifest reconciliation passed")
            if negative_replay_test:
                progress("running tampered dwelling replay rejection")
                _assert_negative_replay_rejected(conn, batch_id)
                progress("tampered dwelling replay correctly rejected and rolled back")

            if counts[1:] != (
                EXPECTED_RESIDENTS, EXPECTED_RESIDENTS, expected_addresses,
                EXPECTED_RESIDENTS, EXPECTED_RESIDENTS, EXPECTED_RESIDENTS,
                EXPECTED_RESIDENTS, EXPECTED_RESIDENTS
            ):
                raise RuntimeError(f"residence materialisation failed reconciliation: {counts!r}")
            return {
                "status": "materialised",
                "batch_id": batch_id,
                "residents": counts[0],
                "distinct_people": counts[1],
                "distinct_dwelling_units": counts[2],
                "distinct_site_addresses": counts[3],
                "current_residences": counts[5],
                "usual_resident_flags": counts[6],
                "household_rows_created": 0,
                "production_database_written": False,
                "allocation_manifest_sha256": allocation["manifest_sha256"],
                "fixture_person_identity_matches_candidate_identity": True,
                "canonical_person_names_reserved": reserved,
                "candidate_person_identity_matches": counts[7],
                "police_subset_preserved": police_count,
            }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--negative-replay-test", action="store_true")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("DATABASE_URL or --database-url is required")
    print(json.dumps(materialise(args.database_url, negative_replay_test=args.negative_replay_test), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
