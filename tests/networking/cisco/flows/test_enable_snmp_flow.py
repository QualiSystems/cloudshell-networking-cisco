from unittest import TestCase

from cloudshell.snmp.snmp_parameters import (
    SNMPReadParameters,
    SNMPV3Parameters,
    SNMPWriteParameters,
)

from cloudshell.networking.cisco.flows.cisco_enable_snmp_flow import CiscoEnableSnmpFlow

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoEnableSNMPFlow(TestCase):
    IP = "localhost"
    SNMP_WRITE_COMMUNITY = "private"
    SNMP_READ_COMMUNITY = "public"
    SNMP_USER = "admin"
    SNMP_PASSWORD = "P@ssw0rD"
    SNMP_PRIVATE_KEY = "PrivKey"

    def _get_handler(self, create_group=True):
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
        return CiscoEnableSnmpFlow(cli_handler=cli, logger=logger)

    @patch(
        "cloudshell.networking.cisco.flows.cisco_enable_snmp_flow"
        ".EnableDisableSnmpActions"
    )
    def test_enable_snmp_v3(self, enable_actions_mock):
        enable_snmp_mock = MagicMock()
        enable_snmp_group_mock = MagicMock()
        enable_snmp_view_mock = MagicMock()
        enable_actions_mock.return_value.get_current_snmp_user.side_effect = [
            "",
            self.SNMP_USER,
        ]
        enable_actions_mock.return_value.enable_snmp_v3 = enable_snmp_mock
        enable_actions_mock.return_value.get_current_snmp_config.return_value = ""
        enable_actions_mock.return_value.enable_snmp_group = enable_snmp_group_mock
        enable_actions_mock.return_value.enable_snmp_view = enable_snmp_view_mock

        enable_flow = self._get_handler()

        enable_flow.enable_flow(self.snmp_v3_parameters)

        enable_snmp_view_mock.assert_called_once_with(
            snmp_view=CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW
        )
        enable_snmp_group_mock.assert_called_once_with(
            snmp_group=CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP,
            snmp_view=CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW,
        )
        enable_snmp_mock.assert_called_once_with(
            snmp_user=self.snmp_v3_parameters.snmp_user,
            snmp_password=self.snmp_v3_parameters.snmp_password,
            auth_protocol=self.snmp_v3_parameters.snmp_auth_protocol.lower(),
            priv_protocol=self.snmp_v3_parameters.snmp_private_key_protocol.lower(),
            snmp_priv_key=self.snmp_v3_parameters.snmp_private_key,
            snmp_group=CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP,
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_enable_snmp_flow"
        ".EnableDisableSnmpActions"
    )
    def test_enable_snmp_v3_no_group(self, enable_actions_mock):
        enable_snmp_mock = MagicMock()
        enable_snmp_group_mock = MagicMock()
        enable_snmp_view_mock = MagicMock()
        enable_actions_mock.return_value.get_current_snmp_user.side_effect = [
            "",
            self.SNMP_USER,
        ]
        enable_actions_mock.return_value.enable_snmp_v3 = enable_snmp_mock
        enable_actions_mock.return_value.enable_snmp_group = enable_snmp_group_mock
        enable_actions_mock.return_value.enable_snmp_view = enable_snmp_view_mock

        enable_flow = self._get_handler(create_group=False)
        self.snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key=self.SNMP_PRIVATE_KEY,
            private_key_protocol="DES",
        )

        with self.assertRaisesRegexp(Exception, "DES"):
            enable_flow.enable_flow(self.snmp_v3_parameters)

        enable_snmp_view_mock.assert_not_called()
        enable_snmp_group_mock.assert_not_called()
        enable_snmp_mock.assert_not_called()

    @patch(
        "cloudshell.networking.cisco.flows.cisco_enable_snmp_flow"
        ".EnableDisableSnmpActions"
    )
    def test_enable_snmp_v2_read(self, enable_actions_mock):
        enable_flow = self._get_handler()
        enable_snmp_mock = MagicMock()
        is_read_only = True
        enable_actions_mock.return_value.get_current_snmp_config.side_effect = [
            "",
            "snmp-server community {}".format(
                self.snmp_v2_read_parameters.snmp_community
            ),
        ]
        enable_snmp_mock.return_value.enable_snmp.return_value = enable_snmp_mock
        enable_actions_mock.return_value.enable_snmp = enable_snmp_mock

        enable_flow.enable_flow(self.snmp_v2_read_parameters)

        enable_snmp_mock.assert_called_once_with(
            self.snmp_v2_read_parameters.snmp_community, is_read_only
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_enable_snmp_flow"
        ".EnableDisableSnmpActions"
    )
    def test_enable_snmp_v2_write(self, enable_actions_mock):
        enable_flow = self._get_handler()
        enable_snmp_mock = MagicMock()
        is_read_only = False
        enable_actions_mock.return_value.get_current_snmp_config.side_effect = [
            "",
            "snmp-server community {}".format(
                self.snmp_v2_write_parameters.snmp_community
            ),
        ]
        enable_snmp_mock.return_value.enable_snmp.return_value = enable_snmp_mock
        enable_actions_mock.return_value.enable_snmp = enable_snmp_mock

        enable_flow.enable_flow(self.snmp_v2_write_parameters)

        enable_snmp_mock.assert_called_once_with(
            self.snmp_v2_write_parameters.snmp_community, is_read_only
        )

    def test_validate_snmp_v3_params_validates_user_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user="",
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key=self.SNMP_PRIVATE_KEY,
        )

        with self.assertRaisesRegexp(Exception, "SNMPv3 user is not defined"):
            enable_flow.enable_flow(snmp_v3_parameters)

    def test_validate_snmp_v3_params_validates_password_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password="",
            snmp_private_key=self.SNMP_PRIVATE_KEY,
            auth_protocol=SNMPV3Parameters.AUTH_MD5,
        )

        with self.assertRaisesRegexp(Exception, "SNMPv3 Password has to be specified"):
            enable_flow.enable_flow(snmp_v3_parameters)

    def test_validate_snmp_v3_params_validates_private_key_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key="",
            auth_protocol=SNMPV3Parameters.AUTH_MD5,
            private_key_protocol=SNMPV3Parameters.PRIV_DES,
        )

        with self.assertRaisesRegexp(
            Exception, "SNMPv3 Private key has to be specified"
        ):
            enable_flow.enable_flow(snmp_v3_parameters)
