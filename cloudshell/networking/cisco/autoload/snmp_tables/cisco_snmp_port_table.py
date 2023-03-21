from cloudshell.snmp.autoload.snmp.tables.snmp_ports_table import SnmpPortsTable

from cloudshell.networking.cisco.autoload.snmp_tables.cisco_duplex_table import (
    CiscoSnmpStackTable,
)
from cloudshell.networking.cisco.autoload.snmp_tables.cisco_ports_auto_neg import (
    CiscoPortAutoNegotiation,
)
from cloudshell.networking.cisco.autoload.snmp_tables.cisco_ports_duplex import (
    CiscoPortDuplex,
)
from cloudshell.networking.cisco.autoload.snmp_tables.cisco_ports_neighbours import (
    CiscoPortNeighbours,
)


class CiscoSnmpPortsTable(SnmpPortsTable):
    def __init__(self, snmp_handler, logger):
        super().__init__(snmp_handler, logger)
        self._snmp_duplex = CiscoSnmpStackTable(snmp_handler, logger)
        self._port_auto_neg = CiscoPortAutoNegotiation(
            snmp_handler, self._snmp_duplex, logger
        )
        self._port_duplex = CiscoPortDuplex(snmp_handler, self._snmp_duplex, logger)
        self._port_neighbors = CiscoPortNeighbours(snmp_handler, logger)
