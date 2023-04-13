from logging import Logger

from cloudshell.snmp.autoload.snmp.tables.port_attrs_snmp_tables.snmp_ports_auto_negotioation import (  # noqa: E501
    PortAutoNegotiation,
)
from cloudshell.snmp.core.snmp_service import SnmpService

from cloudshell.networking.cisco.autoload.snmp_tables.cisco_duplex_table import (
    CiscoSnmpStackTable,
)


class CiscoPortAutoNegotiation(PortAutoNegotiation):
    def __init__(
        self,
        snmp_service: SnmpService,
        snmp_duplex: CiscoSnmpStackTable,
        logger: Logger,
    ):
        super().__init__(snmp_service, logger)
        self._snmp_duplex = snmp_duplex

    def get_value_by_index(self, index):
        response = super().get_value_by_index(index)
        auto_neg_data = self._snmp_duplex.get(index)
        if auto_neg_data in ["auto", "disagree"]:
            response = "True"
        return response
