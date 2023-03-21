from logging import Logger

from cloudshell.snmp.autoload.services.port_table import PortsTable

from cloudshell.networking.cisco.autoload.cisco_snmp_if_port import CiscoSnmpIfPort
from cloudshell.networking.cisco.autoload.snmp_tables.cisco_snmp_port_table import (
    CiscoSnmpPortsTable,
)


class CiscoPortsTable(PortsTable):
    def __init__(
        self, resource_model, ports_snmp_table: CiscoSnmpPortsTable, logger: Logger
    ):
        super().__init__(resource_model, ports_snmp_table, logger)
        self._if_entity = CiscoSnmpIfPort
