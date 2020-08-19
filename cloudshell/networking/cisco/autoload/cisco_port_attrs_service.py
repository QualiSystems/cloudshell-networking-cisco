from cloudshell.snmp.autoload.domain.snmp_port_attr_tables import SnmpPortAttrTables
from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject


class CiscoSnmpPortAttrTables(SnmpPortAttrTables):
    def __init__(self, snmp_handler, logger):
        super(CiscoSnmpPortAttrTables, self).__init__(snmp_handler, logger)
        self._cisco_duplex_state_table = None
        self._cdp_table = None

    @property
    def cdp_table(self):
        if self._cdp_table is None:
            self._cdp_table = self._snmp.get_table(
                SnmpMibObject("CISCO-CDP-MIB", "cdpCacheDeviceId")
            )
            self._logger.info("cdpCacheDeviceId table loaded")
        return self._cdp_table

    @property
    def cisco_duplex_state_table(self):
        if self._cisco_duplex_state_table is None:
            self._cisco_duplex_state_table = {}
            cisco_duplex_state_table = self._snmp.get_table(
                SnmpMibObject("CISCO-STACK-MIB", "portIfIndex")
            )
            if cisco_duplex_state_table:
                self._cisco_duplex_state_table = {
                    v.get("portIfIndex", "").lower(): k
                    for k, v in cisco_duplex_state_table.items()
                }
            self._logger.info("Duplex portIfIndex table loaded")
        return self._cisco_duplex_state_table
