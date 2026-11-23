"""PKG-005 authenticated player context and command runtime tests."""
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

from runtime.player_command_runtime import (
    PlayerContextError,
    PostgresPlayerCommandRuntime,
    PostgresPlayerContextResolver,
)
from runtime.player_interface import CommandResult
from runtime.security import (
    AuthorizationService,
    InMemoryAuditSink,
    PrincipalKind,
    PrincipalStatus,
    SessionStatus,
    VerifiedSession,
)


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.sql = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=()):
        self.sql, self.params = sql, params

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, cursor):
        self.value = cursor

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cursor(self):
        return self.value


class FakeVerifier:
    def __init__(self, session):
        self.session = session
        self.credentials = []

    def verify(self, credential):
        self.credentials.append(credential)
        return self.session


def make_session(kind=PrincipalKind.PLAYER, status=SessionStatus.ACTIVE):
    now = datetime.now(timezone.utc)
    return VerifiedSession(
        session_id=uuid4(),
        principal_id=uuid4(),
        principal_kind=kind,
        principal_status=PrincipalStatus.ACTIVE,
        session_status=status,
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        active_person_id=712,
        policy_version="test-policy",
    )


class PlayerContextResolverTests(unittest.TestCase):
    def test_resolves_database_profile_and_latest_career(self):
        player_id, career_id = uuid4(), uuid4()
        cursor = FakeCursor([(
            player_id, 712, 712, "Database Name", career_id,
            "recruit", "active", "active",
        )])
        resolver = PostgresPlayerContextResolver(lambda: FakeConnection(cursor))

        result = resolver.resolve(uuid4(), 712)

        self.assertEqual(result.profile.player_id, str(player_id))
        self.assertEqual(result.profile.display_name, "Database Name")
        self.assertEqual(result.profile.officer_person_id, 712)
        self.assertEqual(result.profile.career_id, str(career_id))
        self.assertEqual(result.profile.career_stage, "recruit")
        self.assertIn("sw_player.identity_binding", cursor.sql)
        self.assertIn("LEFT JOIN LATERAL", cursor.sql)

    def test_no_career_is_honestly_unassigned(self):
        player_id = uuid4()
        cursor = FakeCursor([(player_id, 712, 712, "New Player", None, None, None, None)])
        result = PostgresPlayerContextResolver(
            lambda: FakeConnection(cursor)
        ).resolve(uuid4(), 712)
        self.assertIsNone(result.profile.career_id)
        self.assertEqual(result.profile.career_stage, "not_started")

    def test_mismatch_missing_or_duplicate_binding_fails_closed(self):
        resolver = PostgresPlayerContextResolver(
            lambda: FakeConnection(FakeCursor([
                (uuid4(), 713, 713, "Wrong Person", None, None, None, None)
            ]))
        )
        with self.assertRaises(PlayerContextError):
            resolver.resolve(uuid4(), 712)

        for rows in ([], [
            (uuid4(), 712, 712, "One", None, None, None, None),
            (uuid4(), 712, 712, "Two", None, None, None, None),
        ]):
            resolver = PostgresPlayerContextResolver(
                lambda rows=rows: FakeConnection(FakeCursor(rows))
            )
            with self.assertRaises(PlayerContextError):
                resolver.resolve(uuid4(), 712)

    def test_principal_person_link_must_match_binding(self):
        cursor = FakeCursor([(uuid4(), 712, 713, "Mismatch", None, None, None, None)])
        with self.assertRaises(PlayerContextError):
            PostgresPlayerContextResolver(
                lambda: FakeConnection(cursor)
            ).resolve(uuid4(), 712)

    def test_ended_career_projects_former_status(self):
        cursor = FakeCursor([(
            uuid4(), 712, 712, "Former Player", uuid4(),
            "recruit", "ended", "separated",
        )])
        result = PostgresPlayerContextResolver(
            lambda: FakeConnection(cursor)
        ).resolve(uuid4(), 712)
        self.assertEqual(result.profile.career_stage, "former")


class PlayerCommandRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.session = make_session()
        self.verifier = FakeVerifier(self.session)
        self.cursor = FakeCursor([(
            uuid4(), 712, 712, "Authoritative Name", None, None, None, None,
        )])
        self.connect = lambda: FakeConnection(self.cursor)
        self.authorization = AuthorizationService(
            self.verifier, InMemoryAuditSink(), ()
        )

    def test_runtime_builds_profile_from_database_and_uses_gateway(self):
        gateway = Mock()
        gateway.execute.return_value = CommandResult(True, "profile")
        with patch(
            "runtime.player_command_runtime.create_postgres_player_application",
            return_value=object(),
        ) as create_app, patch(
            "runtime.player_command_runtime.bind_authorized_player_commands",
            return_value=gateway,
        ) as bind_gateway:
            runtime = PostgresPlayerCommandRuntime(
                self.connect, self.verifier, self.authorization
            )
            result = runtime.execute("opaque-credential", "profile")

        self.assertTrue(result.ok)
        profile = create_app.call_args.args[1]
        self.assertEqual(profile.display_name, "Authoritative Name")
        self.assertEqual(profile.officer_person_id, 712)
        bind_gateway.assert_called_once()
        self.assertEqual(
            bind_gateway.call_args.args[2], self.session.principal_id
        )
        gateway.execute.assert_called_once_with("opaque-credential", "profile")

    def test_revoked_session_is_still_sent_to_gateway_for_audited_denial(self):
        self.verifier.session = make_session(status=SessionStatus.REVOKED)
        gateway = Mock()
        gateway.execute.return_value = CommandResult(False, "Access denied.")
        with patch(
            "runtime.player_command_runtime.create_postgres_player_application",
            return_value=object(),
        ), patch(
            "runtime.player_command_runtime.bind_authorized_player_commands",
            return_value=gateway,
        ):
            runtime = PostgresPlayerCommandRuntime(
                self.connect, self.verifier, self.authorization
            )
            result = runtime.execute("revoked-credential", "profile")
        self.assertFalse(result.ok)
        gateway.execute.assert_called_once_with("revoked-credential", "profile")

    def test_non_player_principal_never_reaches_command_gateway(self):
        self.verifier.session = make_session(kind=PrincipalKind.OFFICER)
        with patch(
            "runtime.player_command_runtime.create_postgres_player_application"
        ) as create_app:
            runtime = PostgresPlayerCommandRuntime(
                self.connect, self.verifier, self.authorization
            )
            result = runtime.execute("officer-credential", "profile")
        self.assertFalse(result.ok)
        create_app.assert_not_called()

    def test_caller_cannot_supply_or_override_identity_context(self):
        runtime = PostgresPlayerCommandRuntime(
            self.connect, self.verifier, self.authorization
        )
        with self.assertRaises(TypeError):
            runtime.execute(
                "credential", "profile",
                principal_id=uuid4(), player_id=uuid4(), person_id=999,
            )

    def test_missing_session_or_person_link_fails_closed(self):
        self.verifier.session = None
        runtime = PostgresPlayerCommandRuntime(
            self.connect, self.verifier, self.authorization
        )
        self.assertFalse(runtime.execute("unknown", "profile").ok)

        self.verifier.session = make_session()
        self.verifier.session = replace(
            self.verifier.session, active_person_id=None
        )
        self.assertFalse(runtime.execute("no-person", "profile").ok)


if __name__ == "__main__":
    unittest.main()
