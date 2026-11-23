"""Composition tests for the trusted PostgreSQL player application."""
import unittest
from unittest.mock import patch

from runtime.application import (
    PostgresPlayerApplication,
    create_postgres_player_application,
)
from runtime.kernel import PostgresRuntimeStore, RuntimeKernel
from runtime.player_interface import PlayerCommandInterface, PlayerProfile
from runtime.recruitment import PostgresRecruitmentService


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
        ) as commands_type:
            store = store_type.return_value
            kernel = kernel_type.return_value
            recruitment = recruitment_type.return_value
            commands = commands_type.return_value

            result = create_postgres_player_application(connect, profile)

        self.assertIsInstance(result, PostgresPlayerApplication)
        store_type.assert_called_once_with(connect)
        kernel_type.assert_called_once_with(store)
        recruitment_type.assert_called_once_with(connect)
        commands_type.assert_called_once_with(kernel, profile, recruitment)
        self.assertIs(result.kernel, kernel)
        self.assertIs(result.recruitment, recruitment)
        self.assertIs(result.commands, commands)

    def test_factory_rejects_untrusted_or_invalid_inputs_before_wiring(self):
        with self.assertRaises(TypeError):
            create_postgres_player_application(None, PlayerProfile("p", "Player"))
        with self.assertRaises(TypeError):
            create_postgres_player_application(lambda: None, object())


if __name__ == "__main__":
    unittest.main()
