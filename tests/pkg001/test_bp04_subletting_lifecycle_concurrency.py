"""Two-session BP04 tests for subletting start/end interleavings."""

from __future__ import annotations

import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import psycopg

from tests.pkg001.test_bp04_concurrent_handover import _seed_fixture, _call_subletting


def _prepare_subtenant(dsn, token, prop, unit, business, establishment, agreement):
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sw_property.occupancy_agreement SET agreement_type='sublease' WHERE agreement_id=%s",
                (agreement,),
            )
            cur.execute(
                """
                INSERT INTO sw_property.occupancy(
                  occupancy_id,property_id,premises_id,unit_id,occupant_business_id,
                  establishment_id,agreement_id,occupant_type,occupancy_status,
                  effective_from_year,effective_to_year,source_dataset
                )
                SELECT %s,%s,premises_id,unit_id,%s,%s,%s,'business_subtenant',
                       'occupied',2027,NULL,'bp04_subletting_lifecycle_concurrency'
                FROM sw_property.occupancy_agreement WHERE agreement_id=%s
                """,
                (f"SWLIFE-OCC-{token}", prop, business, establishment, agreement, agreement),
            )
            cur.execute(
                """
                INSERT INTO sw_property.contractual_rights_index(
                  property_right_id,property_id,premises_id,unit_id,right_type,
                  holder_business_id,source_agreement_id,commencement_year,right_status,
                  permitted_use,source_of_truth,new_legal_instrument_created,source_dataset,
                  consent_requirement
                )
                SELECT %s,%s,premises_id,%s,'subletting',tenant_business_id,%s,2027,
                       'current','commercial','bp04_subletting_lifecycle_concurrency',
                       false,'bp04_subletting_lifecycle_concurrency','not_required'
                FROM sw_property.occupancy_agreement WHERE agreement_id=%s
                """,
                (f"SWLIFE-RIGHT-{token}", prop, unit, agreement, agreement),
            )


def _call_end(dsn, app_name, barrier, args):
    try:
        with psycopg.connect(dsn, application_name=app_name, options="-c statement_timeout=60000") as conn:
            with conn.cursor() as cur:
                barrier.wait(timeout=15)
                cur.execute(
                    "SELECT * FROM sw_property.end_subletting_relationship(%s,%s,%s,%s,%s,%s)",
                    args,
                )
                return ("ok", cur.fetchone(), None)
    except Exception as exc:
        return ("error", None, str(exc))


def _race_unit_lock(dsn, unit, left, right, left_name, right_name):
    blocker = psycopg.connect(dsn, application_name="bp04-sublet-lifecycle-blocker",
                              options="-c statement_timeout=60000")
    try:
        with blocker.cursor() as cur:
            cur.execute("SELECT unit_id FROM sw_property.unit_space WHERE unit_id=%s FOR UPDATE", (unit,))
            assert cur.fetchone() is not None
        barrier = Barrier(3)
        with ThreadPoolExecutor(max_workers=2) as pool:
            f1 = pool.submit(left, dsn, left_name, barrier)
            f2 = pool.submit(right, dsn, right_name, barrier)
            barrier.wait(timeout=15)
            deadline = time.monotonic() + 10
            waiting = 0
            while time.monotonic() < deadline:
                with blocker.cursor() as cur:
                    cur.execute(
                        """SELECT application_name,wait_event_type,pg_blocking_pids(pid)
                           FROM pg_stat_activity WHERE application_name IN (%s,%s)""",
                        (left_name, right_name),
                    )
                    states = cur.fetchall()
                waiting = sum(1 for row in states if row[1] == "Lock" and row[2])
                if waiting == 2:
                    break
                time.sleep(0.05)
            if waiting != 2:
                raise AssertionError(f"both start/end writers must queue on the same unit lock: {states!r}")
            blocker.commit()
            return f1.result(timeout=30), f2.result(timeout=30)
    finally:
        if not blocker.closed:
            blocker.rollback()
            blocker.close()


