from unittest import TestCase

from cloudshell.cli.service.cli import CLI

from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.cli.cisco_command_modes import (
    ConfigCommandMode,
    DefaultCommandMode,
    EnableCommandMode,
)

try:
    from mock import MagicMock, Mock, patch
except ImportError:
    from unittest.mock import MagicMock, Mock, patch


class TestCiscoSystemActions(TestCase):
    def set_up(self):
        ConfigCommandMode.ENTER_CONFIG_RETRY_TIMEOUT = 0.5
        cli_conf = MagicMock()
        cli_conf.cli_tcp_port = "22"
        cli_conf.cli_connection_type = "SSH"
        return CiscoCliHandler(CLI(), cli_conf, Mock())

    def test_default_mode(self):
        cli_handler = self.set_up()
        self.assertIsInstance(cli_handler.default_mode, DefaultCommandMode)

    def test_enable_mode(self):
        cli_handler = self.set_up()
        self.assertIsInstance(cli_handler.enable_mode, EnableCommandMode)

    def test_config_mode(self):
        cli_handler = self.set_up()
        self.assertIsInstance(cli_handler.config_mode, ConfigCommandMode)

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_with_lock(self, recv_mock, cb_mock, paramiko_mock):
        recv_mock.side_effect = [
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#configuration Locked",
            "Boogie(config)#",
            "Boogie(config)#",
            "Boogie(config)#",
            "Boogie(config)#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
        ]
        cli_handler = self.set_up()
        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_with_multiple_retries(
        self, recv_mock, cb_mock, paramiko_mock
    ):
        locked_message = """Boogie#
        configuration Locked
        Boogie#"""
        recv_mock.side_effect = [
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            "Boogie(config)#",
            "Boogie(config)#",
            "Boogie(config)#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
        ]
        cli_handler = self.set_up()
        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_regular(self, recv_mock, cb_mock, paramiko_mock):
        recv_mock.side_effect = [
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie(config)#",
            "Boogie(config)#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
        ]
        cli_handler = self.set_up()
        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_fail(self, recv_mock, cb_mock, paramiko_mock):
        error_message = (
            "Failed to create new session for type SSH, see logs for details"
        )
        locked_message = """Boogie#
        configuration Locked
        Boogie#"""
        recv_mock.side_effect = [
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie#",
            "Boogie(config)#",
            "Boogie#",
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
        ]
        cli_handler = self.set_up()

        try:
            with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
                session.send_command("")
        except Exception as e:
            self.assertTrue(error_message in e.args)
