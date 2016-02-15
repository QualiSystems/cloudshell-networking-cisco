__author__ = 'coye'

import re
import os
from collections import OrderedDict

from cloudshell.networking.cisco.cisco_autoload.resource import Resource
from cloudshell.networking.cisco.resource_drivers_map import CISCO_RESOURCE_DRIVERS_MAP

class CiscoGenericSNMPAutoload(object):
    def __init__(self, snmp_handler, logger):
        self.snmp = snmp_handler
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'mibs'))
        self.snmp.update_mib_sources(path)
        self._logger = logger
        self._load_snmp_tables()
        self.resource = None

    def _load_snmp_tables(self):

        self._logger.info('Start loading MIB tables:')
        self.entity_table = self.snmp.get_table('ENTITY-MIB', 'entPhysicalTable')
        self._logger.info('Entity table loaded')

        self.if_table = self.snmp.get_table('IF-MIB', 'ifTable')
        self._logger.info('IfTable loaded')

        self.snmp_mib = self.snmp.get_table('SNMPv2-MIB', 'system')
        self.lldp_local_table = self.snmp.get_table('LLDP-MIB', 'lldpLocPortDesc')
        self.lldp_remote_table = self.snmp.get_table('LLDP-MIB', 'lldpRemTable')
        self.cdp_index_table = self.snmp.get_table('CISCO-CDP-MIB', 'cdpInterface')
        self.cdp_table = self.snmp.get_table('CISCO-CDP-MIB', 'cdpCacheTable')
        self.duplex_table = self.snmp.get_table('EtherLike-MIB', 'dot3StatsTable')
        self.ip_v4_table = self.snmp.get_table('IP-MIB', 'ipAddrTable')
        self.ip_v6_table = self.snmp.get_table('IPV6-MIB', 'ipv6AddrEntry')
        self.if_x_table = self.snmp.get_table('IF-MIB', 'ifAlias')
        self.port_channel_ports = self.snmp.get_table('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID')

        self._logger.info('MIB Tables loaded successfully')
        self.port_mapping = self.get_mapping()

    def discover(self):
        """
        Loads device structure - chassis, modules, submodules, ports. And attributes for them
        :return: formatted string to
        """
        self.port_relative_address = []
        self.resource = Resource()
        device_id = self.entity_table.filter_by_column('ParentRelPos', '-1').keys()[0]
        port_list = self.entity_table.filter_by_column('Class', "'port'").sort_by_column('ParentRelPos').keys()
        self.module_list = self.entity_table.filter_by_column('Class', "'module'").sort_by_column('ParentRelPos').keys()
        power_port_list = self.entity_table.filter_by_column('Class', "'powerSupply'").sort_by_column('ParentRelPos').keys()
        self.chassis_list = self.entity_table.filter_by_column('Class', "'chassis'").sort_by_column('ParentRelPos').keys()
        info_data = {'attributes': self._get_device_details(device_id),
                     'relative_path': ''}
        self.resource.addChild('', '/', info_data)
        self._get_chassis_attributes(self.chassis_list)
        self._get_ports_attributes(port_list)
        self._get_module_attributes()
        self._get_power_ports(power_port_list)

        self._get_port_channels()

        resource_to_str = self.resource.toString()
        self._logger.info('*******************************************')
        self._logger.info('Resource details:')

        for table in resource_to_str.split('$'):
            self._logger.info('------------------------------')
            for line in table.split('|'):
                self._logger.info(line.replace('^', '\t\t'))

        self._logger.info('*******************************************')

        return resource_to_str

    def _get_chassis_attributes(self, chassis_list):
        '''Get Chassis element attributes

        :param chassis_list: list of chassis to load attributes for
        :return:
        '''
        self._logger.info('Start loading Chassis')
        for chassis in chassis_list:
            chassis_id = chassis_list.index(chassis)
            chassis_details_map = {
                'model': self.entity_table[chassis]['entPhysicalModelName'],
                'serial_number': self.entity_table[chassis]['entPhysicalSerialNum']
            }
            module_name = 'Chassis {0}'.format(chassis_id)
            relative_path = '{0}'.format(chassis_id)
            info_data = {'name': module_name,
                         'attributes': chassis_details_map,
                         'model': 'Generic Chassis',
                         'relative_path': relative_path}
            self.resource.addChild(relative_path, '/', info_data)
            self._logger.info('Added ' + self.entity_table[chassis]['entPhysicalDescr'] + ' Module')
        self._logger.info('Finished Loading Modules')

    def _get_module_attributes(self):
        self._logger.info('Start loading Modules')
        for module in self.module_list:
            if 'MODULE' not in self.entity_table[module]['entPhysicalName'].upper():
                continue
            module_id = str(self.module_list.index(module))
            relative_id = self._get_relative_path(module) + '/' + module_id
            if relative_id not in self.port_relative_address:
                continue
            module_details_map = {
                'model': self.entity_table[module]['entPhysicalDescr'] or '',
                'software_version': self.entity_table[module]['entPhysicalSoftwareRev'] or '',
                'serial_number': self.entity_table[module]['entPhysicalSerialNum'] or ''
            }
            model = 'Generic Sub Module'
            if '/' in relative_id and len(relative_id.split('/')) < 3:
                module_name = 'Module {0}'.format(module_id)
                model = 'Generic Module'
            else:
                module_name = 'Sub Module {0}'.format(module_id)
            info_data = {'name': module_name,
                         'attributes': module_details_map,
                         'model': model,
                         'relative_path': relative_id}
            self.resource.addChild(relative_id, '/', info_data)
            self._logger.info('Added ' + self.entity_table[module]['entPhysicalDescr'] + ' Module')
        self._logger.info('Finished Loading Modules')

    def _get_power_ports(self, power_ports):
        self._logger.info('Start loading Power Ports')
        for port in power_ports:
            module_name = self.entity_table[port]['entPhysicalName']
            relative_path = '{0}/PP{1}'.format(self._get_relative_path(port), power_ports.index(port))
            chassis_details_map = {'model': self.entity_table[port]['entPhysicalModelName'].strip(' \t\n\r'),
                                   'description': self.entity_table[port]['entPhysicalDescr'],
                                   'version': self.entity_table[port]['entPhysicalHardwareRev'],
                                   'serial_number': self.entity_table[port]['entPhysicalSerialNum']}
            info_data = {'name': 'PP{0}'.format(relative_path.replace('/', '-').replace('PP', '')),
                         'attributes': chassis_details_map,
                         'model': 'Generic Power Port',
                         'relative_path': relative_path}
            self.resource.addChild(relative_path, '/', info_data)
            self._logger.info('Added ' + module_name.strip(' \t\n\r') + ' Power Port')
        self._logger.info('Finished Loading Power Ports')

    def _get_port_channels(self):
        port_channel_dic = {index: port for index, port in self.if_table.iteritems() if 'channel' in port['ifDescr']}
        self._logger.info('Start loading Port Channels')
        for key, value in port_channel_dic.iteritems():
            interface_model = value['ifDescr']
            interface_id = str(len(self.chassis_list) + (port_channel_dic.keys().index(key)))
            match_object = re.search('\d+$', interface_model)
            if match_object:
                interface_name = match_object.group(0)
            else:
                interface_name = interface_id

            attribute_map = {'protocol_type': 'Transparent', 'description': self.if_x_table[key]['ifAlias'],
                             'associated_ports': self._get_associated_ports(key)}
            attribute_map.update(self._get_ip_interface_details(key))
            info_data = {'model': 'Generic Port Channel',
                         'name': 'PC{0}'.format(interface_name),
                         'relative_path': interface_id,
                         'attributes': attribute_map}
            self.resource.addChild(interface_id, '/', info_data)
            self._logger.info('Added ' + interface_model + ' Port Channel')
        self._logger.info('Finished Loading Port Channels')

    def _get_associated_ports(self, item_id):
        result = ''
        for key, value in self.port_channel_ports.iteritems():
            if str(item_id) in value['dot3adAggPortAttachedAggID']:
                result += self.if_table[key]['ifDescr'].replace('/', '-').replace(' ', '') + '; '
        return result

    def _get_ports_attributes(self, ports):
        '''Get port attributes for porovided list of ports

        :param ports: list of ports to fill attributes
        :return:
        '''
        self._logger.info('Start loading Ports')
        for port in ports:
            if 'serial' in self.entity_table[port]['entPhysicalName']:
                continue
            interface_model = 'Generic Port'
            interface_name = self.if_table[self.port_mapping[port]]['ifDescr']
            datamodel_interface_name = interface_name.replace('/', '-').replace('\s+', '')
            relative_id = self._get_relative_path(port)
            interface_id = relative_id + '/{0}'.format(ports.index(port))
            attribute_map = {'l2_protocol_type':
                                 self.if_table[self.port_mapping[port]]['ifType'].replace('/', '').replace("'", ''),
                             'mac': self.if_table[self.port_mapping[port]]['ifPhysAddress'],
                             'mtu': self.if_table[self.port_mapping[port]]['ifMtu'],
                             'bandwidth': self.if_table[self.port_mapping[port]]['ifSpeed'],
                             'description': self.if_x_table[self.port_mapping[port]]['ifAlias'],
                             'adjacent': self._get_adjacent(port),
                             'protocol_type': 'Transparent'}
            #device_attributes.update(self.if_table[self.port_mapping[port]])
            #device_attributes.update(self.if_x_table[self.port_mapping[port]])
            attribute_map.update(self._get_interface_details(self.port_mapping[port]))
            attribute_map.update(self._get_ip_interface_details(self.port_mapping[port]))
            #attribute_map = getDictionaryData(device_attributes, ['entPhysicalDescr'])
            #attribute_map.update(getDictionaryData(device_attributes, ['entPhysicalName']))
            info_data = {'model': interface_model,
                         'name': '{0}'.format(datamodel_interface_name),
                         'relative_path': interface_id,
                         'attributes': attribute_map}
            self.resource.addChild(interface_id, '/', info_data)
            self.port_relative_address.append(relative_id)
            self._logger.info('Added ' + interface_name + ' Port')
        self._logger.info('Finished Loading Ports')

    def _get_relative_path(self, item_id):
        return self.__get_relative_path(item_id)[::-1]

    def __get_relative_path(self, item_id):
        parent = int(self.entity_table[item_id]['entPhysicalContainedIn'])
        if parent in self.module_list:
            result = str(self.module_list.index(parent)) + '/'
            result += self._get_relative_path(parent)
        elif parent in self.chassis_list:
            result = str(self.chassis_list.index(parent))
        else:
            result = self._get_relative_path(parent)
        return result

    def _get_ip_interface_details(self, index):
        interface_details = {'port_ip_v4': '', 'port_ip_v6': ''}
        for key, value in self.ip_v4_table.iteritems():
            if int(value['ipAdEntIfIndex']) == index:
                interface_details['port_ip'] = key
                break
        for key, value in self.ip_v6_table.iteritems():
            if int(value['ipAdEntIfIndex']) == index:
                interface_details['port_ip'] = key
                break
        return interface_details

    def _get_interface_details(self, index):
        interface_details = {'duplex': 'Full', 'auto_negotiation': 'False'}
        auto_negotiation = self.snmp.get(('MAU-MIB', 'ifMauAutoNegAdminStatus',
                                          '{0}'.format(index), '1')).values()[0].replace("'", '')
        if auto_negotiation and auto_negotiation == 'enabled':
            interface_details['auto_negotiation'] = 'True'
        for key, value in self.duplex_table.iteritems():
            if value['dot3StatsIndex'] == str(index) and 'dot3StatsDuplexStatus' in value.keys():
                if 'halfDuplex' in value['dot3StatsDuplexStatus']:
                    interface_details['duplex'] = 'Half'
        return interface_details

    def _get_device_details(self, index):
        self._logger.info('Start loading Switch Attributes')
        result = {'vendor': 'Cisco',
                  'system_name': self.snmp_mib[0]['sysName'],
                  'pid': self.entity_table[index]['entPhysicalHardwareRev'],
                  'model': '',
                  'location': self.snmp_mib[0]['sysLocation'],
                  'contact': self.snmp_mib[0]['sysContact'],
                  'os_version': '',
                  'firmware': ''}

        match_version = re.search('\S\s*\((?P<firmware>\S+)\)\S\s*Version\s+(?P<software_version>\S+)\S*\s+',
                                 self.snmp_mib[0]['sysDescr'])
        if match_version:
            result['os_version'] = match_version.groupdict()['software_version'].replace(',', '')
            result['firmware'] = match_version.groupdict()['firmware']

        result.update(self._get_device_model_and_vendor())

        self._logger.info('Finished Loading Switch Attributes')
        return result

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
        result = {'vendor': 'Cisco', 'model': ''}
        match_name = re.search(r'^SNMPv2-SMI::enterprises\.(?P<vendor>\d+)(\.\d)+\.(?P<model>\d+$)',
                               self.snmp_mib[0]['sysObjectID'])
        if match_name is None:
            match_name = re.search(r'1\.3\.6\.1\.4\.1\.(?P<vendor>\d+)(\.\d)+\.(?P<model>\d+$)',
                                   self.snmp_mib[0]['sysObjectID'])
            if match_name is None:

                match_name = re.search(r'^(?P<vendor>\w+)-SMI::ciscoProducts\.(?P<model>\d+)$',
                               self.snmp_mib[0]['sysObjectID'])

        if match_name:
            vendor = match_name.groupdict()['vendor'].capitalize()
            model = match_name.groupdict()['model']
            if vendor and vendor in CISCO_RESOURCE_DRIVERS_MAP:
                if model in CISCO_RESOURCE_DRIVERS_MAP[vendor]:
                    result['model'] = CISCO_RESOURCE_DRIVERS_MAP[vendor][model].lower().replace('_', '').capitalize()
            elif vendor.upper() == result['vendor'].upper():
                if model in CISCO_RESOURCE_DRIVERS_MAP['9']:
                    result['model'] = CISCO_RESOURCE_DRIVERS_MAP['9'][model].lower().replace('_', '').capitalize()
            if not result['model'] or result['model'] == '':
                    self.snmp.load_mib('CISCO-PRODUCTS-MIB')
                    match_name = re.search(r'^(?P<vendor>\S+)-P\S*\s*::(?P<model>\S+$)',
                                           self.snmp.get(('SNMPv2-MIB', 'sysObjectID', '0')).values()[0])
                    if match_name:
                        result['vendor'] = match_name.groupdict()['vendor'].capitalize()
                        result['model'] = match_name.groupdict()['model'].capitalize()
        return result

    def get_mapping(self):
        """ Get mapping from entPhysicalTable to ifTable.

        Build mapping based on entAliasMappingTable if exists else build manually based on
        entPhysicalDescr <-> ifDescr mapping.

        :return: simple mapping from entPhysicalTable index to ifTable index:
        |        {entPhysicalTable index: ifTable index, ...}
        """

        mapping = OrderedDict()
        entAliasMappingTable = self.snmp.walk(('ENTITY-MIB', 'entAliasMappingTable'))
        if entAliasMappingTable:
            for port in self.entity_table.filter_by_column('Class', "'port'"):
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
            ifTable_re = '.*' + module_index + '/' + port_index
            for interface in self.if_table.values():
                if re.search(ifTable_re, interface['ifDescr']):
                    mapping[int(port['suffix'])] = int(interface['suffix'])
                    continue
        return mapping