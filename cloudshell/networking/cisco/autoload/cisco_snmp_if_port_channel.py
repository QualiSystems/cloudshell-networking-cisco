from cloudshell.snmp.autoload.domain.if_entity.snmp_if_port_channel_entity import (
    SnmpIfPortChannel,
)


class CiscoIfPortChannel(SnmpIfPortChannel):
    @property
    def port_name(self):
        return self.if_descr_name
