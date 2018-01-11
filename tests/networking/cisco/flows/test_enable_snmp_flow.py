from unittest import TestCase

from mock import MagicMock, patch
from cloudshell.networking.cisco.flows.cisco_enable_snmp_flow import CiscoEnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters, SNMPV2ReadParameters, SNMPV3Parameters


class TestCiscoEnableSNMPFlow(TestCase):
    IP = "localhost"
    SNMP_WRITE_COMMUNITY = "private"
    SNMP_READ_COMMUNITY = "public"
    SNMP_USER = "admin"
    SNMP_PASSWORD = "P@ssw0rD"
    SNMP_PRIVATE_KEY = "PrivKey"

    def _get_handler(self, create_group=True):
        self.snmp_v2_write_parameters = SNMPV2WriteParameters(ip=self.IP,
                                                              snmp_write_community=self.SNMP_WRITE_COMMUNITY)
        self.snmp_v2_read_parameters = SNMPV2ReadParameters(ip=self.IP, snmp_read_community=self.SNMP_READ_COMMUNITY)
        self.snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER,
                                                   snmp_password=self.SNMP_PASSWORD,
                                                   snmp_private_key=self.SNMP_PRIVATE_KEY)
        cli = MagicMock()
        logger = MagicMock()
        return CiscoEnableSnmpFlow(cli_handler=cli, logger=logger, create_group=create_group)

    @patch("cloudshell.networking.cisco.flows.cisco_enable_snmp_flow.EnableDisableSnmpActions")
    def test_enable_snmp_v3(self, enable_actions_mock):
        enable_snmp_mock = MagicMock()
        enable_snmp_group_mock = MagicMock()
        enable_snmp_view_mock = MagicMock()
        enable_actions_mock.return_value.get_current_snmp_user.side_effect = ["", self.SNMP_USER]
        enable_actions_mock.return_value.enable_snmp_v3 = enable_snmp_mock
        enable_actions_mock.return_value.get_current_snmp_config.return_value = ""
        enable_actions_mock.return_value.enable_snmp_group = enable_snmp_group_mock
        enable_actions_mock.return_value.enable_snmp_view = enable_snmp_view_mock

        enable_flow = self._get_handler()

        enable_flow.execute_flow(self.snmp_v3_parameters)

        enable_snmp_view_mock.assert_called_once_with(snmp_view=CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW)
        enable_snmp_group_mock.assert_called_once_with(snmp_group=CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP,
                                                       snmp_view=CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW)
        enable_snmp_mock.assert_called_once_with(snmp_user=self.snmp_v3_parameters.snmp_user,
                                                 snmp_password=self.snmp_v3_parameters.snmp_password,
                                                 auth_protocol=CiscoEnableSnmpFlow.SNMP_AUTH_MAP[
                                                     self.snmp_v3_parameters.auth_protocol].lower(),
                                                 priv_protocol=CiscoEnableSnmpFlow.SNMP_PRIV_MAP[
                                                     self.snmp_v3_parameters.private_key_protocol].lower(),
                                                 snmp_priv_key=self.snmp_v3_parameters.snmp_private_key,
                                                 snmp_group=CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP)

    @patch("cloudshell.networking.cisco.flows.cisco_enable_snmp_flow.EnableDisableSnmpActions")
    def test_enable_snmp_v3_no_group(self, enable_actions_mock):
        enable_snmp_mock = MagicMock()
        enable_snmp_group_mock = MagicMock()
        enable_snmp_view_mock = MagicMock()
        enable_actions_mock.return_value.get_current_snmp_user.side_effect = ["", self.SNMP_USER]
        enable_actions_mock.return_value.enable_snmp_v3 = enable_snmp_mock
        enable_actions_mock.return_value.enable_snmp_group = enable_snmp_group_mock
        enable_actions_mock.return_value.enable_snmp_view = enable_snmp_view_mock

        enable_flow = self._get_handler(create_group=False)
        self.snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER,
                                                   snmp_password=self.SNMP_PASSWORD,
                                                   snmp_private_key=self.SNMP_PRIVATE_KEY,
                                                   private_key_protocol="DES")
        enable_flow.execute_flow(self.snmp_v3_parameters)
        enable_snmp_view_mock.assert_not_called()
        enable_snmp_group_mock.assert_not_called()
        enable_snmp_mock.assert_called_once_with(snmp_user=self.snmp_v3_parameters.snmp_user,
                                                 snmp_password=self.snmp_v3_parameters.snmp_password,
                                                 auth_protocol=CiscoEnableSnmpFlow.SNMP_AUTH_MAP[
                                                     self.snmp_v3_parameters.auth_protocol].lower(),
                                                 priv_protocol="",
                                                 snmp_priv_key=self.snmp_v3_parameters.snmp_private_key,
                                                 snmp_group=None)

    @patch("cloudshell.networking.cisco.flows.cisco_enable_snmp_flow.EnableDisableSnmpActions")
    def test_enable_snmp_v2_read(self, enable_actions_mock):
        enable_flow = self._get_handler()
        enable_snmp_mock = MagicMock()
        is_read_only = True
        enable_actions_mock.return_value.get_current_snmp_config.side_effect = ["",
                                                                                "snmp-server community {}".format(
                                                                                    self.snmp_v2_read_parameters.snmp_community)]
        enable_snmp_mock.return_value.enable_snmp.return_value = enable_snmp_mock
        enable_actions_mock.return_value.enable_snmp = enable_snmp_mock

        enable_flow.execute_flow(self.snmp_v2_read_parameters)

        enable_snmp_mock.assert_called_once_with(self.snmp_v2_read_parameters.snmp_community, is_read_only)

    @patch("cloudshell.networking.cisco.flows.cisco_enable_snmp_flow.EnableDisableSnmpActions")
    def test_enable_snmp_v2_write(self, enable_actions_mock):
        enable_flow = self._get_handler()
        enable_snmp_mock = MagicMock()
        is_read_only = False
        enable_actions_mock.return_value.get_current_snmp_config.side_effect = ["",
                                                                                "snmp-server community {}".format(
                                                                                    self.snmp_v2_write_parameters.snmp_community)]
        enable_snmp_mock.return_value.enable_snmp.return_value = enable_snmp_mock
        enable_actions_mock.return_value.enable_snmp = enable_snmp_mock

        enable_flow.execute_flow(self.snmp_v2_write_parameters)

        enable_snmp_mock.assert_called_once_with(self.snmp_v2_write_parameters.snmp_community, is_read_only)

    def test_validate_snmp_v3_params_validates_user_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user="", snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY)
        try:
            enable_flow._validate_snmp_v3_params(snmp_v3_parameters)
        except Exception as e:
            self.assertIn("Failed to enable SNMP v3, 'SNMP V3 User' attribute cannot be empty", e.args)

    def test_validate_snmp_v3_params_validates_password_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER, snmp_password="",
                                              snmp_private_key=self.SNMP_PRIVATE_KEY)
        try:
            enable_flow._validate_snmp_v3_params(snmp_v3_parameters)
        except Exception as e:
            self.assertIn("Failed to enable SNMP v3, 'SNMP V3 Password' attribute cannot be empty", e.args)

    def test_validate_snmp_v3_params_validates_private_key_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER, snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key="")
        try:
            enable_flow._validate_snmp_v3_params(snmp_v3_parameters)
        except Exception as e:
            self.assertIn("Failed to enable SNMP v3, 'SNMP V3 Private Key' attribute cannot be empty", e.args)

    def test_validate_snmp_v3_params_validates_private_protocol_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER, snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY,
                                              private_key_protocol="No Privacy Protocol")
        try:
            enable_flow._validate_snmp_v3_params(snmp_v3_parameters)
        except Exception as e:
            self.assertIn("Failed to enable SNMP v3, 'SNMP V3 Privacy Protocol' attribute cannot be empty"
                          " or set to 'No Privacy Protocol'", e.args)

    def test_validate_snmp_v3_params_validates_auth_protocol_and_raise(self):
        enable_flow = CiscoEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER, snmp_password=self.SNMP_PASSWORD,
                                              snmp_private_key=self.SNMP_PRIVATE_KEY,
                                              auth_protocol="No Authentication Protocol")
        try:
            enable_flow._validate_snmp_v3_params(snmp_v3_parameters)
        except Exception as e:
            self.assertIn("Failed to enable SNMP v3, 'SNMP V3 Authentication Protocol' attribute cannot be empty"
                          " or set to 'No Authentication Protocol'", e.args)
