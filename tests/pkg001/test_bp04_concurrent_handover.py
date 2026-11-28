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
                    if row[3] == "Lock" and bool(row[5])
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


def _call_subletting(dsn: str, app_name: str, barrier: Barrier, args: tuple):
    try:
        with psycopg.connect(dsn, application_name=app_name, options="-c statement_timeout=60000") as conn:
            with conn.cursor() as cur:
                barrier.wait(timeout=15)
                cur.execute(
                    """SELECT * FROM sw_property.record_subletting_relationship(
                       %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    args,
                )
                return ("ok", cur.fetchone(), None)
    except Exception as exc:
        return ("error", None, str(exc))


def test_concurrent_exact_subletting_creation_is_idempotent():
    dsn = os.environ["DATABASE_URL"]
    token = uuid.uuid4().hex[:12]
    prop, unit, businesses, agreements, superior_occupancy = _seed_fixture(dsn, token)
    sub_occupancy = f"SWCONC-OCC-{token}-SUB"
    right_id = f"SWCONC-RIGHT-{token}-SUB"
    lease_right_id = f"SWCONC-RIGHT-{token}-LEASE"
    relationship_id = f"SWCONC-REL-{token}-SUB"
    idempotency_key = f"sublet:concurrent:{token}"
    sub_establishment = f"SWCONC-EST-{token}-2"

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sw_property.occupancy_agreement SET agreement_type='sublease' WHERE agreement_id=%s",
                (agreements[1],),
            )
            cur.execute(
                """
                INSERT INTO sw_property.occupancy(
                  occupancy_id,property_id,premises_id,unit_id,occupant_business_id,
                  establishment_id,agreement_id,occupant_type,occupancy_status,
                  effective_from_year,effective_to_year,source_dataset
                )
                SELECT %s,%s,premises_id,unit_id,%s,%s,%s,'business_subtenant',
                       'occupied',2027,NULL,'bp04_concurrent_subletting_acceptance'
                FROM sw_property.occupancy_agreement WHERE agreement_id=%s
                """,
                (sub_occupancy, prop, businesses[1], sub_establishment, agreements[1], agreements[1]),
            )
            cur.execute(
                """
                INSERT INTO sw_property.contractual_rights_index(
                  property_right_id,property_id,premises_id,unit_id,right_type,
                  holder_business_id,source_agreement_id,commencement_year,right_status,
                  permitted_use,source_of_truth,new_legal_instrument_created,source_dataset
                )
                VALUES (%s,%s,
                  (SELECT premises_id FROM sw_property.occupancy_agreement WHERE agreement_id=%s),
                  %s,'subletting',%s,%s,2027,'current','commercial',
                  'bp04_concurrent_subletting_acceptance',false,
                  'bp04_concurrent_subletting_acceptance')
                """,
                (right_id, prop, agreements[0], unit, businesses[0], agreements[0]),
            )

    args = (
        relationship_id, agreements[0], agreements[1], superior_occupancy,
        sub_occupancy, right_id, 5, 5, "actor:subletting-race",
        "source:subletting-race", idempotency_key,
    )
    blocker = psycopg.connect(
        dsn, application_name="bp04-subletting-blocker",
        options="-c statement_timeout=60000",
    )
    try:
        with blocker.cursor() as cur:
            cur.execute(
                """
                SELECT agreement_id FROM sw_property.occupancy_agreement
                WHERE agreement_id IN (%s,%s) ORDER BY agreement_id FOR UPDATE
                """,
                (agreements[0], agreements[1]),
            )
            assert len(cur.fetchall()) == 2
        barrier = Barrier(3)
        names = ("bp04-subletting-left", "bp04-subletting-right")
        with ThreadPoolExecutor(max_workers=2) as pool:
            f1 = pool.submit(_call_subletting, dsn, names[0], barrier, args)
            f2 = pool.submit(_call_subletting, dsn, names[1], barrier, args)
            barrier.wait(timeout=15)
            deadline = time.monotonic() + 10
            waiting = 0
            while time.monotonic() < deadline:
                with blocker.cursor() as cur:
                    cur.execute(
                        """SELECT wait_event_type,pg_blocking_pids(pid)
                           FROM pg_stat_activity WHERE application_name IN (%s,%s)""",
                        names,
                    )
                    states = cur.fetchall()
                waiting = sum(1 for state in states if state[0] == "Lock" and state[1])
                if waiting == 2:
                    break
                time.sleep(0.05)
            if waiting != 2:
                raise AssertionError(f"expected two blocked subletting writers, observed {states!r}")
            blocker.commit()
            first, second = f1.result(timeout=30), f2.result(timeout=30)
    finally:
        if not blocker.closed:
            blocker.rollback()
            blocker.close()

    assert first[0] == "ok", first
    assert second[0] == "ok", second
    assert first[1] == second[1], (first, second)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM sw_property.occupancy_relationship WHERE idempotency_key=%s",
                (idempotency_key,),
            )
            assert cur.fetchone()[0] == 1
            cur.execute(
                """SELECT count(*) FROM sw_property.occupancy_agreement_event
                   WHERE agreement_id=%s AND idempotency_key=%s""",
                (agreements[0], idempotency_key),
            )
            assert cur.fetchone()[0] == 1
    print("BP04 concurrent subletting exact-replay acceptance passed")


def _call_assignment(dsn: str, app_name: str, barrier: Barrier, args: tuple):
    try:
        with psycopg.connect(dsn, application_name=app_name, options="-c statement_timeout=60000") as conn:
            with conn.cursor() as cur:
                barrier.wait(timeout=15)
                cur.execute(
                    """SELECT * FROM sw_property.assign_occupancy_agreement_tenant(
                       %s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    args,
                )
                return ("ok", cur.fetchone(), None)
    except Exception as exc:
        return ("error", None, str(exc))


def test_subletting_creation_serializes_with_tenant_assignment():
    dsn = os.environ["DATABASE_URL"]
    token = uuid.uuid4().hex[:12]
    prop, unit, businesses, agreements, superior_occupancy = _seed_fixture(dsn, token)
    sub_occupancy = f"SWCONC-OCC-{token}-SUB"
    right_id = f"SWCONC-RIGHT-{token}-SUB"
    lease_right_id = f"SWCONC-RIGHT-{token}-LEASE"
    relationship_id = f"SWCONC-REL-{token}-SUB"
    sub_idempotency_key = f"sublet:assignment-race:{token}"
    assignment_idempotency_key = f"assignment:sublet-race:{token}"
    sub_establishment = f"SWCONC-EST-{token}-2"

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sw_property.occupancy_agreement SET agreement_type='sublease' WHERE agreement_id=%s",
                (agreements[1],),
            )
            cur.execute(
                """
                INSERT INTO sw_property.occupancy(
                  occupancy_id,property_id,premises_id,unit_id,occupant_business_id,
                  establishment_id,agreement_id,occupant_type,occupancy_status,
                  effective_from_year,effective_to_year,source_dataset
                )
                SELECT %s,%s,premises_id,unit_id,%s,%s,%s,'business_subtenant',
                       'occupied',2027,NULL,'bp04_subletting_assignment_race'
                FROM sw_property.occupancy_agreement WHERE agreement_id=%s
                """,
                (sub_occupancy, prop, businesses[1], sub_establishment, agreements[1], agreements[1]),
            )
            cur.execute(
                """
                INSERT INTO sw_property.contractual_rights_index(
                  property_right_id,property_id,premises_id,unit_id,right_type,
                  holder_business_id,source_agreement_id,commencement_year,right_status,
                  permitted_use,source_of_truth,new_legal_instrument_created,source_dataset
                )
                VALUES (%s,%s,
                  (SELECT premises_id FROM sw_property.occupancy_agreement WHERE agreement_id=%s),
                  %s,'contractual_lease_licence_or_concession',%s,%s,2027,'current','commercial',
                  'bp04_subletting_assignment_race',false,'bp04_subletting_assignment_race')
                """,
                (lease_right_id, prop, agreements[0], unit, businesses[0], agreements[0]),
            )
            cur.execute(
                """
                INSERT INTO sw_property.contractual_rights_index(
                  property_right_id,property_id,premises_id,unit_id,right_type,
                  holder_business_id,source_agreement_id,commencement_year,right_status,
                  permitted_use,source_of_truth,new_legal_instrument_created,source_dataset
                )
                VALUES (%s,%s,
                  (SELECT premises_id FROM sw_property.occupancy_agreement WHERE agreement_id=%s),
                  %s,'subletting',%s,%s,2027,'current','commercial',
                  'bp04_subletting_assignment_race',false,'bp04_subletting_assignment_race')
                """,
                (right_id, prop, agreements[0], unit, businesses[0], agreements[0]),
            )

    sub_args = (
        relationship_id, agreements[0], agreements[1], superior_occupancy,
        sub_occupancy, right_id, 1, 1, "actor:assignment-race",
        "source:assignment-race", sub_idempotency_key,
    )
    assignment_args = (
        agreements[0], businesses[0], businesses[2], 1, 1,
        "actor:assignment-race", "source:assignment-race",
        assignment_idempotency_key, "gameplay_action",
    )

    blocker = psycopg.connect(
        dsn, application_name="bp04-assignment-race-blocker",
        options="-c statement_timeout=60000",
    )
    try:
        with blocker.cursor() as cur:
            cur.execute(
                """
                SELECT agreement_id FROM sw_property.occupancy_agreement
                WHERE agreement_id IN (%s,%s) ORDER BY agreement_id FOR UPDATE
                """,
                (agreements[0], agreements[1]),
            )
            assert len(cur.fetchall()) == 2
        barrier = Barrier(3)
        with ThreadPoolExecutor(max_workers=2) as pool:
            sub_future = pool.submit(
                _call_subletting, dsn, "bp04-race-subletting", barrier, sub_args
            )
            assignment_future = pool.submit(
                _call_assignment, dsn, "bp04-race-assignment", barrier, assignment_args
            )
            barrier.wait(timeout=15)
            deadline = time.monotonic() + 10
            waiting = 0
            while time.monotonic() < deadline:
                with blocker.cursor() as cur:
                    cur.execute(
                        """
                        SELECT wait_event_type,pg_blocking_pids(pid)
                        FROM pg_stat_activity
                        WHERE application_name IN ('bp04-race-subletting','bp04-race-assignment')
                        """
                    )
                    states = cur.fetchall()
                waiting = sum(1 for state in states if state[0] == "Lock" and state[1])
                if waiting == 2:
                    break
                time.sleep(0.05)
            if waiting != 2:
                raise AssertionError(f"expected both writers blocked on agreement rows; observed {states!r}")
            blocker.commit()
            sub_result = sub_future.result(timeout=30)
            assignment_result = assignment_future.result(timeout=30)
    finally:
        if not blocker.closed:
            blocker.rollback()
            blocker.close()

    outcomes = (sub_result, assignment_result)
    assert sum(result[0] == "ok" for result in outcomes) == 1, outcomes
    assert sum(result[0] == "error" for result in outcomes) == 1, outcomes

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tenant_business_id FROM sw_property.occupancy_agreement WHERE agreement_id=%s",
                (agreements[0],),
            )
            tenant = cur.fetchone()[0]
            cur.execute(
                "SELECT right_status FROM sw_property.contractual_rights_index WHERE property_right_id=%s",
                (right_id,),
            )
            right_status = cur.fetchone()[0]
            cur.execute(
                "SELECT relationship_status FROM sw_property.occupancy_relationship WHERE relationship_id=%s",
                (relationship_id,),
            )
            relationship = cur.fetchone()
            cur.execute(
                "SELECT occupant_business_id,effective_to_year FROM sw_property.occupancy WHERE occupancy_id=%s",
                (superior_occupancy,),
            )
            physical_occupancy = cur.fetchone()

    if sub_result[0] == "ok":
        assert tenant == businesses[0]
        assert right_status == "current"
        assert relationship == ("active",)
        assert assignment_result[0] == "error"
    else:
        assert tenant == businesses[2]
        assert right_status == "historical_expired"
        assert relationship is None
        assert assignment_result[0] == "ok"
    assert physical_occupancy == (businesses[0], None)
    print("BP04 subletting creation and tenant assignment serialization acceptance passed")


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


