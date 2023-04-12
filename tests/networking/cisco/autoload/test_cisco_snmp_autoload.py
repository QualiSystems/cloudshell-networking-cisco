from unittest import TestCase

from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import (
    CiscoGenericSNMPAutoload,
)
from cloudshell.networking.cisco.autoload.snmp_tables.cisco_ports_duplex import (
    CiscoPortDuplex,
)
from cloudshell.networking.cisco.autoload.snmp_tables.cisco_ports_neighbours import (
    CiscoPortNeighbours,
)
from cloudshell.networking.cisco.autoload.snmp_tables.cisco_snmp_port_table import (
    CiscoSnmpPortsTable,
)

from unittest.mock import MagicMock, patch


class TestCiscoGenericSNMPAutoload(TestCase):
    @patch(
        "cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload.CiscoSnmpPortsTable"
    )
    def test_if_table(self, if_table_mock):
        if_table_inst = MagicMock()
        if_table_mock.return_value = if_table_inst
        snmp_handler = MagicMock()
        logger = MagicMock()
        autoload = CiscoGenericSNMPAutoload(
            snmp_handler, logger, resource_model=MagicMock()
        )

        self.assertEqual(autoload.port_snmp_table, if_table_inst)
        _ = autoload.port_snmp_table
        if_table_mock.assert_called_once_with(snmp_handler=snmp_handler, logger=logger)


class TestCiscoIfTable(TestCase):
    def test_if_table(self):
        ports_table = CiscoSnmpPortsTable(MagicMock(), MagicMock())
        self.assertTrue(isinstance(ports_table._port_duplex, CiscoPortDuplex))
        self.assertTrue(isinstance(ports_table._port_neighbors, CiscoPortNeighbours))
