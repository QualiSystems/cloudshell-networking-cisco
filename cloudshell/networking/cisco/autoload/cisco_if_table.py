from cloudshell.snmp.autoload.snmp_if_table import SnmpIfTable

from cloudshell.networking.cisco.autoload.cisco_snmp_if_port import CiscoSnmpIfPort
from cloudshell.networking.cisco.autoload.cisco_snmp_if_port_channel import (
    CiscoIfPortChannel,
)


class CiscoIfTable(SnmpIfTable):
    IF_PORT = CiscoSnmpIfPort
    IF_PORT_CHANNEL = CiscoIfPortChannel
