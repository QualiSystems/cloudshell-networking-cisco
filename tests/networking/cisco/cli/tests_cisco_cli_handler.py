from unittest import TestCase

from cloudshell.cli.cli_service import CliService
from mock import create_autospec, MagicMock
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler


class TestCiscoSystemActions(TestCase):
    def set_up(self):
        cli_service = create_autospec(CliService)
        resource_config = MagicMock()
        api = MagicMock()
        api.DecryptPassword().Value.return_value = "password"
        return CiscoCliHandler(cli=cli_service, resource_config=resource_config, logger=MagicMock(), api=api)

    def test_enter_config_mode_with_lock(self):
        session = MagicMock()
        session.hardware_expect.side_effect = ["Boogie#configuration Locked", "Boogie(config)#", "Boogie(config)#", "Boogie(config)#",
                                            "Boogie(config)#", "Boogie(config)#"]
        cli = self.set_up()
        cli._enter_config_mode(session, cli._logger)

    def test_enter_config_mode_regular(self):
        session = MagicMock()
        session.hardware_expect.return_value = "Boogie(config)#"
        cli = self.set_up()
        cli._enter_config_mode(session, cli._logger)

    def test_enter_config_mode_fail(self):
        session = MagicMock()
        error_message = "Failed to enter config mode, please check logs, for details"
        session.hardware_expect.return_value = "Boogie#"
        cli = self.set_up()
        try:
            cli._enter_config_mode(session, cli._logger)
        except Exception as e:
            self.assertTrue(error_message in e.args)
