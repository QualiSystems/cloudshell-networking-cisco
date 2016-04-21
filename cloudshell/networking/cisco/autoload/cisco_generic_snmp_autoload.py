__author__ = 'coye'
import inject
import re
import os
from collections import OrderedDict

from cloudshell.shell.core.context.driver_context import AutoLoadResource
from cloudshell.shell.core.context.driver_context import AutoLoadAttribute
from cloudshell.shell.core.context.driver_context import AutoLoadDetails

from cloudshell.networking.cisco.resource_drivers_map import CISCO_RESOURCE_DRIVERS_MAP

class CiscoGenericSNMPAutoload(object):
    @inject.params(snmp_handler='snmp_handler', logger='logger')
    def __init__(self, snmp_handler=None, logger=None):
        """Basic init with injected snmp handler and logger

        :param snmp_handler:
        :param logger:
        :return:
        """
        self.snmp = snmp_handler
        self._logger = logger

        local_mib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp.update_mib_sources(local_mib_path)
        self._load_snmp_tables()

    def _load_snmp_tables(self):
        """ Load cisco required snmp tables

        :return:
        """

        self._logger.info('Start loading MIB tables:')
        self.entity_table = self.snmp.get_table('ENTITY-MIB', 'entPhysicalTable')
        if len(self.entity_table.keys()) < 1:
            raise Exception('Cannot load entPhysicalTable. Autoload cannot continue')
        self._logger.info('Entity table loaded')

        self.if_table = self.snmp.get_table('IF-MIB', 'ifDescr')
        self._logger.info('IfTable loaded')

        self.snmp_mib = self.snmp.get_table('SNMPv2-MIB', 'system')
        self.lldp_local_table = self.snmp.get_table('LLDP-MIB', 'lldpLocPortDesc')
        self.lldp_remote_table = self.snmp.get_table('LLDP-MIB', 'lldpRemTable')
        self.cdp_index_table = self.snmp.get_table('CISCO-CDP-MIB', 'cdpInterface')
        self.cdp_table = self.snmp.get_table('CISCO-CDP-MIB', 'cdpCacheTable')
        self.duplex_table = self.snmp.get_table('EtherLike-MIB', 'dot3StatsIndex')
        self.ip_v4_table = self.snmp.get_table('IP-MIB', 'ipAddrTable')
        self.ip_v6_table = self.snmp.get_table('IPV6-MIB', 'ipv6AddrEntry')
        self.if_x_table = self.snmp.get_table('IF-MIB', 'ifAlias')
        self.port_channel_ports = self.snmp.get_table('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID')

        self._logger.info('MIB Tables loaded successfully')
        self.port_mapping = self.get_mapping()

    def discover(self):
        """ Load device structure and attributes: chassis, modules, submodules, ports

        :return: formatted string
        """

        self.port_relative_address = []
        root_element = self.entity_table.filter_by_column('ParentRelPos', '-1')
        if len(root_element.keys()) > 0:
            device_id = root_element.keys()[0]
        else:
            root_element = self.entity_table.filter_by_column('ParentRelPos', '0')
            if len(root_element.keys()) > 0:
                device_id = root_element.keys()[0]
            else:
                raise Exception('Cisco Autoload', "Device's root element not found")

        self.module_list = []
        port_list = self.get_port_list()
        self.get_module_list(port_list)
        power_port_list = self.entity_table.filter_by_column('Class', "'powerSupply'").sort_by_column(
            'ParentRelPos').keys()
        self.chassis_list = self.entity_table.filter_by_column('Class', "'chassis'").sort_by_column(
            'ParentRelPos').keys()

        self.resources = []
        self.attributes = []
        # methods fill self.resources and self.attributes lists
        self._get_device_details(device_id)
        self._get_chassis_attributes(self.chassis_list)
        self._get_ports_attributes(port_list)
        self._get_module_attributes()
        self._get_power_ports(power_port_list)
        self._get_port_channels()

        result = AutoLoadDetails(resources=self.resources, attributes=self.attributes)
        return result

    def get_port_list(self):
        """Read all ports from filtered entity mib table

        :return: filtered_port_list
        """
        filtered_port_list = []
        raw_port_list = self.entity_table.filter_by_column('Class', "'port'").sort_by_column('ParentRelPos').keys()
        for port in raw_port_list:
            if 'serial' in self.entity_table[port]['entPhysicalName'].lower() or \
                            'serial' in self.entity_table[port]['entPhysicalDescr'].lower():
                continue
            if 'stack' in self.entity_table[port]['entPhysicalName'].lower() or \
                            'stack' in self.entity_table[port]['entPhysicalDescr'].lower():
                continue
            if 'engine' in self.entity_table[port]['entPhysicalName'].lower() or \
                            'engine' in self.entity_table[port]['entPhysicalDescr'].lower():
                continue
            if 'management' in self.entity_table[port]['entPhysicalDescr'].lower():
                continue
            filtered_port_list.append(port)
        return filtered_port_list

    def get_module_list(self, port_list):
        """Set list of all modules from entity mib table for provided list of ports

        :param port_list:
        :return:
        """
        for port in port_list:
            if port in self.port_mapping.keys():
                module_id = int(self.entity_table[port]['entPhysicalContainedIn'])
                if re.search('container', self.entity_table[module_id]['entPhysicalClass']):
                    module_id = int(self.entity_table[module_id]['entPhysicalContainedIn'])
                if re.search('module', self.entity_table[module_id]['entPhysicalClass']):
                    if module_id not in self.module_list:
                        self.module_list.append(module_id)

    def _get_chassis_attributes(self, chassis_list):
        """Get Chassis element attributes

        :param chassis_list: list of chassis to load attributes for
        :return:
        """

        self._logger.info('Start loading Chassis')
        for chassis in chassis_list:
            chassis_id = self.entity_table[chassis]['entPhysicalParentRelPos']
            if chassis_id == '-1':
                chassis_id = '0'
            chassis_details_map = {
                'Model': self.entity_table[chassis]['entPhysicalModelName'],
                'Serial Number': self.entity_table[chassis]['entPhysicalSerialNum']
            }
            if chassis_details_map['Model'] == '':
                chassis_details_map['Model'] = self.entity_table[chassis]['entPhysicalDescr']
            module_name = 'Chassis {0}'.format(chassis_id)
            relative_path = '{0}'.format(chassis_id)
            info_data = {'name': module_name,
                         'model': 'Generic Chassis',
                         'relative_path': relative_path}
            self._add_resources_data(info_data)
            self._add_attributes_data(relative_path, chassis_details_map)
            self._logger.info('Added ' + self.entity_table[chassis]['entPhysicalDescr'] + ' Module')
        self._logger.info('Finished Loading Modules')

    def _get_module_attributes(self):
        """Set attributes for all discovered modules

        :return:
        """

        self._logger.info('Start loading Modules')
        for module in self.module_list:
            parent_id = int(self.entity_table[module]['entPhysicalContainedIn'])
            if re.search('container', self.entity_table[parent_id]['entPhysicalClass']):
                module_id = self.entity_table[parent_id]['entPhysicalParentRelPos']
            else:
                module_id = self.entity_table[module]['entPhysicalParentRelPos']
            relative_id = self._get_relative_path(module) + '/' + module_id
            if relative_id not in self.port_relative_address:
                continue
            module_details_map = {
                'Model': self.entity_table[module]['entPhysicalDescr'] or '',
                'Version': self.entity_table[module]['entPhysicalSoftwareRev'] or '',
                'Serial Number': self.entity_table[module]['entPhysicalSerialNum'] or ''
            }
            model = 'Generic Sub Module'
            if '/' in relative_id and len(relative_id.split('/')) < 3:
                module_name = 'Module {0}'.format(module_id)
                model = 'Generic Module'
            else:
                module_name = 'Sub Module {0}'.format(module_id)
            info_data = {'name': module_name,
                         'model': model,
                         'relative_path': relative_id}
            self._add_resources_data(info_data)
            self._add_attributes_data(relative_id, module_details_map)
            self._logger.info('Added ' + self.entity_table[module]['entPhysicalDescr'] + ' Module')
        self._logger.info('Finished Loading Modules')

    def _get_power_ports(self, power_ports):
        """Get attributes for ports provided in power_ports list

        :param power_ports:
        :return:
        """
        self._logger.info('Start loading Power Ports')
        for port in power_ports:
            module_name = self.entity_table[port]['entPhysicalName']
            relative_path = '{0}/PP{1}'.format(self._get_relative_path(port),
                                               self.entity_table[port]['entPhysicalParentRelPos'])
            chassis_details_map = {'Model': self.entity_table[port]['entPhysicalModelName'].strip('\s'),
                                   'Port Description': self.entity_table[port]['entPhysicalDescr'],
                                   'Version': self.entity_table[port]['entPhysicalHardwareRev'],
                                   'Serial Number': self.entity_table[port]['entPhysicalSerialNum']}
            info_data = {'name': 'PP{0}'.format(relative_path.replace('/', '-').replace('PP', '')),
                         'relative_path': relative_path,
                         'model': 'Generic Power Port'}

            self._add_resources_data(info_data)
            self._add_attributes_data(relative_path, chassis_details_map)
            self._logger.info('Added ' + module_name.strip('\s') + ' Power Port')
        self._logger.info('Finished Loading Power Ports')

    def _get_port_channels(self):
        """Get all port channels and set attributes for them

        :return:
        """
        port_channel_dic = {index: port for index, port in self.if_table.iteritems() if 'channel' in port['ifDescr']}
        self._logger.info('Start loading Port Channels')
        for key, value in port_channel_dic.iteritems():
            interface_model = value['ifDescr']
            match_object = re.search('\d+$', interface_model)
            if match_object:
                interface_id = 'PC{0}'.format(match_object.group(0))
            else:
                self._logger.error('Adding of {0} failed. Name is invalid'.format(interface_model))
                continue
            attribute_map = {'Protocol Type': 'Transparent', 'Port Description': self.if_x_table[key]['ifAlias'],
                             'Associated Ports': self._get_associated_ports(key)}
            attribute_map.update(self._get_ip_interface_details(key))
            info_data = {'model': 'Generic Port Channel',
                         'name': interface_model,
                         'relative_path': interface_id}
            self._add_resources_data(info_data)
            self._add_attributes_data(interface_id, attribute_map)

            self._logger.info('Added ' + interface_model + ' Port Channel')
        self._logger.info('Finished Loading Port Channels')

    def _get_associated_ports(self, item_id):
        """Get all ports associated with provided port channel

        :param item_id:
        :return:
        """
        result = ''
        for key, value in self.port_channel_ports.iteritems():
            if str(item_id) in value['dot3adAggPortAttachedAggID']:
                result += self.if_table[key]['ifDescr'].replace('/', '-').replace(' ', '') + '; '
        return result.strip('\s')

    def _get_ports_attributes(self, ports):
        """Get port attributes for specified list of ports

        :param ports: list of ports to fill attributes
        :return:
        """

        self._logger.info('Start loading Ports')
        for port in ports:
            if port not in self.port_mapping.keys():
                continue
            interface_model = 'Generic Port'
            if_table_port_attr = ['ifType', 'ifPhysAddress', 'ifMtu', 'ifSpeed']
            if_table = self.if_table[self.port_mapping[port]].copy()
            if_table.update(self.snmp.get_bulk_values('IF-MIB', self.port_mapping[port], if_table_port_attr))
            interface_name = self.if_table[self.port_mapping[port]]['ifDescr']
            datamodel_interface_name = interface_name.replace('/', '-').replace('\s+', '')
            parent_id = int(self.entity_table[port]['entPhysicalContainedIn'])
            interface_id = self.entity_table[port]['entPhysicalParentRelPos']
            if 'container' in self.entity_table[parent_id]['entPhysicalClass'].lower():
                interface_id = self.entity_table[parent_id]['entPhysicalParentRelPos']
            relative_id = self._get_relative_path(port)
            relative_path = relative_id + '/{0}'.format(interface_id)
            attribute_map = {'L2 Protocol Type':
                                 if_table[self.port_mapping[port]]['ifType'].replace('/', '').replace("'", ''),
                             'MAC Address': if_table[self.port_mapping[port]]['ifPhysAddress'],
                             'MTU': if_table[self.port_mapping[port]]['ifMtu'],
                             'Bandwidth': if_table[self.port_mapping[port]]['ifSpeed'],
                             'Port Description': self.if_x_table[self.port_mapping[port]]['ifAlias'],
                             'Adjacent': self._get_adjacent(port),
                             'Protocol Type': 'Transparent'}
            attribute_map.update(self._get_interface_details(self.port_mapping[port]))
            attribute_map.update(self._get_ip_interface_details(self.port_mapping[port]))
            info_data = {'model': interface_model,
                         'name': '{0}'.format(datamodel_interface_name),
                         'relative_path': relative_path}
            self._add_resources_data(info_data)
            self._add_attributes_data(relative_path, attribute_map)
            self.port_relative_address.append(relative_id)
            self._logger.info('Added ' + interface_name + ' Port')
        self._logger.info('Finished Loading Ports')

    def _get_relative_path(self, item_id):
        """Build relative path for received item

        :param item_id:
        :return:
        """
        parent = int(self.entity_table[item_id]['entPhysicalContainedIn'])
        if parent in self.module_list:
            parent_id = int(self.entity_table[parent]['entPhysicalContainedIn'])
            if re.search('container', self.entity_table[parent_id]['entPhysicalClass']):
                result = '/' + self.entity_table[parent_id]['entPhysicalParentRelPos']
            else:
                result = '/' + self.entity_table[parent]['entPhysicalParentRelPos']
            result = self._get_relative_path(parent) + result
        elif parent in self.chassis_list:
            result = self.entity_table[parent]['entPhysicalParentRelPos']
            if result == '-1':
                result = '0'
        else:
            result = self._get_relative_path(parent)
        return result

    def _get_ip_interface_details(self, port_index):
        """Get IP address details for provided port

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'IPv4 Address': '', 'IPv6 Address': ''}
        """

        interface_details = {'IPv4 Address': '', 'IPv6 Address': ''}
        for key, value in self.ip_v4_table.iteritems():
            if int(value['ipAdEntIfIndex']) == index:
                interface_details['IPv4 Address'] = key
                break
        for key, value in self.ip_v6_table.iteritems():
            if int(value['ipAdEntIfIndex']) == index:
                interface_details['IPv6 Address'] = key
                break
        return interface_details

    def _get_interface_details(self, port_index):
        """Get interface attributes

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'Auto Negotiation': '', 'Duplex': ''}
        """
        interface_details = {'Duplex': 'Full', 'Auto Negotiation': 'False'}
        auto_negotiation = self.snmp.get(('MAU-MIB', 'ifMauAutoNegAdminStatus',
                                          '{0}'.format(index), '1')).values()[0].replace("'", '')
        if auto_negotiation and auto_negotiation == 'enabled':
            interface_details['Auto Negotiation'] = 'True'
        for key, value in self.duplex_table.iteritems():
            if value['dot3StatsIndex'] == str(index):
                interface_duplex = self.snmp.get_value('EtherLike-MIB', 'dot3StatsDuplexStatus', key)
                if 'halfDuplex' in interface_duplex:
                    interface_details['Duplex'] = 'Half'
        return interface_details

    def _add_attributes_data(self, relative_path, dict_data=None):
        """

        :param relative_path:
        :param dict_data:
        :return:
        """
        for key, value in dict_data.items():
            self.attributes.append(AutoLoadAttribute(relative_address=relative_path,
                                                     attribute_name=key,
                                                     attribute_value=value))

    def _add_resources_data(self, dict_data=None):
        if 'model' not in dict_data or 'name' not in dict_data or 'relative_path' not in dict_data:
            raise Exception('Cisco Generic SNMP Autoload', 'Resources details not found!')
        self.resources.append(AutoLoadResource(dict_data['model'], dict_data['name'], dict_data['relative_path']))

    def _get_device_details(self, index):
        self._logger.info('Start loading Switch Attributes')
        result = {'Vendor': 'Cisco',
                  'System Name': self.snmp.get_value('SNMPv2-MIB', 'sysName', 0),
                  # 'pid': self.entity_table[index]['entPhysicalHardwareRev'],
                  'Model': '',
                  'Location': self.snmp.get_value('SNMPv2-MIB', 'sysLocation', 0),
                  'Contact Name': self.snmp.get_value('SNMPv2-MIB', 'sysContact', 0),
                  'OS Version': ''
                  # 'firmware': ''
                  }

        match_version = re.search('\S\s*\((?P<firmware>\S+)\)\S\s*Version\s+(?P<software_version>\S+)\S*\s+',
                                  self.snmp.get_value('SNMPv2-MIB', 'sysDescr', 0))
        if match_version:
            result['OS Version'] = match_version.groupdict()['software_version'].replace(',', '')
            # result['firmware'] = match_version.groupdict()['firmware']

        result.update(self._get_device_model_and_vendor())

        self._logger.info('Finished Loading Switch Attributes')

        self._add_attributes_data('', result)

    def _get_adjacent(self, interface_id):
        result = ''
        for key, value in self.cdp_table.iteritems():
            if re.search('^\d+', str(key)).group(0) == self.port_mapping[interface_id]:
                result = '{0} through {1}'.format(value['cdpCacheDeviceId'], value['cdpCacheDevicePort'])
        if result == '' and self.lldp_remote_table:
            for key, value in self.lldp_local_table.iteritems():
                if self.entity_table[interface_id]['entPhysicalDescr'] in value['lldpLocPortDesc']:
                    result = '{0} through {1}'.format(self.lldp_remote_table[key]['lldpRemSysName'],
                                                      self.lldp_remote_table[key]['lldpRemPortDesc'])
        return result

    def _get_device_model_and_vendor(self):
        result = {'Vendor': 'Cisco', 'Model': ''}
        match_name = re.search(r'^SNMPv2-SMI::enterprises\.(?P<vendor>\d+)(\.\d)+\.(?P<model>\d+$)',
                               self.snmp.get_value('SNMPv2-MIB', 'sysObjectID', 0))
        if match_name is None:
            match_name = re.search(r'1\.3\.6\.1\.4\.1\.(?P<vendor>\d+)(\.\d)+\.(?P<model>\d+$)',
                                   self.snmp.get_value('SNMPv2-MIB', 'sysObjectID', 0))
            if match_name is None:
                match_name = re.search(r'^(?P<vendor>\w+)-SMI::cisco(Products|Modules)\S*\.(?P<model>\d+)$',
                                       self.snmp.get_value('SNMPv2-MIB', 'sysObjectID', 0))

        if match_name:
            model = match_name.groupdict()['model']
            if model in CISCO_RESOURCE_DRIVERS_MAP:
                result['Model'] = CISCO_RESOURCE_DRIVERS_MAP[model].lower().replace('_', '').capitalize()
        if not result['Model'] or result['Model'] == '':
            self.snmp.load_mib('CISCO-PRODUCTS-MIB')
            match_name = re.search(r'^(?P<vendor>\S+)-P\S*\s*::(?P<model>\S+$)',
                                   self.snmp.get_value('SNMPv2-MIB', 'sysObjectID', '0'))
            if match_name:
                result['Vendor'] = match_name.groupdict()['vendor'].capitalize()
                result['Model'] = match_name.groupdict()['model'].capitalize()
        return result

    def get_mapping(self):
        """Get mapping from entPhysicalTable to ifTable.
        Build mapping based on entAliasMappingTable if exists else build manually based on
        entPhysicalDescr <-> ifDescr mapping.

        :return: simple mapping from entPhysicalTable index to ifTable index:
        |        {entPhysicalTable index: ifTable index, ...}
        """

        mapping = OrderedDict()
        entAliasMappingTable = self.snmp.walk(('ENTITY-MIB', 'entAliasMappingTable'))
        if entAliasMappingTable:
            for port in self.entity_table.filter_by_column('Class', "'port'"):
                if port in entAliasMappingTable.keys():
                    entAliasMappingIdentifier = entAliasMappingTable[port]['entAliasMappingIdentifier']
                    mapping[port] = int(entAliasMappingIdentifier.split('.')[-1])
        else:
            mapping = self._descr_based_mapping()

        return mapping

    def _descr_based_mapping(self):
        """ Manually calculate mapping from entityTable to ifTable.
        :return: simple mapping from entPhysicalTable index to ifTable index:
        |        {entPhysicalTable index: ifTable index, ...}
        """

        mapping = OrderedDict()
        for port in self.entity_table.filter_by_column('Class', "'port'").values():
            entPhysicalDescr = port['entPhysicalDescr']
            module_index, port_index = re.findall('\d+', entPhysicalDescr)
            ifTable_re = '^.*' + module_index + '/' + port_index + '$'
            for interface in self.if_table.values():
                if re.search(ifTable_re, interface['ifDescr']):
                    mapping[int(port['suffix'])] = int(interface['suffix'])
                    continue
        return mapping