def test_exact_start_replay_interleaved_with_end_is_serialized():
    dsn = os.environ["DATABASE_URL"]
    token = uuid.uuid4().hex[:12]
    prop, unit, businesses, agreements, superior_occ = _seed_fixture(dsn, token)
    _prepare_subtenant(dsn, token, prop, unit, businesses[1], f"SWCONC-EST-{token}-2", agreements[1])
    right = f"SWLIFE-RIGHT-{token}"
    relationship = f"SWLIFE-REL-{token}"
    start_key = f"sublet:lifecycle:start:{token}"
    start_args = (relationship, agreements[0], agreements[1], superior_occ,
                  f"SWLIFE-OCC-{token}", right, 10, 10, "npc:granting-tenant",
                  "generated:subletting", start_key)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sw_property.record_subletting_relationship(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", start_args)
            assert cur.fetchone()[1] == "active"
    end_args = (relationship, 20, 20, "npc:granting-tenant", "generated:subletting-end",
                f"sublet:lifecycle:end:{token}")
    replay = lambda dsn, name, barrier: _call_subletting(dsn, name, barrier, start_args)
    end = lambda dsn, name, barrier: _call_end(dsn, name, barrier, end_args)
    a, b = _race_unit_lock(dsn, unit, replay, end,
                           "bp04-lifecycle-start-replay", "bp04-lifecycle-end")
    assert a[0] == "ok" and b[0] == "ok", (a, b)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT relationship_status,effective_to_tick FROM sw_property.occupancy_relationship WHERE relationship_id=%s", (relationship,))
            assert cur.fetchone() == ("ended", 20)
            cur.execute("SELECT count(*) FROM sw_property.occupancy_agreement_event WHERE agreement_id=%s AND idempotency_key IN (%s,%s)", (agreements[0], start_key, end_args[5]))
            assert cur.fetchone()[0] == 2
            cur.execute("SELECT effective_to_year FROM sw_property.occupancy WHERE occupancy_id=%s", (f"SWLIFE-OCC-{token}",))
            assert cur.fetchone()[0] is None, "legal subletting end must not silently end physical occupancy"


def test_new_subletting_start_interleaved_with_prior_relationship_end():
    dsn = os.environ["DATABASE_URL"]
    token = uuid.uuid4().hex[:12]
    prop, unit, businesses, agreements, superior_occ = _seed_fixture(dsn, token)
    _prepare_subtenant(dsn, token+"A", prop, unit, businesses[1], f"SWCONC-EST-{token}-2", agreements[1])
    _prepare_subtenant(dsn, token+"B", prop, unit, businesses[2], f"SWCONC-EST-{token}-3", agreements[2])
    first_right, second_right = f"SWLIFE-RIGHT-{token}A", f"SWLIFE-RIGHT-{token}B"
    first_rel, second_rel = f"SWLIFE-REL-{token}A", f"SWLIFE-REL-{token}B"
    first_start = (first_rel, agreements[0], agreements[1], superior_occ,
                   f"SWLIFE-OCC-{token}A", first_right, 10, 10, "npc:tenant",
                   "generated:first-sublet", f"sublet:first:{token}")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sw_property.record_subletting_relationship(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", first_start)
            assert cur.fetchone()[1] == "active"
    second_start = (second_rel, agreements[0], agreements[2], superior_occ,
                    f"SWLIFE-OCC-{token}B", second_right, 21, 21, "npc:tenant",
                    "generated:second-sublet", f"sublet:second:{token}")
    end_args = (first_rel, 20, 20, "npc:tenant", "generated:first-end", f"sublet:end-first:{token}")
    start = lambda dsn, name, barrier: _call_subletting(dsn, name, barrier, second_start)
    end = lambda dsn, name, barrier: _call_end(dsn, name, barrier, end_args)
    a, b = _race_unit_lock(dsn, unit, start, end,
                           "bp04-lifecycle-second-start", "bp04-lifecycle-first-end")
    assert a[0] == "ok" and b[0] == "ok", (a, b)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT relationship_id,relationship_status FROM sw_property.occupancy_relationship WHERE relationship_id IN (%s,%s) ORDER BY relationship_id", (first_rel, second_rel))
            assert cur.fetchall() == [(first_rel, "ended"), (second_rel, "active")]
            cur.execute("SELECT count(*) FROM sw_property.occupancy_agreement_event WHERE agreement_id=%s AND idempotency_key IN (%s,%s)", (agreements[0], end_args[5], second_start[10]))
            assert cur.fetchone()[0] == 2


if __name__ == "__main__":
    import unittest
    unittest.main()
