import re

from cloudshell.snmp.autoload.snmp.entities.snmp_if_entity import SnmpIfEntity


class CiscoSnmpIfPort(SnmpIfEntity):
    """Cisco SNMP If Port."""

    PORT_NAME_MATCH = re.compile(
        r"^\S*(Ethernet|GigE|Serial|Sonet|Port-channel|Bundle-Ether)",
        re.IGNORECASE,
    )

    @property
    def port_name(self):
        name = self.if_descr_name
        if not self.PORT_NAME_MATCH.search(name):
            name = self.if_name
        return name.replace("/", "-").replace(":", "_")
