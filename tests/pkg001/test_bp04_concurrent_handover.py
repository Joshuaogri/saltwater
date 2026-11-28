"""Real multi-session race tests for BP04 physical occupancy handover."""

from __future__ import annotations

import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import psycopg


def _call_handover(dsn: str, app_name: str, barrier: Barrier, args: tuple):
    try:
        with psycopg.connect(dsn, application_name=app_name, options="-c statement_timeout=60000") as conn:
            with conn.cursor() as cur:
                barrier.wait(timeout=15)
                cur.execute(
                    """
                    SELECT *
                    FROM sw_property.handover_business_occupancy(
                      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
                    """,
                    args,
                )
                return ("ok", cur.fetchone(), None)
    except Exception as exc:  # expected loser in competing-writer test
        return ("error", None, str(exc))


def _run_locked_pair(dsn: str, unit_id: str, left: tuple, right: tuple):
    blocker = psycopg.connect(dsn, application_name="bp04-concurrency-blocker", options="-c statement_timeout=60000")
    try:
        with blocker.cursor() as cur:
            cur.execute(
                "SELECT unit_id FROM sw_property.unit_space WHERE unit_id=%s FOR UPDATE",
                (unit_id,),
            )
            if cur.fetchone() is None:
                raise AssertionError("concurrency fixture unit disappeared")

        barrier = Barrier(3)
        with ThreadPoolExecutor(max_workers=2) as pool:
            f1 = pool.submit(_call_handover, dsn, "bp04-concurrency-left", barrier, left)
            f2 = pool.submit(_call_handover, dsn, "bp04-concurrency-right", barrier, right)
            barrier.wait(timeout=15)

            # Hold the unit lock until both independent sessions are queued on it.
            deadline = time.monotonic() + 10
            waiting = 0
            while time.monotonic() < deadline:
                with blocker.cursor() as cur:
                    cur.execute(
                        """
                        SELECT pid,application_name,state,wait_event_type,wait_event,
                               pg_blocking_pids(pid)
                        FROM pg_stat_activity
                        WHERE application_name IN (
                          'bp04-concurrency-left','bp04-concurrency-right'
                        )
                        ORDER BY application_name
                        """
                    )
                    states = cur.fetchall()
                waiting = sum(
                    1 for row in states
                    if row[2] == "active" and row[3] == "Lock" and bool(row[5])
                )
                if waiting == 2:
                    break
                time.sleep(0.05)
            if waiting != 2:
                raise AssertionError(
                    "expected two concurrent handover sessions blocked on the held unit row; "
                    f"observed sessions={states!r}"
                )
            blocker.commit()
            return f1.result(timeout=30), f2.result(timeout=30)
    finally:
        if not blocker.closed:
            blocker.rollback()
            blocker.close()


