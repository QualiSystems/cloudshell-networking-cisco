from unittest import TestCase

from mock import MagicMock
from cloudshell.networking.cisco.flows.cisco_enable_snmp_flow import CiscoEnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters, SNMPV2ReadParameters, SNMPV3Parameters


class TestCiscoEnableSNMPFlow(TestCase):
    IP = "localhost"
    SNMP_WRITE_COMMUNITY = "private"
    SNMP_READ_COMMUNITY = "public"
    SNMP_USER = "admin"
    SNMP_PASSWORD = "P@ssw0rD"
    SNMP_PRIVATE_KEY = "PrivKey"

    def _get_handler(self, output):
        cli = MagicMock()
        self.session = MagicMock()
        self.session.send_command.return_value = output
        self.snmp_v2_write_parameters = SNMPV2WriteParameters(ip=self.IP,
                                                              snmp_write_community=self.SNMP_WRITE_COMMUNITY)
        self.snmp_v2_read_parameters = SNMPV2ReadParameters(ip=self.IP, snmp_read_community=self.SNMP_READ_COMMUNITY)
        self.snmp_v3_parameters = SNMPV3Parameters(ip=self.IP, snmp_user=self.SNMP_USER,
                                                   snmp_password=self.SNMP_PASSWORD,
                                                   snmp_private_key=self.SNMP_PRIVATE_KEY)
        cliservice = MagicMock()
        cliservice.__enter__.return_value = self.session
        cli.get_cli_service.return_value = cliservice
        logger = MagicMock()
        return CiscoEnableSnmpFlow(cli_handler=cli, logger=logger)

    def test_enable_snmp_read_v2(self):
        enable_flow = self._get_handler("""N5K-L3-Sw1#""")

        enable_flow.execute_flow(self.snmp_v2_read_parameters)
        self.session.send_command.assert_called_once()

    def test_enable_snmp_write_v2(self):
        enable_flow = self._get_handler("""N5K-L3-Sw1#""")

        enable_flow.execute_flow(self.snmp_v2_write_parameters)
        self.session.send_command.assert_called_once()

    def test_enable_snmp_v3(self):
        enable_flow = self._get_handler("""N5K-L3-Sw1#""")

        self.assertRaises(Exception, enable_flow.execute_flow, self.snmp_v3_parameters)
