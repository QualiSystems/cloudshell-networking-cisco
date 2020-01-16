from cloudshell.snmp.autoload.core.snmp_oid_template import SnmpMibOidTemplate
from cloudshell.snmp.autoload.domain.if_entity.snmp_if_port_entity import SnmpIfPort


class CiscoSnmpIfPort(SnmpIfPort):
    CISCO_CDP_MIB = SnmpMibOidTemplate("CISCO-CDP-MIB", "cdpCacheDeviceId")

    def __init__(
        self, snmp_handler, logger, port_name_response, port_attributes_snmp_tables
    ):
        super(CiscoSnmpIfPort, self).__init__(
            snmp_handler, logger, port_name_response, port_attributes_snmp_tables
        )
        self._cisco_duplex = None

    @property
    def port_name(self):
        return self.if_descr_name

    def _get_adjacent(self):
        """Get connected device interface and device name to the specified port id.

        Using cdp or lldp protocols
        :return: device's name and port connected to port id
        :rtype string
        """
        result_template = "{remote_host} through {remote_port}"
        result = ""
        for key, value in self._port_attributes_snmp_tables.cdp_table.items():
            if str(key).startswith(str(self.if_index)):
                port = self._snmp.get_property(self.CISCO_CDP_MIB.get_snmp_mib_oid(key))
                result = result_template.format(
                    remote_host=value.get("cdpCacheDeviceId", ""), remote_port=port
                )
                break
        if result == "":
            result = super(CiscoSnmpIfPort, self)._get_adjacent()
        return result

    def _get_auto_neg(self):
        """Get port auto negotiation status.

        :return return "True"
        """
        cisco_duplex = self._get_cisco_duplex()
        if cisco_duplex:
            if cisco_duplex in ["auto", "disagree"]:
                return "True"
        else:
            return super(CiscoSnmpIfPort, self)._get_auto_neg()

    def _get_cisco_duplex(self):
        if not self._cisco_duplex:
            state_table = self._port_attributes_snmp_tables.cisco_duplex_state_table
            cisco_duplex_id = state_table.get(str(self.if_index))
            if cisco_duplex_id:
                self._cisco_duplex = self._snmp.get_property(
                    "CISCO-STACK-MIB", "portDuplex", cisco_duplex_id
                ).replace("'", "")
        return self._cisco_duplex

    def _get_duplex(self):
        """Get current duplex state.

        :return str "Full"
        """
        cisco_duplex = self._get_cisco_duplex()
        if cisco_duplex:
            if cisco_duplex in ["full", "half"]:
                return cisco_duplex.capitalize()
        else:
            return super(CiscoSnmpIfPort, self)._get_duplex()
