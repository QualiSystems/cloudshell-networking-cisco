from functools import lru_cache

from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.networking.cisco.autoload.snmp_tables.cisco_snmp_port_table import (
    CiscoSnmpPortsTable,
)
from cloudshell.networking.cisco.autoload.table_services.cisco_ports_table import (
    CiscoPortsTable,
)
from cloudshell.networking.cisco.autoload.table_services.cisco_sys_info_table import (
    CiscoSnmpSystemInfo,
)


class CiscoGenericSNMPAutoload(GenericSNMPAutoload):
    @property
    @lru_cache()
    def system_info_service(self) -> CiscoSnmpSystemInfo:
        """Get system info service."""
        return CiscoSnmpSystemInfo(self.snmp_handler, self.logger)

    @property
    @lru_cache()
    def port_snmp_table(self) -> CiscoSnmpPortsTable:
        """Get port snmp table."""
        return CiscoSnmpPortsTable(snmp_handler=self.snmp_handler, logger=self.logger)

    @property
    def port_table_service(self) -> CiscoPortsTable:
        """Get port table service."""
        if not self._port_table_service:
            self._port_table_service = CiscoPortsTable(
                resource_model=self._resource_model,
                ports_snmp_table=self.port_snmp_table,
                logger=self.logger,
            )
        return self._port_table_service
