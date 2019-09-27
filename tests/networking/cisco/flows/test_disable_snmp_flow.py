from unittest import TestCase

from cloudshell.snmp.snmp_parameters import (
    SNMPReadParameters,
    SNMPV3Parameters,
    SNMPWriteParameters,
)

from cloudshell.networking.cisco.flows.cisco_disable_snmp_flow import (
    CiscoDisableSnmpFlow,
)
from cloudshell.networking.cisco.flows.cisco_enable_snmp_flow import CiscoEnableSnmpFlow

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoDisableSNMPFlow(TestCase):
    IP = "localhost"
    SNMP_WRITE_COMMUNITY = "private"
    SNMP_READ_COMMUNITY = "public"
    SNMP_USER = "admin"
    SNMP_PASSWORD = "P@ssw0rD"
    SNMP_PRIVATE_KEY = "PrivKey"

    def _get_handler(self, remove_group=True):
        self.snmp_v2_write_parameters = SNMPWriteParameters(
            ip=self.IP, snmp_community=self.SNMP_WRITE_COMMUNITY
        )
        self.snmp_v2_read_parameters = SNMPReadParameters(
            ip=self.IP, snmp_community=self.SNMP_READ_COMMUNITY
        )
        self.snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key=self.SNMP_PRIVATE_KEY,
        )
        cli = MagicMock()
        logger = MagicMock()
        return CiscoDisableSnmpFlow(cli_handler=cli, logger=logger)

    @patch(
        "cloudshell.networking.cisco.flows.cisco_disable_snmp_flow"
        ".EnableDisableSnmpActions"
    )
    def test_disable_snmp_v3_no_group(self, disable_actions_mock):
        disable_actions_mock.return_value.get_current_snmp_user.side_effect = [
            self.SNMP_USER,
            "",
        ]

        disable_flow = self._get_handler(remove_group=False)
        self.snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key=self.SNMP_PRIVATE_KEY,
            private_key_protocol="DES",
        )
        disable_flow.disable_flow(self.snmp_v3_parameters)
        disable_actions_mock.return_value.get_current_snmp_user.assert_called()
        disable_actions_mock.return_value.remove_snmp_user.assert_called_once_with(
            self.snmp_v3_parameters.snmp_user, CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_disable_snmp_flow"
        ".EnableDisableSnmpActions"
    )
    def test_disable_snmp_v3_with_group(self, disable_actions_mock):
        disable_actions_mock.return_value.get_current_snmp_user.side_effect = [
            self.SNMP_USER,
            "",
        ]
        (
            disable_actions_mock.return_value.get_current_snmp_config.return_value
        ) = "snmp-server view {}".format(CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW)

        disable_flow = self._get_handler()
        self.snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key=self.SNMP_PRIVATE_KEY,
            private_key_protocol="DES",
        )
        disable_flow.disable_flow(self.snmp_v3_parameters)
        disable_actions_mock.return_value.get_current_snmp_user.assert_called()
        disable_actions_mock.return_value.remove_snmp_user.assert_called_once_with(
            self.snmp_v3_parameters.snmp_user, CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP
        )
        disable_actions_mock.return_value.get_current_snmp_config.assert_called_once()
        disable_actions_mock.return_value.remove_snmp_group.assert_called_once_with(
            CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP
        )
        disable_actions_mock.return_value.remove_snmp_view.assert_called_once_with(
            CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_disable_snmp_flow"
        ".EnableDisableSnmpActions"
    )
    def test_disable_snmp_v2_read(self, disable_actions_mock):
        disable_actions_mock.return_value.get_current_snmp_config.return_value = ""

        disable_flow = self._get_handler()

        disable_flow.disable_flow(self.snmp_v2_read_parameters)
        disable_actions_mock.return_value.get_current_snmp_config.assert_called_once()
        disable_actions_mock.return_value.disable_snmp.assert_called_once_with(
            self.snmp_v2_read_parameters.snmp_community
        )
