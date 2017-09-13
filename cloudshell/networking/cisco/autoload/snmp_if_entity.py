class SnmpIfEntity(object):
    IF_MIB = "IF-MIB"
    IF_TYPE = "ifType"
    IF_MTU = "ifMtu"
    IF_SPEED = "ifHighSpeed"
    IF_NAME = "ifDescr"
    IF_MAC = "ifPhysAddress"
    IF_ALIAS = "ifAlias"

    def __init__(self, snmp_handler, logger, index, port_attributes_snmp_tables):
        self.if_index = int(index)
        self._snmp = snmp_handler
        self._port_attributes_snmp_tables = port_attributes_snmp_tables
        self._logger = logger
        self._if_type = "other"
        self._if_speed = 0
        self._if_mtu = 0
        self._if_mac = ""
        self._ipv4 = ""
        self._ipv6 = ""
        self._if_alias = ""
        self._if_name = None
        self._adjacent = ""
        self._duplex = ""
        self._auto_neg = ""
        self._port_channel_associated_port = ""

    @property
    def if_name(self):
        if not self._if_name:
            self._if_name = self._snmp.get_property(self.IF_MIB, self.IF_NAME, self.if_index)
        return self._if_name

    @property
    def if_type(self):
        if not self._if_type:
            self._if_type = self._snmp.get_property(self.IF_MIB, self.IF_TYPE, self.if_index).replace('/', '').replace(
                "'", '')
        return self._if_type

    @property
    def if_port_description(self):
        if not self._if_alias:
            self._if_alias = self._snmp.get_property(self.IF_MIB, self.IF_ALIAS, self.if_index)
        return self._if_alias

    @property
    def if_speed(self):
        if not self._if_speed:
            self._if_speed = self._snmp.get_property(self.IF_MIB, self.IF_SPEED, self.if_index)
        return self._if_speed

    @property
    def if_mtu(self):
        if not self._if_mtu:
            self._if_mtu = self._snmp.get_property(self.IF_MIB, self.IF_MTU, self.if_index)
        return self._if_mtu

    @property
    def if_mac(self):
        if not self._if_mac:
            self._if_mac = self._snmp.get_property(self.IF_MIB, self.IF_MAC, self.if_index)
        return self._if_mac

    @property
    def ipv4_address(self):
        if not self._ipv4:
            self._ipv4 = self._get_ipv4()
        return self._ipv4

    @property
    def ipv6_address(self):
        if not self._ipv6:
            self._ipv6 = self._get_ipv6()
        return self._ipv6

    @property
    def adjacent(self):
        if not self._adjacent:
            self._adjacent = self._get_adjacent()
        return self._adjacent

    @property
    def duplex(self):
        if not self._duplex:
            self._duplex = self._get_duplex() or "Half"
        return self._duplex

    @property
    def auto_negotiation(self):
        if not self._auto_neg:
            self._auto_neg = self._get_auto_neg() or "False"
        return self._auto_neg

    @property
    def associated_port_list(self):
        if not self._port_channel_associated_port:
            self._port_channel_associated_port = self._get_associated_ports()
        return self._port_channel_associated_port

    def _get_associated_ports(self):
        """Get all ports associated with provided port channel
        :return:
        """

        result = []
        for key, value in self._port_attributes_snmp_tables.port_channel_ports.iteritems():
            if str(self.if_index) in value['dot3adAggPortAttachedAggID']:
                result.append(key)
        return result

    def _get_adjacent(self):
        """Get connected device interface and device name to the specified port id, using cdp or lldp protocols

        :param interface_id: port id
        :return: device's name and port connected to port id
        :rtype string
        """

        result_template = '{remote_host} through {remote_port}'
        result = ''
        for key, value in self._port_attributes_snmp_tables.cdp_table.iteritems():
            if str(key).startswith(str(self.if_index)):
                port = self._snmp.get_property('CISCO-CDP-MIB', 'cdpCacheDevicePort', key)
                result = result_template.format(remote_host=value.get('cdpCacheDeviceId', ''), remote_port=port)
                break
        if result == '' and self._port_attributes_snmp_tables.lldp_local_table:
            interface_name = self.if_name.lower()
            if interface_name:
                key = self._port_attributes_snmp_tables.lldp_local_table.get(interface_name, None)
                if key:
                    for port_id, rem_table in self._port_attributes_snmp_tables.lldp_remote_table.iteritems():
                        if ".{0}.".format(key) in port_id:
                            remoute_sys_name = rem_table.get('lldpRemSysName', "")
                            remoute_port_name = self._snmp.get_property('LLDP-MIB', 'lldpRemPortDesc', port_id)
                            if remoute_port_name and remoute_sys_name:
                                result = result_template.format(remote_host=remoute_sys_name,
                                                                remote_port=remoute_port_name)
                                break
        return result

    def _get_auto_neg(self):
        """Get port auto negotiation status

        :return return "True"
        """

        try:
            auto_negotiation = self._snmp.get(('MAU-MIB', 'ifMauAutoNegAdminStatus', self.if_index, 1)).values()[0]
            if 'enabled' in auto_negotiation.lower():
                return 'True'
        except Exception as e:
            self._logger.error('Failed to load auto negotiation property for interface {0}'.format(e.message))

    def _get_duplex(self):
        """Get current duplex state

        :return str "Full"
        """

        for key, value in self._port_attributes_snmp_tables.duplex_table.iteritems():
            if 'dot3StatsIndex' in value.keys() and value['dot3StatsIndex'] == str(self.if_index):
                interface_duplex = self._snmp.get_property('EtherLike-MIB', 'dot3StatsDuplexStatus', key)
                if 'fullDuplex' in interface_duplex:
                    return 'Full'

    def _get_ipv4(self):
        """Get IPv4 address details for provided port

        :return str IPv4 Address
        """

        if self._port_attributes_snmp_tables.ip_v4_table:
            for key, value in self._port_attributes_snmp_tables.ip_v4_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == self.if_index:
                    return key

    def _get_ipv6(self):
        """Get IPv6 address details for provided port

        :return str IPv6 Address
        """

        if self._port_attributes_snmp_tables.ip_v6_table:
            for key, value in self._port_attributes_snmp_tables.ip_v6_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == self.if_index:
                    return key
