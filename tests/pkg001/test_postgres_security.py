import hashlib
import os
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg

from runtime.postgres_security import (
    PostgresAuditSink,
    PostgresGrantProvider,
    PostgresSessionVerifier,
)
from runtime.postgres_sessions import PostgresSessionLifecycle
from runtime.security import AuthorizationService, Effect, Grant


def connect():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
    )


class PostgresSecurityAdapterTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        suffix = uuid4().hex
        self.principal_id = uuid4()
        self.session_id = uuid4()
        self.policy = "adapter-" + suffix
        self.token = "saltwater-test-token-" + suffix
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE sw_auth.policy_version SET active=false WHERE active=true")
                cur.execute(
                    "INSERT INTO sw_auth.policy_version(policy_version,description,active) VALUES (%s,%s,true)",
                    (self.policy, "Disposable adapter test"),
                )
                cur.execute(
                    """INSERT INTO sw_auth.principal
                       (principal_id,issuer,subject,principal_kind)
                       VALUES (%s,%s,%s,'player')""",
                    (self.principal_id, "test-issuer", suffix),
                )
                cur.execute(
                    """INSERT INTO sw_auth.session
                       (session_id,principal_id,credential_digest,issued_at,expires_at,policy_version)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (self.session_id, self.principal_id,
                     hashlib.sha256(self.token.encode()).digest(),
                     self.now-timedelta(minutes=1), self.now+timedelta(hours=1), self.policy),
                )
                cur.execute(
                    "INSERT INTO sw_auth.principal_role(principal_id,role_code) VALUES (%s,'player')",
                    (self.principal_id,),
                )
        self.verifier = PostgresSessionVerifier(connect)
        self.audit = PostgresAuditSink(connect)

    def test_verifier_and_durable_audit_work_end_to_end(self):
        session = self.verifier.verify(self.token)
        self.assertEqual(session.principal_id, self.principal_id)
        self.assertEqual(session.session_id, self.session_id)
        self.assertIn("player", session.roles)
        auth = AuthorizationService(
            self.verifier, self.audit,
            (Grant("read_case", "case/*", "active_play", Effect.ALLOW,
                   principal_kind=session.principal_kind),),
        )
        decision = auth.decide(
            self.token, action="read_case", resource="case/test",
            purpose="active_play", now=self.now,
        )
        self.assertTrue(decision.allowed)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM sw_auth.audit WHERE session_id=%s", (self.session_id,))
                self.assertEqual(cur.fetchone()[0], 1)
                cur.execute("SELECT count(*) FROM sw_auth.session WHERE credential_digest=%s",
                            (hashlib.sha256(self.token.encode()).digest(),))
                self.assertEqual(cur.fetchone()[0], 1)

    def test_revoked_session_and_disabled_principal_are_denied(self):
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE sw_auth.session SET status='revoked',revoked_at=now() WHERE session_id=%s",
                    (self.session_id,),
                )
        session = self.verifier.verify(self.token)
        self.assertEqual(session.session_status.value, "revoked")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE sw_auth.principal SET status='disabled' WHERE principal_id=%s", (self.principal_id,))
        auth = AuthorizationService(self.verifier, self.audit)
        self.assertFalse(auth.decide(
            self.token, action="read_case", resource="case/test",
            purpose="active_play", now=self.now,
        ).allowed)

    def test_inactive_policy_restricts_existing_session(self):
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE sw_auth.policy_version SET active=false WHERE policy_version=%s", (self.policy,))
                cur.execute(
                    "INSERT INTO sw_auth.policy_version(policy_version,description,active) VALUES (%s,%s,true)",
                    (self.policy+"-next", "Replacement test policy"),
                )
        session = self.verifier.verify(self.token)
        self.assertEqual(session.session_status.value, "restricted")
        auth = AuthorizationService(self.verifier, self.audit)
        self.assertFalse(auth.decide(
            self.token, action="read_case", resource="case/test",
            purpose="active_play", now=self.now,
        ).allowed)


    def test_postgres_session_authorizes_composed_player_command_and_audits_it(self):
        from runtime.application import (
            bind_authorized_player_commands,
            create_postgres_player_application,
        )
        from runtime.player_interface import PlayerProfile
        from runtime.security import Effect, Grant

        profile = PlayerProfile(str(self.principal_id), "Database-backed Player")
        application = create_postgres_player_application(connect, profile)
        authorization = AuthorizationService(
            self.verifier,
            self.audit,
            (
                Grant(
                    "player.command.profile",
                    f"player:{profile.player_id}",
                    "gameplay",
                    Effect.ALLOW,
                    principal_id=self.principal_id,
                ),
            ),
        )
        gateway = bind_authorized_player_commands(
            application, authorization, self.principal_id
        )

        result = gateway.execute(self.token, "profile")

        self.assertTrue(result.ok)
        self.assertIn("Database-backed Player", result.message)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT action, resource, purpose, allowed, reason
                       FROM sw_auth.audit WHERE session_id=%s
                       ORDER BY audit_id DESC LIMIT 1""",
                    (self.session_id,),
                )
                audit = cur.fetchone()
        self.assertEqual(
            audit,
            (
                "player.command.profile",
                f"player:{profile.player_id}",
                "gameplay",
                True,
                "explicit_allow",
            ),
        )

    def test_postgres_session_without_command_grant_is_denied_and_audited(self):
        from runtime.application import (
            bind_authorized_player_commands,
            create_postgres_player_application,
        )
        from runtime.player_interface import PlayerProfile

        profile = PlayerProfile(str(self.principal_id), "Unprivileged Player")
        application = create_postgres_player_application(connect, profile)
        authorization = AuthorizationService(self.verifier, self.audit, ())
        gateway = bind_authorized_player_commands(
            application, authorization, self.principal_id
        )

        result = gateway.execute(self.token, "profile")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "Access denied.")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT action, allowed, reason FROM sw_auth.audit
                       WHERE session_id=%s ORDER BY audit_id DESC LIMIT 1""",
                    (self.session_id,),
                )
                audit = cur.fetchone()
        self.assertEqual(
            audit,
            ("player.command.profile", False, "no_matching_grant"),
        )


    def test_postgres_grants_are_loaded_and_revocation_takes_effect_immediately(self):
        from runtime.application import (
            bind_authorized_player_commands,
            create_postgres_player_application,
        )
        from runtime.player_interface import PlayerProfile

        profile = PlayerProfile(str(self.principal_id), "Grant-backed Player")
        application = create_postgres_player_application(connect, profile)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sw_auth.permission_grant
                      (action,resource_pattern,purpose,effect,principal_id,policy_version)
                    VALUES (%s,%s,%s,'allow',%s,%s)
                    """,
                    (
                        "player.command.profile",
                        f"player:{profile.player_id}",
                        "gameplay",
                        self.principal_id,
                        self.policy,
                    ),
                )
        authorization = AuthorizationService(
            self.verifier, self.audit, PostgresGrantProvider(connect)
        )
        gateway = bind_authorized_player_commands(
            application, authorization, self.principal_id
        )

        allowed = gateway.execute(self.token, "profile")
        self.assertTrue(allowed.ok)
        self.assertIn("Grant-backed Player", allowed.message)

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sw_auth.permission_grant
                    SET revoked_at=now()
                    WHERE action=%s AND principal_id=%s AND policy_version=%s
                    """,
                    ("player.command.profile", self.principal_id, self.policy),
                )
        denied = gateway.execute(self.token, "profile")
        self.assertFalse(denied.ok)
        self.assertEqual(denied.message, "Access denied.")
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT allowed, reason FROM sw_auth.audit
                    WHERE session_id=%s AND action='player.command.profile'
                    ORDER BY audit_id DESC LIMIT 2
                    """,
                    (self.session_id,),
                )
                audit = cur.fetchall()
        self.assertEqual(audit, [(False, "no_matching_grant"), (True, "explicit_allow")])


    def test_game_native_session_issue_hashes_credential_and_revokes(self):
        lifecycle = PostgresSessionLifecycle(connect)
        issued = lifecycle.issue(
            self.principal_id,
            lifetime=timedelta(minutes=30),
            now=self.now,
        )
        self.assertNotEqual(
            issued.credential,
            hashlib.sha256(issued.credential.encode("utf-8")).hexdigest(),
        )
        verified = self.verifier.verify(issued.credential)
        self.assertIsNotNone(verified)
        self.assertEqual(verified.session_id, issued.session_id)
        self.assertEqual(verified.principal_id, self.principal_id)

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT credential_digest FROM sw_auth.session WHERE session_id=%s",
                    (issued.session_id,),
                )
                stored_digest = cur.fetchone()[0]
        self.assertEqual(
            stored_digest,
            hashlib.sha256(issued.credential.encode("utf-8")).digest(),
        )
        self.assertTrue(
            lifecycle.revoke(issued.session_id, principal_id=self.principal_id, now=self.now)
        )
        self.assertFalse(lifecycle.revoke(issued.session_id, now=self.now))
        revoked = self.verifier.verify(issued.credential)
        self.assertEqual(revoked.session_status.value, "revoked")

    def test_session_issue_rejects_inactive_principal_and_bad_lifetime(self):
        lifecycle = PostgresSessionLifecycle(connect)
        with self.assertRaises(ValueError):
            lifecycle.issue(self.principal_id, lifetime=timedelta(0))
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE sw_auth.principal SET status='disabled' WHERE principal_id=%s",
                    (self.principal_id,),
                )
        with self.assertRaises(PermissionError):
            lifecycle.issue(self.principal_id)


if __name__ == "__main__":
    unittest.main()
