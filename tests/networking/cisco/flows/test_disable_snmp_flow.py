from unittest import TestCase

from mock import MagicMock
from cloudshell.networking.cisco.flows.cisco_disable_snmp_flow import CiscoDisableSnmpFlow


class TestCiscoDisableSNMPFlow(TestCase):
    def _get_handler(self, output):
        cli = MagicMock()
        self.session = MagicMock()
        self.session.send_command.return_value = output
        cliservice = MagicMock()
        cliservice.__enter__.return_value = self.session
        cli.get_cli_service.return_value = cliservice
        logger = MagicMock()
        return CiscoDisableSnmpFlow(cli_handler=cli, logger=logger)