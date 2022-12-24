from logging import Logger

from cloudshell.networking.cisco.autoload.snmp_tables.cisco_duplex_table import (
    CiscoSnmpStackTable,
)
from cloudshell.snmp.core.snmp_service import SnmpService

from cloudshell.snmp.autoload.snmp.tables.port_attrs_snmp_tables.snmp_ports_duplex_table import (  # noqa: E501
    PortDuplex,
)


class CiscoPortDuplex(PortDuplex):
    def __init__(
        self,
        snmp_service: SnmpService,
        snmp_duplex: CiscoSnmpStackTable,
        logger: Logger,
    ):
        super().__init__(snmp_service, logger)
        self._snmp_duplex = snmp_duplex

    def get_duplex_by_port_index(self, index):
        response = super().get_duplex_by_port_index(index)
        duplex = self._snmp_duplex.get(index)
        if duplex in ["full", "half"]:
            response = duplex.capitalize()
        return response
