"""Composition and session-bound command gateway tests."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from runtime.application import (
    PostgresPlayerApplication,
    bind_authorized_player_commands,
    create_postgres_player_application,
)
from runtime.player_interface import CommandResult, PlayerProfile
from runtime.security import AuthorizationService


class PostgresPlayerApplicationTests(unittest.TestCase):
    def test_factory_wires_shared_connection_factory_and_domain_services(self):
        connect = lambda: None
        profile = PlayerProfile(
            "00000000-0000-4000-8000-000000000001",
            "Saltwater Player",
        )
        with patch("runtime.application.PostgresRuntimeStore") as store_type, patch(
            "runtime.application.PostgresRecruitmentService"
        ) as recruitment_type, patch(
            "runtime.application.RuntimeKernel"
        ) as kernel_type, patch(
            "runtime.application.PlayerCommandInterface"
        ) as commands_type, patch(
            "runtime.application.PostgresSessionLifecycle"
        ) as sessions_type:
            store = store_type.return_value
            kernel = kernel_type.return_value
            recruitment = recruitment_type.return_value
            sessions = sessions_type.return_value
            commands = commands_type.return_value
            result = create_postgres_player_application(connect, profile)

        self.assertIsInstance(result, PostgresPlayerApplication)
        store_type.assert_called_once_with(connect)
        kernel_type.assert_called_once_with(store)
        recruitment_type.assert_called_once_with(connect)
        sessions_type.assert_called_once_with(connect)
        commands_type.assert_called_once_with(kernel, profile, recruitment)
        self.assertIs(result.kernel, kernel)
        self.assertIs(result.recruitment, recruitment)
        self.assertIs(result.sessions, sessions)
        self.assertIs(result.commands, commands)

    def test_factory_rejects_untrusted_or_invalid_inputs_before_wiring(self):
        with self.assertRaises(TypeError):
            create_postgres_player_application(None, PlayerProfile("p", "Player"))
        with self.assertRaises(TypeError):
            create_postgres_player_application(lambda: None, object())

    def test_gateway_authorizes_and_audits_before_dispatch(self):
        principal_id = uuid4()
        commands = Mock()
        commands.profile = PlayerProfile(str(uuid4()), "Player")
        commands.execute.return_value = CommandResult(True, "status")
        authorization = Mock(spec=AuthorizationService)
        authorization.decide.return_value = SimpleNamespace(
            allowed=True, principal_id=principal_id
        )
        application = PostgresPlayerApplication(
            kernel=object(), recruitment=object(), sessions=object(), commands=commands
        )
        gateway = bind_authorized_player_commands(
            application, authorization, principal_id
        )

        result = gateway.execute("opaque-token", "status")

        self.assertTrue(result.ok)
        authorization.decide.assert_called_once_with(
            "opaque-token",
            action="player.command.status",
            resource=f"player:{commands.profile.player_id}",
            purpose="gameplay",
        )
        commands.execute.assert_called_once_with("status")

    def test_gateway_denies_invalid_session_or_wrong_principal_without_dispatch(self):
        principal_id = uuid4()
        commands = Mock()
        commands.profile = PlayerProfile(str(uuid4()), "Player")
        authorization = Mock(spec=AuthorizationService)
        authorization.decide.return_value = SimpleNamespace(
            allowed=True, principal_id=uuid4()
        )
        application = PostgresPlayerApplication(
            kernel=object(), recruitment=object(), commands=commands
        )
        gateway = bind_authorized_player_commands(
            application, authorization, principal_id
        )

        result = gateway.execute("other-player-token", "recruit")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "Access denied.")
        commands.execute.assert_not_called()

    def test_gateway_denies_unknown_commands_without_dispatch(self):
        commands = Mock()
        commands.profile = PlayerProfile(str(uuid4()), "Player")
        authorization = Mock(spec=AuthorizationService)
        application = PostgresPlayerApplication(
            kernel=object(), recruitment=object(), commands=commands
        )
        gateway = bind_authorized_player_commands(
            application, authorization, uuid4()
        )

        result = gateway.execute("token", "reveal-secret")

        self.assertFalse(result.ok)
        authorization.decide.assert_not_called()
        commands.execute.assert_not_called()

    def test_gateway_factory_rejects_untrusted_bindings(self):
        with self.assertRaises(TypeError):
            bind_authorized_player_commands(object(), Mock(), uuid4())


if __name__ == "__main__":
    unittest.main()