def _call_title_transfer(dsn: str, app_name: str, barrier: Barrier, args: tuple):
    try:
        with psycopg.connect(dsn, application_name=app_name, options="-c statement_timeout=60000") as conn:
            with conn.cursor() as cur:
                barrier.wait(timeout=15)
                cur.execute(
                    """SELECT * FROM sw_property.transfer_property_ownership(
                       %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    args,
                )
                return ("ok", cur.fetchone(), None)
    except Exception as exc:
        return ("error", None, str(exc))


def test_competing_title_transfers_serialize_and_preserve_tenancy():
    """Only one concurrent transfer from an expected proprietor may win."""
    dsn = os.environ["DATABASE_URL"]
    token = uuid.uuid4().hex[:12]
    prop, unit, businesses, agreements, occupancy = _seed_fixture(dsn, token)
    owner = f"SWCONC-ORG-{token}-OWNER"
    successor_a = f"SWCONC-ORG-{token}-A"
    successor_b = f"SWCONC-ORG-{token}-B"
    ownership = f"SWCONC-OWN-{token}"
    title = f"SWCONC-TITLE-{token}"
    interest = f"SWCONC-INTEREST-{token}"
    rights = f"SWCONC-RIGHTS-{token}"

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sw_property.organisation(
                  organisation_id,display_name,organisation_type,registered_city,status,source_dataset
                ) VALUES
                  (%s,%s,'property_holding_company','Saltwater','active','bp04_title_transfer_race'),
                  (%s,%s,'property_holding_company','Saltwater','active','bp04_title_transfer_race'),
                  (%s,%s,'property_holding_company','Saltwater','active','bp04_title_transfer_race')
                """,
                (owner, "Concurrent Title Owner", successor_a, "Title Successor A",
                 successor_b, "Title Successor B"),
            )
            cur.execute(
                """
                INSERT INTO sw_property.ownership_interest(
                  ownership_interest_id,property_id,owner_organisation_id,
                  management_model,interest_type,source_dataset
                ) VALUES (%s,%s,%s,'direct_owner','freehold','bp04_title_transfer_race')
                """,
                (ownership, prop, owner),
            )
            cur.execute(
                """
                INSERT INTO sw_property.property_title_register(
                  title_register_id,property_id,current_ownership_interest_id,
                  registered_proprietor_organisation_id,title_status,tenure_type,
                  registration_tick,source_basis,boundary_record_id,
                  active_dispute_count,unresolved_title_issue_count,source_dataset
                ) VALUES (%s,%s,%s,%s,'registered_current','freehold',0,
                          'generated_fixture','fixture-boundary',0,0,'bp04_title_transfer_race')
                """,
                (title, prop, ownership, owner),
            )
            cur.execute(
                """
                INSERT INTO sw_property.property_interest_record(
                  property_interest_record_id,property_id,ownership_interest_id,
                  interest_holder_organisation_id,interest_type,interest_status,
                  priority_order,source_basis,source_dataset
                ) VALUES (%s,%s,%s,%s,'registered_ownership','current',1,
                          'generated_fixture','bp04_title_transfer_race')
                """,
                (interest, prop, ownership, owner),
            )
            cur.execute(
                """
                INSERT INTO sw_property.property_rights_schedule(
                  property_rights_schedule_id,property_id,title_register_id,
                  registered_ownership_interest_id,registered_owner_organisation_id,
                  current_contractual_right_count,historical_contractual_right_count,
                  right_class_coverage,unverified_right_classes,schedule_status,
                  legal_search_required_before_disposition_or_works,source_dataset
                ) VALUES (%s,%s,%s,%s,%s,1,0,
                          ARRAY['ownership','leasehold_or_occupancy']::text[],
                          ARRAY['easement']::text[],'generated_fixture',true,
                          'bp04_title_transfer_race')
                """,
                (rights, prop, title, ownership, owner),
            )
            cur.execute(
                "UPDATE sw_property.occupancy_agreement SET landlord_organisation_id=%s WHERE agreement_id=%s",
                (owner, agreements[0]),
            )

    common = (prop, owner)
    left = common + (
        successor_a, 11, 11, 2028, 2028, "actor:title-race",
        "source:title-race", f"title-race:{token}:a", "gameplay_action",
    )
    right = common + (
        successor_b, 11, 11, 2028, 2028, "actor:title-race",
        "source:title-race", f"title-race:{token}:b", "gameplay_action",
    )

    blocker = psycopg.connect(
        dsn, application_name="bp04-title-transfer-blocker",
        options="-c statement_timeout=60000",
    )
    try:
        with blocker.cursor() as cur:
            cur.execute(
                "SELECT title_register_id FROM sw_property.property_title_register WHERE title_register_id=%s FOR UPDATE",
                (title,),
            )
            assert cur.fetchone() == (title,)
        barrier = Barrier(3)
        names = ("bp04-title-transfer-left", "bp04-title-transfer-right")
        with ThreadPoolExecutor(max_workers=2) as pool:
            first_future = pool.submit(_call_title_transfer, dsn, names[0], barrier, left)
            second_future = pool.submit(_call_title_transfer, dsn, names[1], barrier, right)
            barrier.wait(timeout=15)
            deadline = time.monotonic() + 10
            waiting = 0
            while time.monotonic() < deadline:
                with blocker.cursor() as cur:
                    cur.execute(
                        """
                        SELECT wait_event_type,pg_blocking_pids(pid)
                        FROM pg_stat_activity WHERE application_name IN (%s,%s)
                        """,
                        names,
                    )
                    states = cur.fetchall()
                waiting = sum(1 for state in states if state[0] == "Lock" and state[1])
                if waiting == 2:
                    break
                time.sleep(0.05)
            if waiting != 2:
                raise AssertionError(
                    "expected both ownership-transfer writers blocked on the title row; "
                    f"observed sessions={states!r}"
                )
            blocker.commit()
            first, second = first_future.result(timeout=30), second_future.result(timeout=30)
    finally:
        if not blocker.closed:
            blocker.rollback()
            blocker.close()

    outcomes = (first, second)
    assert sum(result[0] == "ok" for result in outcomes) == 1, outcomes
    assert sum(result[0] == "error" for result in outcomes) == 1, outcomes
    winner = first if first[0] == "ok" else second
    winning_owner = winner[1][2]
    assert winning_owner in (successor_a, successor_b)

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT registered_proprietor_organisation_id FROM sw_property.property_title_register WHERE title_register_id=%s",
                (title,),
            )
            assert cur.fetchone()[0] == winning_owner
            cur.execute(
                "SELECT owner_organisation_id FROM sw_property.ownership_interest WHERE ownership_interest_id=%s",
                (ownership,),
            )
            assert cur.fetchone()[0] == winning_owner
            cur.execute(
                "SELECT interest_holder_organisation_id FROM sw_property.property_interest_record WHERE property_interest_record_id=%s",
                (interest,),
            )
            assert cur.fetchone()[0] == winning_owner
            cur.execute(
                "SELECT registered_owner_organisation_id FROM sw_property.property_rights_schedule WHERE property_rights_schedule_id=%s",
                (rights,),
            )
            assert cur.fetchone()[0] == winning_owner
            cur.execute(
                "SELECT count(*) FROM sw_property.property_lifecycle_event WHERE property_id=%s AND event_type='ownership_transferred'",
                (prop,),
            )
            assert cur.fetchone()[0] == 1
            cur.execute(
                "SELECT count(*) FROM sw_property.property_title_instrument WHERE property_id=%s",
                (prop,),
            )
            assert cur.fetchone()[0] == 1
            cur.execute(
                "SELECT count(*) FROM sw_property.property_transaction_index WHERE property_id=%s",
                (prop,),
            )
            assert cur.fetchone()[0] == 1
            cur.execute(
                "SELECT landlord_organisation_id,tenant_business_id,operator_business_id FROM sw_property.occupancy_agreement WHERE agreement_id=%s",
                (agreements[0],),
            )
            assert cur.fetchone() == (owner, businesses[0], businesses[0])
            cur.execute(
                "SELECT occupant_business_id,occupancy_status,effective_to_year FROM sw_property.occupancy WHERE occupancy_id=%s",
                (occupancy,),
            )
            assert cur.fetchone() == (businesses[0], "occupied", None)
            cur.execute(
                "SELECT business_id,valid_to_tick FROM sw_property.business_unit_link WHERE unit_id=%s AND valid_to_tick IS NULL",
                (unit,),
            )
            assert cur.fetchone() == (businesses[0], None)

    # The archive-only importer requires its organisation baseline to remain empty.
    # Remove only this disposable concurrency fixture after all assertions pass.
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sw_property.property_transaction_index WHERE property_id=%s", (prop,))
            cur.execute("DELETE FROM sw_property.property_title_instrument WHERE property_id=%s", (prop,))
            cur.execute("ALTER TABLE sw_property.property_lifecycle_event DISABLE TRIGGER property_lifecycle_event_immutable")
            cur.execute("DELETE FROM sw_property.property_lifecycle_event WHERE property_id=%s", (prop,))
            cur.execute("ALTER TABLE sw_property.property_lifecycle_event ENABLE TRIGGER property_lifecycle_event_immutable")
            cur.execute("DELETE FROM sw_property.property_rights_schedule WHERE property_id=%s", (prop,))
            cur.execute("DELETE FROM sw_property.property_interest_record WHERE property_id=%s", (prop,))
            cur.execute("DELETE FROM sw_property.property_title_register WHERE property_id=%s", (prop,))
            cur.execute("UPDATE sw_property.occupancy_agreement SET landlord_organisation_id=NULL WHERE agreement_id=%s", (agreements[0],))
            cur.execute("DELETE FROM sw_property.ownership_interest WHERE property_id=%s", (prop,))
            cur.execute(
                "DELETE FROM sw_property.organisation WHERE organisation_id IN (%s,%s,%s)",
                (owner, successor_a, successor_b),
            )

    print("BP04 competing title-transfer serialization and tenancy-preservation acceptance passed")


if __name__ == '__main__':
    test_competing_and_idempotent_handover_writers_serialize()
    test_concurrent_exact_subletting_creation_is_idempotent()
    test_subletting_creation_serializes_with_tenant_assignment()
    test_competing_title_transfers_serialize_and_preserve_tenancy()