def _seed_fixture(dsn: str, token: str):
    prop = f"SWCONC-PROP-{token}"
    premises = f"SWCONC-PREM-{token}"
    unit = f"SWCONC-UNIT-{token}"
    businesses = [f"SWCONC-BUS-{token}-{i}" for i in range(1, 4)]
    establishments = [f"SWCONC-EST-{token}-{i}" for i in range(1, 4)]
    agreements = [f"SWCONC-AGR-{token}-{i}" for i in range(1, 4)]
    occupancy = f"SWCONC-OCC-{token}-1"
    link = f"SWCONC-LINK-{token}-1"

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sw_property.property_site(
                  property_id,display_name,lifecycle_status,source_dataset
                ) VALUES (%s,%s,'active','bp04_concurrency_acceptance')
                """,
                (prop, f"Concurrency Fixture {token}"),
            )
            cur.execute(
                """
                INSERT INTO sw_property.premises(
                  premises_id,property_id,display_name,premises_use,lifecycle_status,source_dataset
                ) VALUES (%s,%s,%s,'commercial','active','bp04_concurrency_acceptance')
                """,
                (premises, prop, f"Concurrency Premises {token}"),
            )
            cur.execute(
                """
                INSERT INTO sw_property.unit_space(
                  unit_id,property_id,premises_id,display_name,unit_class,use_class,
                  lifecycle_status,source_dataset
                ) VALUES (%s,%s,%s,%s,'commercial','commercial','active','bp04_concurrency_acceptance')
                """,
                (unit, prop, premises, f"Concurrency Unit {token}"),
            )
            for i, business in enumerate(businesses, start=1):
                cur.execute(
                    """
                    INSERT INTO sw_property.business(
                      business_id,display_name,sector,status,source_dataset
                    ) VALUES (%s,%s,'professional_services','active','bp04_concurrency_acceptance')
                    """,
                    (business, f"Concurrency Business {token} {i}"),
                )
                cur.execute(
                    """
                    INSERT INTO sw_property.establishment(
                      establishment_id,business_id,property_id,premises_id,unit_id,
                      display_name,establishment_type,status,source_dataset
                    ) VALUES (%s,%s,%s,%s,%s,%s,'primary','active','bp04_concurrency_acceptance')
                    """,
                    (establishments[i - 1], business, prop, premises, unit, f"Concurrency Establishment {token} {i}"),
                )
                cur.execute(
                    """
                    INSERT INTO sw_property.occupancy_agreement(
                      agreement_id,property_id,premises_id,unit_id,tenant_business_id,
                      operator_business_id,establishment_id,agreement_type,commencement_year,
                      agreement_status,source_dataset
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,'commercial_occupancy_lease',2027,
                              'active','bp04_concurrency_acceptance')
                    """,
                    (
                        agreements[i - 1], prop, premises, unit, business, business,
                        establishments[i - 1],
                    ),
                )
            cur.execute(
                """
                INSERT INTO sw_property.occupancy(
                  occupancy_id,property_id,premises_id,unit_id,occupant_business_id,
                  establishment_id,agreement_id,occupant_type,occupancy_status,
                  effective_from_year,effective_to_year,source_dataset
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,'business','occupied',2027,NULL,
                          'bp04_concurrency_acceptance')
                """,
                (occupancy, prop, premises, unit, businesses[0], establishments[0], agreements[0]),
            )
            cur.execute(
                """
                INSERT INTO sw_property.business_unit_link(
                  business_unit_link_id,business_id,establishment_id,unit_id,premises_id,
                  valid_from_tick,valid_to_tick,occupancy_relationship,occupancy_status,source_dataset
                ) VALUES (%s,%s,%s,%s,%s,0,NULL,'primary_occupant','occupied',
                          'bp04_concurrency_acceptance')
                """,
                (link, businesses[0], establishments[0], unit, premises),
            )
    return prop, unit, businesses, agreements, occupancy


def test_competing_and_idempotent_handover_writers_serialize():
    dsn = os.environ["DATABASE_URL"]
    token = uuid.uuid4().hex[:12]
    prop, unit, businesses, agreements, prior_occupancy = _seed_fixture(dsn, token)

    common = (prop, unit, prior_occupancy)
    left = common + (
        agreements[1], businesses[1], 2028, 1, 1, "actor:race", "source:race",
        f"race:compete:{token}:left", "gameplay_action",
    )
    right = common + (
        agreements[2], businesses[2], 2028, 1, 1, "actor:race", "source:race",
        f"race:compete:{token}:right", "gameplay_action",
    )
    first, second = _run_locked_pair(dsn, unit, left, right)
    successes = [item for item in (first, second) if item[0] == "ok"]
    failures = [item for item in (first, second) if item[0] == "error"]
    assert len(successes) == 1, (first, second)
    assert len(failures) == 1, (first, second)
    assert "prior occupancy must be current" in failures[0][2], failures[0][2]

    winning_row = successes[0][1]
    winning_new_occupancy = winning_row[2]
    # Resolve the actual winner from the committed new occupancy row.
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT occupant_business_id FROM sw_property.occupancy WHERE occupancy_id=%s",
                (winning_new_occupancy,),
            )
            winning_business = cur.fetchone()[0]
            cur.execute(
                "SELECT count(*) FROM sw_property.occupancy_handover_event WHERE property_id=%s",
                (prop,),
            )
            assert cur.fetchone()[0] == 1
            cur.execute(
                "SELECT count(*) FROM sw_property.business_unit_link WHERE unit_id=%s AND valid_to_tick IS NULL",
                (unit,),
            )
            assert cur.fetchone()[0] == 1

    loser_index = 2 if winning_business == businesses[1] else 1
    current_occupancy = winning_new_occupancy
    replay_args = (
        prop, unit, current_occupancy, agreements[loser_index], businesses[loser_index],
        2029, 2, 2, "actor:replay", "source:replay",
        f"race:exact:{token}", "gameplay_action",
    )
    replay_one, replay_two = _run_locked_pair(dsn, unit, replay_args, replay_args)
    assert replay_one[0] == "ok", replay_one
    assert replay_two[0] == "ok", replay_two
    assert replay_one[1] == replay_two[1], (replay_one, replay_two)

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM sw_property.occupancy_handover_event WHERE property_id=%s AND idempotency_key=%s",
                (prop, f"race:exact:{token}"),
            )
            assert cur.fetchone()[0] == 1
            cur.execute(
                "SELECT count(*) FROM sw_property.business_unit_link WHERE unit_id=%s AND valid_to_tick IS NULL",
                (unit,),
            )
            assert cur.fetchone()[0] == 1

    print("BP04 concurrent handover serialization and idempotency acceptance passed")


if __name__ == '__main__':
    test_competing_and_idempotent_handover_writers_serialize()
