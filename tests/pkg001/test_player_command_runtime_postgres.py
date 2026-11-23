"""PKG-005 real PostgreSQL command-path integration test.

Runs only in the disposable PostgreSQL CI service after proposals 0001-0005.
"""
import os
import unittest
from uuid import uuid4

import psycopg

from runtime.player_activation import PostgresPlayerActivationService
from runtime.player_command_runtime import PostgresPlayerCommandRuntime
from runtime.postgres_security import (
    PostgresAuditSink,
    PostgresGrantProvider,
    PostgresSessionVerifier,
)
from runtime.postgres_sessions import PostgresSessionLifecycle
from runtime.recruitment import PostgresRecruitmentService
from runtime.security import AuthorizationService


def connect():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
    )


def create_person(cur, suffix):
    cur.execute(
        "SELECT event_type_id FROM sw_core.event_type WHERE event_code='PERSON_CREATED'"
    )
    person_event_type = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO sw_core.simulation_event
          (event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key)
        VALUES (%s,now(),0,'person',%s,'{}'::jsonb,%s)
        RETURNING event_id
        """,
        (person_event_type, "pkg005:" + suffix, "pkg005-person:" + suffix),
    )
    event_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO sw_people.person(created_tick,source_ref,last_event_id)
        VALUES (0,%s,%s) RETURNING person_id
        """,
        ("pkg005:" + suffix, event_id),
    )
    person_id = cur.fetchone()[0]

    cur.execute(
        "SELECT event_type_id FROM sw_core.event_type WHERE event_code='POPULATION_STATE_CHANGED'"
    )
    population_event_type = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO sw_core.simulation_event
          (event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key)
        VALUES (%s,now(),0,'person',%s,%s,
                '{"life_status":1,"scope_status":1}'::jsonb,%s)
        RETURNING event_id
        """,
        (
            population_event_type, person_id, "pkg005:" + suffix,
            "pkg005-population:" + suffix,
        ),
    )
    population_event_id = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO sw_people.population_state
          (person_id,life_status,scope_status,effective_tick,last_event_id)
        VALUES (%s,1,1,0,%s)
        """,
        (person_id, population_event_id),
    )
    return person_id


class PlayerCommandRuntimePostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suffix = uuid4().hex
        cls.player_id = uuid4()
        cls.principal_id = uuid4()
        cls.admin_id = uuid4()
        cls.policy = "pkg005-" + cls.suffix
        cls.display_name = "PKG-005 Database Player"

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE sw_auth.policy_version SET active=false WHERE active=true")
                cur.execute(
                    """
                    INSERT INTO sw_auth.policy_version(policy_version,description,active)
                    VALUES (%s,'PKG-005 disposable runtime test',true)
                    """,
                    (cls.policy,),
                )
                cur.execute(
                    """
                    INSERT INTO sw_auth.principal(principal_id,issuer,subject,principal_kind,status)
                    VALUES (%s,'pkg005-test',%s,'administrator','active'),
                           (%s,'pkg005-test',%s,'player','active')
                    """,
                    (
                        cls.admin_id, "admin-" + cls.suffix,
                        cls.principal_id, "player-" + cls.suffix,
                    ),
                )
                cur.execute(
                    """
                    INSERT INTO sw_auth.principal_role(principal_id,role_code,assigned_by)
                    VALUES (%s,'recruitment_approver',%s)
                    """,
                    (cls.admin_id, cls.admin_id),
                )

                # Fresh disposable database starts ready at tick zero.
                cur.execute(
                    "UPDATE sw_runtime.state SET state=1,player_present=false WHERE singleton=1 AND state=0"
                )
                cur.execute(
                    "UPDATE sw_runtime.state SET bootstrap_open=false WHERE singleton=1 AND bootstrap_open=true"
                )
                cur.execute(
                    "UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1 AND state=1"
                )

                cur.execute(
                    "SELECT person_id FROM sw_people.person ORDER BY person_id LIMIT 2"
                )
                fixture_people = cur.fetchall()
                if len(fixture_people) != 2:
                    raise AssertionError("storage fixture must provide two canonical people")
                supervisor_person = fixture_people[0][0]
                supervisor_of_supervisor = fixture_people[1][0]
                cur.execute(
                    "SELECT world_tick FROM sw_runtime.state WHERE singleton=1"
                )
                current_tick = cur.fetchone()[0]
                cur.execute(
                    """
                    SELECT event_type_id FROM sw_core.event_type
                    WHERE event_code='PERSONNEL_APPOINTED'
                    """
                )
                appointment_type = cur.fetchone()[0]
                cur.execute(
                    """
                    INSERT INTO sw_core.simulation_event
                      (event_type_id,occurred_at,world_tick,subject_kind,subject_id,
                       source_ref,attributes,idempotency_key)
                    VALUES (%s,now(),0,'person',%s,'PKG-005 fixture',
                            '{"standing":"established"}'::jsonb,%s)
                    RETURNING event_id
                    """,
                    (
                        appointment_type, current_tick, supervisor_person,
                        "pkg005-supervisor-appointment:" + cls.suffix,
                    ),
                )
                appointment_event = cur.fetchone()[0]
                personnel_id = uuid4()
                cur.execute(
                    """
                    INSERT INTO sw_police.personnel
                      (personnel_id,person_id,service_number,service_standing,service_status,
                       supervisor_person_id,appointment_tick,appointment_source,appointment_event_id)
                    VALUES (%s,%s,%s,'established','active',%s,%s,'PKG-005 fixture',%s)
                    """,
                    (
                        personnel_id, supervisor_person, "PKG5-" + cls.suffix[:16],
                        supervisor_of_supervisor, current_tick, appointment_event,
                    ),
                )
                cur.execute(
                    """
                    INSERT INTO sw_police.recruit_supervisor_authorisation
                      (person_id,authorised_by_principal_id,authority_source,effective_tick)
                    VALUES (%s,%s,'PKG-005 disposable fixture',0)
                    """,
                    (supervisor_person, cls.admin_id),
                )

        recruitment = PostgresRecruitmentService(connect)
        intake_id = recruitment.request_intake(
            cls.player_id, cls.display_name, "pkg005-request:" + cls.suffix
        )
        recruitment.accept_intake(
            intake_id,
            supervisor_person_id=supervisor_person,
            appointment_source="PKG-005 disposable integration fixture",
            idempotency_key="pkg005-accept:" + cls.suffix,
            authorised_by_principal_id=cls.admin_id,
            given_name="Test",
            family_name="Player",
        )
        activation = PostgresPlayerActivationService(
            connect, PostgresSessionLifecycle(connect)
        ).activate(cls.principal_id, cls.player_id)
        cls.credential = activation.session.credential
        cls.session_id = activation.session.session_id

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT count(*) FROM sw_auth.permission_grant
                    WHERE principal_id=%s
                    """,
                    (cls.principal_id,),
                )
                if cur.fetchone()[0] != 0:
                    raise AssertionError("PKG-004 activation unexpectedly created grants")
                cur.execute(
                    """
                    INSERT INTO sw_auth.permission_grant
                      (action,resource_pattern,purpose,effect,principal_id,policy_version)
                    VALUES ('player.command.profile',%s,'gameplay','allow',%s,%s)
                    """,
                    ("player:" + str(cls.player_id), cls.principal_id, cls.policy),
                )

        verifier = PostgresSessionVerifier(connect)
        cls.audit = PostgresAuditSink(connect)
        cls.runtime = PostgresPlayerCommandRuntime(
            connect,
            verifier,
            AuthorizationService(verifier, cls.audit, PostgresGrantProvider(connect)),
        )

    def test_authoritative_profile_grant_revocation_and_durable_audit(self):
        allowed = self.runtime.execute(self.credential, "profile")
        self.assertTrue(allowed.ok, allowed.message)
        self.assertIn(self.display_name, allowed.message)
        self.assertIn(str(self.player_id), allowed.message)
        self.assertIn("recruit", allowed.message)

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT count(*) FROM sw_auth.audit
                    WHERE session_id=%s AND action='player.command.profile'
                      AND allowed=true AND reason='explicit_allow'
                    """,
                    (self.session_id,),
                )
                self.assertEqual(cur.fetchone()[0], 1)

        self.assertTrue(
            PostgresSessionLifecycle(connect).revoke(
                self.session_id, principal_id=self.principal_id
            )
        )
        denied = self.runtime.execute(self.credential, "profile")
        self.assertFalse(denied.ok)
        self.assertEqual(denied.message, "Access denied.")

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT allowed,reason FROM sw_auth.audit
                    WHERE session_id=%s AND action='player.command.profile'
                    ORDER BY audit_id
                    """,
                    (self.session_id,),
                )
                self.assertEqual(
                    cur.fetchall(),
                    [(True, "explicit_allow"), (False, "session_not_active")],
                )
                # Return the disposable runtime to stopped state for the
                # following population-cap fixture; no world tick advanced.
                cur.execute(
                    "UPDATE sw_runtime.state SET state=0,player_present=false WHERE singleton=1 AND state=2"
                )


if __name__ == "__main__":
    unittest.main()
