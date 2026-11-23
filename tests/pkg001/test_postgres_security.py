import hashlib
import os
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg

from runtime.postgres_security import PostgresAuditSink, PostgresSessionVerifier
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


if __name__ == "__main__":
    unittest.main()
