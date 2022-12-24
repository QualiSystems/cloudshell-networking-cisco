import re

from cloudshell.snmp.autoload.snmp.helper.snmp_if_entity import SnmpIfEntity


class CiscoSnmpIfPort(SnmpIfEntity):
    PORT_NAME_MATCH = re.compile(
        r"^(GigabitEthernet|FastEthernet|FortyGig|"
        r"TenGig|Hundred|Ethernet|Port-channel)",
        re.IGNORECASE,
    )

    @property
    def port_name(self):
        name = self.if_descr_name
        if not self.PORT_NAME_MATCH.search(name):
            name = self.if_name
        return name
