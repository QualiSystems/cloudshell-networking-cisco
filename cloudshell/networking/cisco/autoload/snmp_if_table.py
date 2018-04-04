import re
from cloudshell.networking.cisco.autoload.snmp_if_entity import SnmpIfEntity
from cloudshell.networking.cisco.autoload.snmp_if_port_channel_entity import SnmpIfPortChannelEntity
from cloudshell.networking.cisco.autoload.snmp_if_port_entity import SnmpIfPortEntity
from cloudshell.networking.cisco.autoload.snmp_port_attr_tables import SnmpPortAttrTables


class SnmpIfTable(object):
    PORT_CHANNEL_NAME = ["port-channel", "bundle-ether"]
    PORT_EXCLUDE_LIST = ["mgmt", "management", "loopback", "null"]

    def __init__(self, snmp_handler, logger):
        self._snmp = snmp_handler
        self._logger = logger
        self._load_snmp_tables()
        self._if_entities_dict = dict()
        self._if_port_dict = dict()
        self._if_port_channels_dict = dict()
        self.port_attributes_snmp_tables = SnmpPortAttrTables(snmp_handler, logger)

    @property
    def if_entities(self):
        if not self._if_entities_dict:
            self._get_if_entities()
        return self._if_entities_dict.values()

    @property
    def if_ports(self):
        if not self._if_port_dict:
            self._get_if_entities()
        return self._if_port_dict.values()

    @property
    def if_port_channels(self):
        if not self._if_port_channels_dict:
            self._get_if_entities()
        return self._if_port_channels_dict.values()

    def get_if_entity_by_index(self, if_index):
        if not self._if_entities_dict:
            self._get_if_entities()
        return self._if_entities_dict.get(if_index)

    def _get_if_entities(self):
        for index in self._if_table.keys():
            interface_name = self._if_table.get(index, {}).get("ifDescr", "")
            if "." in interface_name:
                continue
            if any([port_channel for port_channel in self.PORT_CHANNEL_NAME if port_channel in interface_name.lower()]):

                port_channel_obj = SnmpIfPortChannelEntity(snmp_handler=self._snmp, logger=self._logger,
                                                           index=index, name=interface_name,
                                                           port_attributes_snmp_tables=self.port_attributes_snmp_tables)
                self._if_entities_dict[index] = port_channel_obj
                self._if_port_channels_dict[index] = port_channel_obj
            elif any([exclude_port for exclude_port in self.PORT_EXCLUDE_LIST if
                      exclude_port in interface_name.lower()]):
                continue
            else:
                port_obj = SnmpIfPortEntity(snmp_handler=self._snmp, logger=self._logger,
                                            index=index, name=interface_name,
                                            port_attributes_snmp_tables=self.port_attributes_snmp_tables)
                self._if_entities_dict[index] = port_obj
                self._if_port_dict[index] = port_obj

    def _load_snmp_tables(self):
        """ Load all cisco required snmp tables

        :return:
        """

        self._logger.info('Start loading MIB tables:')
        self._if_table = self._snmp.get_table('IF-MIB', "ifDescr")
        self._logger.info('ifIndex table loaded')

        self._logger.info('MIB Tables loaded successfully')

    def get_if_index_from_port_name(self, port_name, port_filter_list):
        port_if_re = re.findall('\d+', port_name)
        if port_if_re:
            if_table_re = "/".join(port_if_re)
            for interface in self.if_ports:
                if not re.search("ethernet|other", interface.if_type, re.IGNORECASE):
                    continue
                if re.search(r"^(?!.*null|.*{0})\D*{1}(/\D+|$)".format(port_filter_list, if_table_re),
                             interface.if_name, re.IGNORECASE):
                    return interface
