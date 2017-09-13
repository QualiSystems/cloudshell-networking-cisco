class SnmpPortAttrTables(object):
    def __init__(self, snmp_handler, logger):
        self._snmp = snmp_handler
        self._logger = logger
        self._lldp_remote_table = dict()
        self._lldp_local_table = dict()
        self._cdp_table = dict()
        self._duplex_table = dict()
        self._ip_v4_table = dict()
        self._ip_v6_table = dict()
        self._port_channel_ports = dict()

    @property
    def lldp_remote_table(self):
        if not self._lldp_remote_table:
            self._lldp_remote_table = self._snmp.get_table('LLDP-MIB', 'lldpRemSysName')
            self._logger.info('lldpRemSysName table loaded')
        return self._lldp_remote_table

    @property
    def lldp_local_table(self):
        if not self._lldp_remote_table:
            lldp_local_table = self._snmp.get_table('LLDP-MIB', 'lldpLocPortDesc')
            if lldp_local_table:
                self._lldp_local_table = dict([(v['lldpLocPortDesc'].lower(), k) for k, v in lldp_local_table.iteritems()])
            self._logger.info('lldpLocPortDesc table loaded')
        return self._lldp_remote_table

    @property
    def cdp_table(self):
        if not self._cdp_table:
            self._cdp_table = self._snmp.get_table('CISCO-CDP-MIB', 'cdpCacheDeviceId')
            self._logger.info('cdpCacheDeviceId table loaded')
        return self._cdp_table

    @property
    def duplex_table(self):
        if not self._duplex_table:
            self._duplex_table = self._snmp.get_table('EtherLike-MIB', 'dot3StatsIndex')
            self._logger.info('dot3StatsIndex table loaded')
        return self._duplex_table

    @property
    def ip_v4_table(self):
        if not self._ip_v4_table:
            self._ip_v4_table = self._snmp.get_table('IP-MIB', 'ipAddrTable')
            self._logger.info('ipAddrTable table loaded')
        return self._ip_v4_table

    @property
    def ip_v6_table(self):
        if not self._ip_v6_table:
            self._ip_v6_table = self._snmp.get_table('IPV6-MIB', 'ipv6AddrEntry')
            self._logger.info('ipv6AddrEntry table loaded')
        return self._ip_v6_table

    @property
    def port_channel_ports(self):
        if not self._port_channel_ports:
            self._port_channel_ports = self._snmp.get_table('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID')
            self._logger.info('dot3adAggPortAttachedAggID table loaded')
        return self._port_channel_ports
