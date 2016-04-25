__author__ = 'coye'
import inject
import re
import os
from collections import OrderedDict

from cloudshell.shell.core.context.driver_context import AutoLoadResource
from cloudshell.shell.core.context.driver_context import AutoLoadAttribute
from cloudshell.shell.core.context.driver_context import AutoLoadDetails

from cloudshell.networking.cisco.resource_drivers_map import CISCO_RESOURCE_DRIVERS_MAP


def _is_table_value_exist(table, value, property):
    result = False
    if table and len(table) > 0:
        if value in table:
            if property in table[value]:
                result = True
    return result

def _get_table_value(table, value, property, value_type='str'):
    if _is_table_value_exist(table, value, property):
        if value_type == 'int':
            result = int(table[value][property].strip('\s'))
        else:
            result = table[value][property].strip('\s')
    else:
        if value_type == 'int':
            result = -2
        else:
            result = ''
    return result

def _is_list_valid(items_list):
    result = True
    if len(items_list) < 1:
        result = False
    return result

class CiscoGenericSNMPAutoload(object):
    @inject.params(snmp_handler='snmp_handler', logger='logger')
    def __init__(self, snmp_handler=None, logger=None):
        """Basic init with injected snmp handler and logger

        :param snmp_handler:
        :param logger:
        :return:
        """
        self.snmp = snmp_handler
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp.update_mib_sources(path)
        self._logger = logger

        local_mib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp.update_mib_sources(local_mib_path)
        self._load_snmp_tables()
        self.port_exclude_pattern = 'serial|stack|engine|management'
        self.resources = list()
        self.attributes = list()

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
        self._logger.info('IfDescr table loaded')

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
        self.port_mapping = self._get_mapping()

    def discover(self):
        """ Load device structure and attributes: chassis, modules, submodules, ports

        :return: formatted string
        """

        self.port_relative_address = []
        try:
            root_element = self.entity_table.filter_by_column('ParentRelPos', '-1')
            if len(root_element.keys()) > 0:
                device_id = root_element.keys()[0]
            else:
                root_element = self.entity_table.filter_by_column('ParentRelPos', '0')
                if len(root_element.keys()) > 0:
                    device_id = root_element.keys()[0]
                else:
                    self._logger.error("Device's root element not found")
                    return ''
        except Exception:
            self._logger.error("Entity table is inconsistent, entPhysicalParentRelPos is missing")
            # raise Exception('Cisco Autoload', "Device's root element not found")
            return ''
        self.chassis_list = self.entity_table.filter_by_column('Class', "'chassis'").sort_by_column(
            'ParentRelPos').keys()
        if not self._is_list_valid(self.chassis_list):
            self._logger.error('Entity table error, no chassis found')
            return ''
        port_list = self.get_port_list()
        self.module_list = []
        self.get_module_list(port_list)
        power_port_list = self.entity_table.filter_by_column('Class', "'powerSupply'").sort_by_column(
            'ParentRelPos').keys()
        self.chassis_list = self.entity_table.filter_by_column('Class', "'chassis'").sort_by_column(
            'ParentRelPos').keys()

        self._get_device_details()
        self._get_chassis_attributes(self.chassis_list)
        self._get_ports_attributes(port_list)
        self._get_module_attributes()
        self._get_power_ports(power_port_list)
        self._get_port_channels()

        result = AutoLoadDetails(resources=self.resources, attributes=self.attributes)
        return result

    def get_port_list(self):
        # ToDo take a look here
        """Read all ports from filtered entity mib table

        :return: filtered_port_list
         
        Builds and validates port name according to self.port_exclude_pattern
        :rtype: bool
        """
        filtered_port_list = []
        raw_port_list = self.entity_table.filter_by_column('Class', "'port'").sort_by_column('ParentRelPos').keys()
        for port in raw_port_list:
            if 'entPhysicalName' in self.entity_table[port] or 'entPhysicalDescr' in self.entity_table[port]:
                self._logger.error('entPhysicalName for port index {0} is not found'.format(port))
                if re.search(self.port_exclude_pattern, self.entity_table[port]['entPhysicalName']):
                    continue
                if re.search(self.port_exclude_pattern, self.entity_table[port]['entPhysicalDescr']):
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
        """
        Get Chassis element attributes
        :param chassis_list: list of chassis to load attributes for
        :return:
        """
        self._logger.info('Start loading Chassis')
        for chassis in chassis_list:
            chassis_id = self.entity_table[chassis]['entPhysicalParentRelPos']
            if chassis_id == '-1':
                chassis_id = '0'
            chassis_details_map = {
                'Model': _get_table_value(self.entity_table, 'entPhysicalModelName', chassis),
                'Serial Number': _get_table_value(self.entity_table, 'entPhysicalSerialNum', chassis)
            }
            if chassis_details_map['Model'] == '':
                chassis_details_map['Model'] = _get_table_value(self.entity_table, 'entPhysicalDescr', chassis)
            module_name = 'Chassis {0}'.format(chassis_id)
            relative_path = '{0}'.format(chassis_id)
            info_data = {'Name': module_name,
                         'Model': 'Generic Chassis',
                         'Relative Path': relative_path}
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
            if not _is_table_value_exist(self.entity_table, module, 'entPhysicalContainedIn'):
                continue
            parent_id = int(self.entity_table[module]['entPhysicalContainedIn'])
            if re.search('container', _get_table_value(self.entity_table, 'entPhysicalClass', parent_id)):
                module_id = _get_table_value(self.entity_table, parent_id, 'entPhysicalParentRelPos')
            else:
                module_id = _get_table_value(self.entity_table, module,
                                                  'entPhysicalParentRelPos')
                if module_id == '':
                    self._logger.error("Module id couldn't be retrieved from Entity-MIB")
                    module_id = self.module_list.index(module)
            try:
                relative_id = self._get_relative_path(module) + '/' + module_id
            except Exception as e:
                self._logger.error('Failed to build relative path for module {0}. Error: {1}'.format(module_id,
                                                                                                     e.message))
                continue
            if relative_id not in self.port_relative_address:
                continue
            module_details_map = {
                'Model': _get_table_value(self.entity_table, module, 'entPhysicalDescr'),
                'Version': _get_table_value(self.entity_table, module, 'entPhysicalSoftwareRev'),
                'Serial Number': _get_table_value(self.entity_table, module, 'entPhysicalSerialNum')
            }
            model = 'Generic Sub Module'
            if '/' in relative_id and len(relative_id.split('/')) < 3:
                module_name = 'Module {0}'.format(module_id)
                model = 'Generic Module'
            else:
                module_name = 'Sub Module {0}'.format(module_id)
            info_data = {'Name': module_name,
                         'Model': model,
                         'Relative Path': relative_id}
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
            if port not in self.entity_table:
                continue
            module_name = _get_table_value(self.entity_table, port, 'entPhysicalName')
            port_id = _get_table_value(self.entity_table, port, 'entPhysicalParentRelPos', 'int')
            if port_id == -2:
                continue
            try:
                relative_path = '{0}/PP{1}'.format(self._get_relative_path(port), port_id)
            except Exception as e:
                self._logger.error('Failed to build relative path for power port {0}. Error: {1}'.format(port_id,
                                                                                                         e.message))
                continue
            chassis_details = {'Model': _get_table_value(self.entity_table, port, 'entPhysicalModelName'),
                               'Port Description': _get_table_value(self.entity_table, port, 'entPhysicalDescr'),
                               'Version': _get_table_value(self.entity_table, port, 'entPhysicalHardwareRev'),
                               'Serial Number': _get_table_value(self.entity_table, port, 'entPhysicalSerialNum')
                               }
            info_data = {'Name': 'PP{0}'.format(relative_path.replace('/', '-').replace('PP', '')),
                         'Relative Path': relative_path,
                         'Model': 'Generic Power Port'}

            self._add_resources_data(info_data)
            self._add_attributes_data(relative_path, chassis_details)
            self._logger.info('Added ' + module_name.strip('\s') + ' Power Port')
        self._logger.info('Finished Loading Power Ports')

    def _get_port_channels(self):
        """Get all port channels and set attributes for them

        :return:
        """
        if not self.if_table:
            return
        port_channel_dic = {index: port for index, port in self.if_table.iteritems()
                            if 'ifDescr' in self.if_table[port] and 'channel' in port['ifDescr']}
        self._logger.info('Start loading Port Channels')
        for key, value in port_channel_dic.iteritems():
            interface_model = value['ifDescr']
            match_object = re.search('\d+$', interface_model)
            if match_object:
                interface_id = 'PC{0}'.format(match_object.group(0))
            else:
                self._logger.error('Adding of {0} failed. Name is invalid'.format(interface_model))
                continue
            attribute_map = {'Protocol Type': 'Transparent',
                             'Port Description': _get_table_value(self.if_x_table, key, 'ifAlias'),
                             'Associated Ports': self._get_associated_ports(key)}
            attribute_map.update(self._get_ip_interface_details(key))
            info_data = {'Model': 'Generic Port Channel',
                         'Name': interface_model,
                         'Relative Path': interface_id}
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
            if self.port_mapping[port] not in self.if_table:
                continue
            interface_model = 'Generic Port'
            if_table_port_attr = {'ifType': 'str', 'ifPhysAddress': 'str', 'ifMtu': 'int', 'ifSpeed': 'int'}
            if_table = self.if_table[self.port_mapping[port]].copy()
            if_table.update(self.snmp.get_bulk_values('IF-MIB', self.port_mapping[port], if_table_port_attr))
            interface_name = _get_table_value(self.if_table, self.port_mapping[port], 'ifDescr')
            if interface_name == '':
                interface_name = _get_table_value(self.entity_table, port, 'entPhysicalName')
            if interface_name == '':
                continue
            datamodel_interface_name = interface_name.replace('/', '-').replace('\s+', '')
            parent_id = _get_table_value(self.entity_table, port, 'entPhysicalContainedIn', value_type='int')
            interface_id = _get_table_value(self.entity_table, port, 'entPhysicalParentRelPos')
            if interface_id == '':
                port_id_match_data = re.search('\d+$', interface_name)
                if port_id_match_data:
                    interface_id = port_id_match_data.group()
                else:
                    continue
            if 'container' in self.entity_table[parent_id]['entPhysicalClass'].lower():
                interface_id = self.entity_table[parent_id]['entPhysicalParentRelPos']
            try:
                relative_id = self._get_relative_path(port)
            except Exception as e:
                self._logger.error(
                    'Failed to build relative path for port {0}. Error: {1}'.format(interface_id, e.message))
                continue
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
            info_data = {'Model': interface_model,
                         'Name': '{0}'.format(datamodel_interface_name),
                         'Relative Path': relative_path}
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
        if self.ip_v4_table and len(self.ip_v4_table) > 1:
            for key, value in self.ip_v4_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == port_index:
                    interface_details['IPv4 Address'] = key
                break
        if self.ip_v6_table and len(self.ip_v6_table) > 1:
            for key, value in self.ip_v6_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == port_index:
                    interface_details['IPv6 Address'] = key
                break
        return interface_details

    def _get_interface_details(self, port_index):
        """Get interface attributes

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'Auto Negotiation': '', 'Duplex': ''}
        """
        interface_details = {'Duplex': 'Full', 'Auto Negotiation': 'False'}
        try:
            auto_negotiation = self.snmp.get(('MAU-MIB', 'ifMauAutoNegAdminStatus', '{0}'.format(port_index),
                                              '1')).values()[0].replace("'", '')
            if auto_negotiation and auto_negotiation == 'enabled':
                interface_details['Auto Negotiation'] = 'True'
        except Exception as e:
            self._logger.error('Failed to load auto negotiation property for interface ')
        for key, value in self.duplex_table.iteritems():
            if 'dot3StatsIndex' in value.keys() and value['dot3StatsIndex'] == str(port_index):
                interface_duplex = self.snmp.get_property_value('EtherLike-MIB', 'dot3StatsDuplexStatus', key)
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

    def _get_device_details(self):
        self._logger.info('Start loading Switch Attributes')
        result = {'Nendor': 'Cisco',
                  'System Name': self.snmp.get_property_value('SNMPv2-MIB', 'sysName', 0),
                  'Model': '',
                  'Location': self.snmp.get_property_value('SNMPv2-MIB', 'sysLocation', 0),
                  'Contact': self.snmp.get_property_value('SNMPv2-MIB', 'sysContact', 0),
                  'OS Version': ''}

        match_version = re.search('\S\s*\((?P<firmware>\S+)\)\S\s*Version\s+(?P<software_version>\S+)\S*\s+',
                                  self.snmp.get_property_value('SNMPv2-MIB', 'sysDescr', 0))
        if match_version:
            result['OS Version'] = match_version.groupdict()['software_version'].replace(',', '')

        result.update(self._get_device_model_and_vendor())

        self._logger.info('Finished Loading Switch Attributes')

        self._add_attributes_data('', result)

    def _get_adjacent(self, interface_id):
        result = ''
        for key, value in self.cdp_table.iteritems():
            if 'cdpCacheDeviceId' in value and 'cdpCacheDevicePort' in value:
                if re.search('^\d+', str(key)).group(0) == self.port_mapping[interface_id]:
                    result = '{0} through {1}'.format(value['cdpCacheDeviceId'], value['cdpCacheDevicePort'])
        if result == '' and self.lldp_remote_table:
            for key, value in self.lldp_local_table.iteritems():
                interface_name = _get_table_value(self.if_table, self.port_mapping[interface_id], 'ifDescr')
                if interface_name == '':
                    break
                if 'lldpLocPortDesc' in value and interface_name in value['lldpLocPortDesc']:
                    if 'lldpRemSysName' in self.lldp_remote_table and 'lldpRemPortDesc' in self.lldp_remote_table:
                        result = '{0} through {1}'.format(self.lldp_remote_table[key]['lldpRemSysName'],
                                                          self.lldp_remote_table[key]['lldpRemPortDesc'])
        return result

    def _get_device_model_and_vendor(self):
        result = {'Vendor': 'Cisco', 'Model': ''}
        match_name = re.search(r'^SNMPv2-SMI::enterprises\.(?P<vendor>\d+)(\.\d)+\.(?P<model>\d+$)',
                               self.snmp.get_property_value('SNMPv2-MIB', 'sysObjectID', 0))
        if match_name is None:
            match_name = re.search(r'1\.3\.6\.1\.4\.1\.(?P<vendor>\d+)(\.\d)+\.(?P<model>\d+$)',
                                   self.snmp.get_property_value('SNMPv2-MIB', 'sysObjectID', 0))
            if match_name is None:
                match_name = re.search(r'^(?P<vendor>\w+)-SMI::cisco(Products|Modules)\S*\.(?P<model>\d+)$',
                                       self.snmp.get_property_value('SNMPv2-MIB', 'sysObjectID', 0))

        if match_name:
            model = match_name.groupdict()['model']
            if model in CISCO_RESOURCE_DRIVERS_MAP:
                result['Model'] = CISCO_RESOURCE_DRIVERS_MAP[model].lower().replace('_', '').capitalize()
        if not result['Model'] or result['Model'] == '':
            self.snmp.load_mib('CISCO-PRODUCTS-MIB')
            match_name = re.search(r'^(?P<vendor>\S+)-P\S*\s*::(?P<model>\S+$)',
                                   self.snmp.get_property_value('SNMPv2-MIB', 'sysObjectID', '0'))
            if match_name:
                result['Vendor'] = match_name.groupdict()['vendor'].capitalize()
                result['Model'] = match_name.groupdict()['model'].capitalize()
        return result

    def _get_mapping(self):
        """ Get mapping from entPhysicalTable to ifTable.
        Build mapping based on ent_alias_mapping_table if exists else build manually based on
        entPhysicalDescr <-> ifDescr mapping.

        :return: simple mapping from entPhysicalTable index to ifTable index:
        |        {entPhysicalTable index: ifTable index, ...}
        """

        mapping = OrderedDict()
        ent_alias_mapping_table = self.snmp.get_table(('ENTITY-MIB', 'entAliasMappingIdentifier'))
        if len(ent_alias_mapping_table) > 1:
            for port in self.entity_table.filter_by_column('Class', "'port'"):
                if port in ent_alias_mapping_table.keys():
                    ent_alias_mapping_identifier = ent_alias_mapping_table[port]['entAliasMappingIdentifier']
                    port_id = int(ent_alias_mapping_identifier.split('.')[-1])
                    if port_id in self.if_table:
                        mapping[port] = port_id
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
