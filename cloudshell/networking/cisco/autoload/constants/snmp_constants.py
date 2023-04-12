from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject

CISCO_CDP_DEVICE_ID = SnmpMibObject("CISCO-CDP-MIB", "cdpCacheDeviceId")
CISCO_CDP_DEVICE_PORT = SnmpMibObject("CISCO-CDP-MIB", "cdpCacheDevicePort")
CISCO_STACK_DUPLEX = SnmpMibObject("CISCO-STACK-MIB", "portDuplex")
CISCO_STACK_DUPLEX_ID = SnmpMibObject("CISCO-STACK-MIB", "portIfIndex")
