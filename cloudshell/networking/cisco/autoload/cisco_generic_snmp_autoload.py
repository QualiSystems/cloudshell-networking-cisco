import re
import os
from cloudshell.networking.cisco.autoload.cisco_snmp_entity_table import CiscoSNMPEntityTable
from cloudshell.shell.core.driver_context import AutoLoadDetails


class CiscoGenericSNMPAutoload(object):
    IF_ENTITY = "ifDescr"
    ENTITY_PHYSICAL = "entPhysicalDescr"

    def __init__(self, snmp_handler, logger, supported_os, resource_name):
        """Basic init with injected snmp handler and logger

        :param snmp_handler:
        :param logger:
        :return:
        """

        self.snmp = snmp_handler
        self.resource_name = resource_name
        self.logger = logger
        self.supported_os = supported_os
        self.cisco_entity = CiscoSNMPEntityTable(snmp_handler, logger)
        self.resources = list()
        self.attributes = list()
        self.port = None
        self.power_port = None
        self.port_channel = None
        self.root_model = None
        self.chassis = None
        self.module = None

    def load_cisco_mib(self):
        """
        Loads Cisco specific mibs inside snmp handler

        """
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp.update_mib_sources(path)

    def discover(self):
        """General entry point for autoload,
        read device structure and attributes: chassis, modules, submodules, ports, port-channels and power supplies

        :return: AutoLoadDetails object
        """

        self._is_valid_device_os()

        self.logger.info('************************************************************************')
        self.logger.info('Start SNMP discovery process .....')

        self.load_cisco_mib()
        self.snmp.load_mib(['CISCO-PRODUCTS-MIB', 'CISCO-ENTITY-VENDORTYPE-OID-MIB'])
        self._get_device_details()
        self._load_snmp_tables()
        port_list = self.cisco_entity.get_port_list
        module_list = self.cisco_entity.get_module_list
        chassis_list = self.cisco_entity.get_chassis
        if not chassis_list:
            raise Exception(self.__class__.__name__, "Failed to load chassis, cannot continue")

        self._get_chassis_attributes(chassis_list)
        self.cisco_entity.add_relative_addresss()
        self._get_ports_attributes(port_list)
        self._get_module_attributes(module_list)
        self._get_power_ports(self.cisco_entity.get_power_port_list)
        self._get_port_channels()

        result = AutoLoadDetails(resources=self.resources, attributes=self.attributes)

        self.logger.info('*******************************************')
        self.logger.info('SNMP discovery Completed.')
        self.logger.info('The following platform structure detected:' +
                         '\nModel, Name, Relative Path, Uniqe Id')

        for resource in self.resources:
            self.logger.info('{0},\t\t{1},\t\t{2},\t\t{3}'.format(resource.model, resource.name,
                                                                  resource.relative_address,
                                                                  resource.unique_identifier))
        self.logger.info('------------------------------')
        for attribute in self.attributes:
            self.logger.info('{0},\t\t{1},\t\t{2}'.format(attribute.relative_address, attribute.attribute_name,
                                                          attribute.attribute_value))

        self.logger.info('*******************************************')

        return result

    def _is_valid_device_os(self):
        """Validate device OS using snmp
        :return: True or False
        """

        device_os = None
        system_description = self.snmp.get(('SNMPv2-MIB', 'sysDescr'))['sysDescr']
        res = re.search(r"({0})".format("|".join(self.supported_os)),
                        system_description,
                        flags=re.DOTALL | re.IGNORECASE)
        if res:
            device_os = res.group(0).strip(' \s\r\n')
        if device_os:
            return

        self.logger.info('Detected system description: \'{0}\''.format(system_description))

        error_message = 'Incompatible driver! Please use this driver for \'{0}\' operation system(s)'. \
            format(str(tuple(self.supported_os)))
        self.logger.error(error_message)
        raise Exception(error_message)

    def _load_snmp_tables(self):
        """ Load all cisco required snmp tables

        :return:
        """

        self.logger.info('Start loading MIB tables:')
        self.if_table = self.snmp.get_table('IF-MIB', self.IF_ENTITY)
        self.if_type_table = self.snmp.get_table('IF-MIB', "ifType")
        self.logger.info('{0} table loaded'.format(self.IF_ENTITY))
        self.entity_table = self.cisco_entity.get_entity_table()
        self.logger.info('Entity table loaded')

        self.lldp_remote_table = self.snmp.get_table('LLDP-MIB', 'lldpRemSysName')
        self.lldp_local_table = dict()
        lldp_local_table = self.snmp.get_table('LLDP-MIB', 'lldpLocPortDesc')
        if lldp_local_table:
            self.lldp_local_table = dict([(v['lldpLocPortDesc'].lower(), k) for k, v in lldp_local_table.iteritems()])
        self.cdp_table = self.snmp.get_table('CISCO-CDP-MIB', 'cdpCacheDeviceId')
        self.duplex_table = self.snmp.get_table('EtherLike-MIB', 'dot3StatsIndex')
        self.ip_v4_table = self.snmp.get_table('IP-MIB', 'ipAddrTable')
        self.ip_v6_table = self.snmp.get_table('IPV6-MIB', 'ipv6AddrEntry')
        self.port_channel_ports = self.snmp.get_table('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID')

        self.logger.info('MIB Tables loaded successfully')

    def _add_resource(self, resource):
        """Add object data to resources and attributes lists

        :param resource: object which contains all required data for certain resource
        """

        self.resources.append(resource.get_resource())
        self.attributes.extend(resource.get_attributes())

    def _get_chassis_attributes(self, chassis_list):
        """Get Chassis element attributes

        :param chassis_list: list of chassis to load attributes for
        :return:
        """

        self.logger.info('Start loading Chassis')
        for chassis in chassis_list:
            chassis_id = self.cisco_entity.relative_address[chassis]
            chassis_details_map = {
                self.chassis.MODEL: self.snmp.get_property('ENTITY-MIB', 'entPhysicalModelName', chassis),
                self.chassis.SERIAL_NUMBER: self.snmp.get_property('ENTITY-MIB', 'entPhysicalSerialNum', chassis)
            }
            if chassis_details_map[self.chassis.MODEL] == '':
                chassis_details_map[self.chassis.MODEL] = self.entity_table[chassis]['entPhysicalDescr']
            relative_address = '{0}'.format(chassis_id)
            name = 'Chassis {}'.format(chassis_id)
            unique_id = '{}.{}.{}'.format(self.resource_name, 'chassis', chassis)
            chassis_object = self.chassis(name=name,
                                          relative_address=relative_address,
                                          unique_id=unique_id,
                                          **chassis_details_map)
            self._add_resource(chassis_object)
            self.logger.info('Added ' + self.entity_table[chassis]['entPhysicalDescr'] + ' Chassis')
        self.logger.info('Finished Loading Modules')

    def _get_module_attributes(self, module_list):
        """Set attributes for all discovered modules

        :return:
        """

        self.logger.info('Start loading Modules')
        for module in module_list:
            module_id = self.cisco_entity.relative_address.get(module)
            module_index = self.cisco_entity.get_resource_id(module)
            module_details_map = {
                self.module.MODEL: self.entity_table[module]['entPhysicalDescr'],
                self.module.VERSION: self.snmp.get_property('ENTITY-MIB', 'entPhysicalSoftwareRev', module),
                self.module.SERIAL_NUMBER: self.snmp.get_property('ENTITY-MIB', 'entPhysicalSerialNum', module)
            }

            if '/' in module_id and len(module_id.split('/')) < 3:
                module_name = 'Module {0}'.format(module_index)
                model = 'Generic Module'
                unique_id = '{}.{}.{}'.format(self.resource_name, 'module', module)
            else:
                module_name = 'Sub Module {0}'.format(module_index)
                model = 'Generic Sub Module'
                unique_id = '{}.{}.{}'.format(self.resource_name, 'sub-module', module)

            module_object = self.module(name=module_name, resource_model=model, relative_address=module_id,
                                        unique_id=unique_id, **module_details_map)
            self._add_resource(module_object)

            self.logger.info('Module {} added'.format(self.entity_table[module]['entPhysicalDescr']))
        self.logger.info('Load modules completed.')

    def _filter_power_port_list(self, power_supply_list):
        """Get power supply relative path

        :return: string relative path
        """

        unfiltered_power_supply_list = list(power_supply_list)
        for power_port in unfiltered_power_supply_list:
            parent_index = int(self.entity_table[power_port]['entPhysicalContainedIn'])
            if 'powerSupply' in self.entity_table[parent_index]['entPhysicalClass']:
                if parent_index in power_supply_list:
                    power_supply_list.remove(power_port)

    def _get_power_supply_parent_id(self, port):
        """
        Retrieve power port relative address, handles exceptional cases

        :param port:
        :return:
        """
        parent_index = int(self.entity_table[port]['entPhysicalContainedIn'])
        result = int(self.entity_table[parent_index]['entPhysicalParentRelPos'])
        return result

    def _get_power_ports(self, power_supply_list):
        """Get attributes for power ports provided in self.power_supply_list

        :return:
        """

        self.logger.info('Load Power Ports:')
        self._filter_power_port_list(power_supply_list)
        for port in power_supply_list:
            port_id = self.entity_table[port]['entPhysicalParentRelPos']
            parent_index = int(self.entity_table[port]['entPhysicalContainedIn'])
            parent_id = self._get_power_supply_parent_id(port=port)
            chassis_id = self.cisco_entity.get_relative_address(parent_index)
            relative_address = '{0}/PP{1}-{2}'.format(chassis_id, parent_id, port_id)
            port_name = 'PP{0}'.format(power_supply_list.index(port))
            port_details = {self.power_port.MODEL: self.snmp.get_property('ENTITY-MIB', 'entPhysicalModelName', port, ),
                            self.power_port.PORT_DESCRIPTION: self.snmp.get_property('ENTITY-MIB', 'entPhysicalDescr',
                                                                                     port, 'str'),
                            self.power_port.VERSION: self.snmp.get_property('ENTITY-MIB', 'entPhysicalHardwareRev',
                                                                            port),
                            self.power_port.SERIAL_NUMBER: self.snmp.get_property('ENTITY-MIB', 'entPhysicalSerialNum',
                                                                                  port)
                            }

            unique_id = '{}.{}.{}'.format(self.resource_name, 'power_port', port)
            power_port_object = self.power_port(name=port_name, relative_address=relative_address,
                                                unique_id=unique_id, **port_details)
            self._add_resource(power_port_object)

            self.logger.info('Added ' + self.entity_table[port]['entPhysicalName'].strip(' \t\n\r') + ' Power Port')
        self.logger.info('Load Power Ports completed.')

    def _get_port_channels(self):
        """Get all port channels and set attributes for them

        :return:
        """

        if not self.if_table:
            return
        port_channel_dic = {index: port for index, port in self.if_table.iteritems() if
                            'channel' in port[self.IF_ENTITY] and '.' not in port[self.IF_ENTITY]}
        self.logger.info('Loading Port Channels:')
        for key, value in port_channel_dic.iteritems():
            interface_model = value[self.IF_ENTITY]
            match_object = re.search(r'\d+$', interface_model)
            if match_object:
                interface_id = 'PC{0}'.format(match_object.group(0))
            else:
                self.logger.error('Adding of {0} failed. Name is invalid'.format(interface_model))
                continue
            attribute_map = {self.port_channel.PORT_DESCRIPTION: self.snmp.get_property('IF-MIB', 'ifAlias', key),
                             self.port_channel.ASSOCIATED_PORTS: self._get_associated_ports(key)}

            unique_id = '{}.{}.{}'.format(self.resource_name, 'port-channel', interface_id)
            attribute_map.update(self._get_ip_interface_details(self.port_channel, key))
            port_channel = self.port_channel(name=interface_model, relative_address=interface_id,
                                             unique_id=unique_id, **attribute_map)
            self._add_resource(port_channel)

            self.logger.info('Added ' + interface_model + ' Port Channel')
        self.logger.info('Load Port Channels completed.')

    def _get_associated_ports(self, item_id):
        """Get all ports associated with provided port channel
        :param item_id:
        :return:
        """

        result = ''
        for key, value in self.port_channel_ports.iteritems():
            if str(item_id) in value['dot3adAggPortAttachedAggID'] \
                    and key in self.if_table \
                    and self.IF_ENTITY in self.if_table[key]:
                result += self.if_table[key][self.IF_ENTITY].replace('/', '-').replace(' ', '') + '; '
        return result.strip(' \t\n\r')

    def _get_ports_attributes(self, port_list):
        """Get resource details and attributes for every port in self.port_list

        :return:
        """

        self.logger.info('Load Ports:')
        for port in port_list:
            if_table_port_attr = {'ifType': 'str', 'ifPhysAddress': 'str', 'ifMtu': 'int', 'ifHighSpeed': 'int'}
            port_if_index = self._get_mapping(port, self.entity_table[port][self.ENTITY_PHYSICAL])
            if not port_if_index or port_if_index not in self.if_table:
                continue
            if_table = self.if_table[port_if_index].copy()
            if_table.update(self.snmp.get_properties('IF-MIB', port_if_index, if_table_port_attr))
            interface_name = self.if_table[port_if_index][self.IF_ENTITY].replace("'", '')
            if interface_name == '':
                interface_name = self.entity_table[port]['entPhysicalName']
            if interface_name == '':
                continue

            interface_type = if_table[port_if_index]['ifType'].replace('/', '').replace("'", '')
            attribute_map = {self.port.L2_PROTOCOL_TYPE: interface_type,
                             self.port.MAC_ADDRESS: if_table[port_if_index]['ifPhysAddress'],
                             self.port.MTU: if_table[port_if_index]['ifMtu'],
                             self.port.BANDWIDTH: if_table[port_if_index]['ifHighSpeed'],
                             self.port.PORT_DESCRIPTION: self.snmp.get_property('IF-MIB', 'ifAlias',
                                                                                port_if_index),
                             self.port.ADJACENT: self._get_adjacent(port_if_index)}
            attribute_map.update(self._get_interface_details(resource_obj=self.port,
                                                             port_index=port_if_index))
            attribute_map.update(self._get_ip_interface_details(resource_obj=self.port,
                                                                port_index=port_if_index))

            unique_id = '{}.{}.{}'.format(self.resource_name, 'port', port)

            port_object = self.port(name=interface_name.replace('/', '-'),
                                    relative_address=self.cisco_entity.relative_address[port],
                                    unique_id=unique_id, **attribute_map)
            self._add_resource(port_object)
            self.logger.info('Added ' + interface_name + ' Port')
        self.logger.info('Load port completed.')

    def _get_ip_interface_details(self, resource_obj, port_index):
        """Get IP address details for provided port

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'IPv4 Address': '', 'IPv6 Address': ''}
        """

        interface_details = {}
        if self.ip_v4_table and len(self.ip_v4_table) > 1:
            for key, value in self.ip_v4_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == port_index:
                    interface_details[resource_obj.IPV4_ADDRESS] = key
                break
        if self.ip_v6_table and len(self.ip_v6_table) > 1:
            for key, value in self.ip_v6_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == port_index:
                    interface_details[resource_obj.IPV6_ADDRESS] = key
                break
        return interface_details

    def _get_interface_details(self, resource_obj, port_index):
        """Get interface attributes

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'Auto Negotiation': '', 'Duplex': ''}
        """

        interface_details = {}
        try:
            auto_negotiation = self.snmp.get(('MAU-MIB', 'ifMauAutoNegAdminStatus', port_index, 1)).values()[0]
            if 'enabled' in auto_negotiation.lower():
                interface_details[resource_obj.AUTO_NEGOTIATION] = 'True'
        except Exception as e:
            self.logger.error('Failed to load auto negotiation property for interface {0}'.format(e.message))
        for key, value in self.duplex_table.iteritems():
            if 'dot3StatsIndex' in value.keys() and value['dot3StatsIndex'] == str(port_index):
                interface_duplex = self.snmp.get_property('EtherLike-MIB', 'dot3StatsDuplexStatus', key)
                if 'fullDuplex' in interface_duplex:
                    interface_details[resource_obj.DUPLEX] = 'Full'
        return interface_details

    def _get_device_details(self):
        """Get root element attributes

        """

        self.logger.info('Load Switch Attributes:')
        result = {self.root_model.SYSTEM_NAME: self.snmp.get_property('SNMPv2-MIB', 'sysName', 0),
                  self.root_model.VENDOR: 'Cisco',
                  self.root_model.MODEL: self._get_device_model(),
                  self.root_model.LOCATION: self.snmp.get_property('SNMPv2-MIB', 'sysLocation',
                                                                   0),
                  self.root_model.CONTACT_NAME: self.snmp.get_property(
                      'SNMPv2-MIB', 'sysContact', 0),
                  self.root_model.OS_VERSION: ''}

        match_version = re.search(r'Version\s+(?P<software_version>\S+)\S*\s+',
                                  self.snmp.get_property('SNMPv2-MIB', 'sysDescr', 0))
        if match_version:
            result['os_version'] = match_version.groupdict()['software_version'].replace(',', '')

        root = self.root_model(**result)
        self.attributes.extend(root.get_attributes())
        self.logger.info('Load Switch Attributes completed.')

    def _get_adjacent(self, interface_id):
        """Get connected device interface and device name to the specified port id, using cdp or lldp protocols

        :param interface_id: port id
        :return: device's name and port connected to port id
        :rtype string
        """

        result_template = '{remote_host} through {remote_port}'
        result = ''
        for key, value in self.cdp_table.iteritems():
            if str(key).startswith(str(interface_id)):
                port = self.snmp.get_property('CISCO-CDP-MIB', 'cdpCacheDevicePort', key)
                result = result_template.format(remote_host=value.get('cdpCacheDeviceId', ''), remote_port=port)
                break
        if result == '' and self.lldp_local_table:
            interface_name = self.if_table[interface_id][self.IF_ENTITY].lower()
            if interface_name:
                key = self.lldp_local_table.get(interface_name, None)
                if key:
                    for port_id, rem_table in self.lldp_remote_table.iteritems():
                        if ".{0}.".format(key) in port_id:
                            remoute_sys_name = rem_table.get('lldpRemSysName', "")
                            remoute_port_name = self.snmp.get_property('LLDP-MIB', 'lldpRemPortDesc', port_id)
                            if remoute_port_name and remoute_sys_name:
                                result = result_template.format(remote_host=remoute_sys_name,
                                                                remote_port=remoute_port_name)
                                break
        return result

    def _get_device_model(self):
        """Get device model form snmp SNMPv2 mib

        :return: device model
        :rtype: str
        """

        result = ''
        match_name = re.search(r'::(?P<model>\S+$)', self.snmp.get_property('SNMPv2-MIB', 'sysObjectID', '0'))
        if match_name:
            result = match_name.groupdict()['model'].capitalize()
        return result

    def _get_mapping(self, port_index, port_descr):
        """Get mapping from entPhysicalTable to ifTable.
        Build mapping based on ent_alias_mapping_table if exists else build manually based on
        entPhysicalDescr <-> ifDescr mapping.

        :return: simple mapping from entPhysicalTable index to ifTable index:
        |        {entPhysicalTable index: ifTable index, ...}
        """

        port_id = None
        port_exclude_list = self.cisco_entity.port_exclude_pattern.replace("|", "|.*")

        try:
            ent_alias_mapping_identifier = self.snmp.get(('ENTITY-MIB', 'entAliasMappingIdentifier', port_index, 0))
            port_id = int(ent_alias_mapping_identifier['entAliasMappingIdentifier'].split('.')[-1])
        except Exception as e:
            self.logger.error(e.message)

            port_if_re = re.findall('\d+', port_descr)
            if port_if_re:
                if_table_re = "/".join(port_if_re)
                for interface_id, interface_value in self.if_table.iteritems():
                    port_type = self.if_type_table.get(interface_id)
                    if port_type:
                        if not re.search("ethernet|other", port_type.get("ifType", ""), re.IGNORECASE):
                            continue
                    if re.search(r"^(?!.*null|.*{0})\D*{1}(/\D+|$)".format(port_exclude_list, if_table_re),
                                 interface_value[self.IF_ENTITY], re.IGNORECASE):
                        port_id = int(interface_value['suffix'])
                        break
        return port_id
