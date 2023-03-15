from functools import lru_cache
from logging import Logger

from cloudshell.networking.cisco.autoload.constants.snmp_constants import (
    CISCO_CDP_DEVICE_ID,
    CISCO_CDP_DEVICE_PORT,
)
from cloudshell.snmp.core.snmp_service import SnmpService

from cloudshell.snmp.autoload.snmp.tables.port_attrs_snmp_tables.snmp_ports_neighbors_table import (  # noqa: E501
    PortNeighbours,
)


class CiscoPortNeighbours(PortNeighbours):
    def __init__(self, snmp_service: SnmpService, logger: Logger):
        super().__init__(snmp_service, logger)
        self._cisco_cdp_table = {}

    @property
    @lru_cache()
    def load_cisco_cdp_table(self):
        self._cisco_cdp_table = self._snmp.get_multiple_columns(
            [CISCO_CDP_DEVICE_ID, CISCO_CDP_DEVICE_PORT]
        )
        return self._cisco_cdp_table

    def set_port_attributes(self, port_object, port):
        port_object.adjacent = self._get_adjacent(
            port.if_index
        ) or super().get_adjacent_by_port(port=port, port_object=port_object)

    def _get_adjacent(self, if_index):
        """Get connected device interface and device name to the specified port id.

        Using cdp or lldp protocols
        :return: device's name and port connected to port id
        :rtype string
        """
        key = next(
            (k for k in self.load_cisco_cdp_table if k.startswith(f"{if_index}.")), None
        )
        if key:
            remote_host = self.load_cisco_cdp_table.get(key).get(
                CISCO_CDP_DEVICE_ID.object_name
            )
            remote_port = self.load_cisco_cdp_table.get(key).get(
                CISCO_CDP_DEVICE_PORT.object_name
            )
            if remote_host and remote_port:
                result = self.ADJACENT_TEMPLATE.format(
                    remote_host=remote_host, remote_port=remote_port
                )
                return result
