from unittest import TestCase

from cloudshell.networking.cisco.flows.cisco_configuration_flow import (
    CiscoConfigurationFlow,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoSaveConfigurationFlow(TestCase):
    PATH = "ftp://admin:password@10.10.10.10/CloudShell/config"

    def setUp(self):
        cli = MagicMock()
        logger = MagicMock()
        self.handler = CiscoConfigurationFlow(cli, MagicMock(), logger)

    @patch("cloudshell.networking.cisco.flows.cisco_configuration_flow.SystemActions")
    def test_restore_append_startup(self, sys_actions_mock):
        copy_mock = MagicMock()
        sys_actions_mock.return_value.copy = copy_mock
        configuration_type = "startup"
        restore_method = "append"
        vrf_management_name = MagicMock()
        self.handler._restore_flow(
            self.PATH, configuration_type, restore_method, vrf_management_name
        )
        copy_mock.assert_called_once()

    @patch("cloudshell.networking.cisco.flows.cisco_configuration_flow.SystemActions")
    def test_restore_append_running(self, sys_actions_mock):
        copy_mock = MagicMock()
        sys_actions_mock.return_value.copy = copy_mock
        configuration_type = "running"
        restore_method = "append"
        vrf_management_name = MagicMock()
        self.handler._restore_flow(
            self.PATH, configuration_type, restore_method, vrf_management_name
        )
        copy_mock.assert_called_once()

    @patch("cloudshell.networking.cisco.flows.cisco_configuration_flow.SystemActions")
    def test_restore_override_startup(self, sys_actions_mock):
        delete_mock = MagicMock()
        copy_mock = MagicMock()
        sys_actions_mock.return_value.delete_file = delete_mock
        sys_actions_mock.return_value.copy = copy_mock
        configuration_type = "startup"
        restore_method = "override"
        vrf_management_name = MagicMock()
        self.handler._restore_flow(
            self.PATH, configuration_type, restore_method, vrf_management_name
        )
        delete_mock.assert_called_once()
        copy_mock.assert_called_once()

    @patch("cloudshell.networking.cisco.flows.cisco_configuration_flow.SystemActions")
    def test_restore_override_running(self, sys_actions_mock):
        override_running_mock = MagicMock()
        sys_actions_mock.return_value.override_running = override_running_mock
        configuration_type = "running"
        restore_method = "override"
        vrf_management_name = MagicMock()
        self.handler._restore_flow(
            self.PATH, configuration_type, restore_method, vrf_management_name
        )
        override_running_mock.assert_called_once()
