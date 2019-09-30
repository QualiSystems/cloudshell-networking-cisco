from unittest import TestCase

from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import (
    CiscoGenericSNMPAutoload,
)
from cloudshell.networking.cisco.autoload.cisco_if_table import CiscoIfTable
from cloudshell.networking.cisco.autoload.cisco_snmp_if_port import CiscoSnmpIfPort
from cloudshell.networking.cisco.autoload.cisco_snmp_if_port_channel import (
    CiscoIfPortChannel,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoGenericSNMPAutoload(TestCase):
    @patch(
        "cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload.CiscoIfTable"
    )
    def test_if_table(self, if_table_mock):
        if_table_inst = MagicMock()
        if_table_mock.return_value = if_table_inst
        snmp_handler = MagicMock()
        logger = MagicMock()
        autoload = CiscoGenericSNMPAutoload(snmp_handler, logger)

        self.assertEqual(autoload.if_table_service, if_table_inst)
        _ = autoload.if_table_service
        if_table_mock.assert_called_once_with(snmp_handler=snmp_handler, logger=logger)


class TestCiscoIfTable(TestCase):
    def test_if_table(self):
        self.assertEqual(CiscoIfTable.IF_PORT, CiscoSnmpIfPort)
        self.assertEqual(CiscoIfTable.IF_PORT_CHANNEL, CiscoIfPortChannel)
