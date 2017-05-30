from unittest import TestCase
from cloudshell.cli.cli_service import CliService
from mock import MagicMock, create_autospec

from cloudshell.networking.cisco.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions


def return_cmd(cmd, **kwargs):
    return cmd


class TestCiscoSystemActions(TestCase):
    def set_up(self, response):
        cli_service = create_autospec(CliService)
        if callable(response):
            cli_service.send_command = response
        else:
            cli_service.send_command.return_value = response
        return EnableDisableSnmpActions(cli_service=cli_service,
                                        logger=MagicMock())

    def test_get_current_snmp_communities(self):
        # Setup
        expected_result = "snmp-server community public ro"
        enable_disable_actions = self.set_up(expected_result)

        # Act
        result = enable_disable_actions.get_current_snmp_communities()

        # Assert
        self.assertTrue(result == expected_result)

    def test_get_current_enable_snmp_read_only(self):
        # Setup
        community = "public"
        expected_result = "snmp-server community public ro"
        enable_disable_actions = self.set_up(return_cmd)

        # Act
        result = enable_disable_actions.enable_snmp(community)

        # Assert
        self.assertTrue(result)
        self.assertTrue(result == expected_result)

    def test_get_current_enable_snmp_read_write(self):
        # Setup
        community = "public"
        expected_result = "snmp-server community public rw"
        enable_disable_actions = self.set_up(return_cmd)

        # Act
        result = enable_disable_actions.enable_snmp(community, is_read_only_community=False)

        # Assert
        self.assertTrue(result)
        self.assertTrue(result == expected_result)

    def test_get_current_disable_snmp(self):
        # Setup
        community = "public"
        expected_result = "no snmp-server community public"
        enable_disable_actions = self.set_up(return_cmd)

        # Act
        result = enable_disable_actions.disable_snmp(community)

        # Assert
        self.assertTrue(result)
        self.assertTrue(result == expected_result)
