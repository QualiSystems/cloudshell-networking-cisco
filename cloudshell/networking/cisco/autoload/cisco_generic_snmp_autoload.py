#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os

from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.standards.networking.autoload_structure import *
from cloudshell.snmp.quali_snmp import QualiMibTable


class CiscoGenericSNMPAutoload(object):
    IF_ENTITY = "ifDescr"
    ENTITY_PHYSICAL = "entPhysicalDescr"

    def __init__(self, snmp_handler, shell_name, shell_type, resource_name, logger):
        """Basic init with injected snmp handler and logger

        :param snmp_handler:
        :param logger:
        :return:
        """

        self.snmp_handler = snmp_handler
        self.shell_name = shell_name
        self.shell_type = shell_type
        self.resource_name = resource_name
        self.logger = logger
        self.exclusion_list = []
        self._excluded_models = []
        self.module_list = []
        self.chassis_list = []
        self.port_list = []
        self.power_supply_list = []
        self.relative_address = {}
        self.port_mapping = {}
        self.entity_table_black_list = ["alarm", "fan", "sensor"]
        self.port_exclude_pattern = r"stack|engine|management|mgmt|voice|foreign|cpu"
        self.module_exclude_pattern = r"cevsfp"

        self.elements = {}
        self.resource = GenericResource(shell_name=shell_name,
                                        shell_type=shell_type,
                                        name=resource_name,
                                        unique_id=resource_name)

    def load_cisco_mib(self):
        """
        Loads Cisco specific mibs inside snmp handler

        """
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mibs"))
        self.snmp_handler.update_mib_sources(path)

    def discover(self, supported_os):
        """General entry point for autoload,
        read device structure and attributes: chassis, modules, submodules, ports, port-channels and power supplies

        :return: AutoLoadDetails object
        """

        if not self._is_valid_device_os(supported_os):
            raise Exception(self.__class__.__name__, 'Unsupported device OS')

        self.logger.info("*" * 70)
        self.logger.info("Start SNMP discovery process .....")

        self.load_cisco_mib()
        self.snmp_handler.load_mib(["CISCO-PRODUCTS-MIB", "CISCO-ENTITY-VENDORTYPE-OID-MIB"])
        self._get_device_details()
        self._load_snmp_tables()

        if self.chassis_list:
            for chassis in self.chassis_list:
                if chassis not in self.exclusion_list:
                    chassis_id = self._get_resource_id(chassis)
                    if chassis_id == "-1":
                        chassis_id = "0"
                    self.relative_address[chassis] = chassis_id
    
            self._filter_lower_bay_containers()
            self._get_module_list()
            self._add_relative_addresss()
            self._get_chassis_attributes()
            self._get_power_ports()
            self._get_module_attributes()
            self._get_ports_attributes()

            self._get_port_channels()
        else:
            self.logger.error("Entity table error, no chassis found")

        autoload_details = AutoloadDetailsBuilder(self.resource).autoload_details()
        self._log_autoload_details(autoload_details)
        return autoload_details

    def _log_autoload_details(self, autoload_details):
        """
        Logging autoload details
        :param autoload_details:
        :return:
        """
        self.logger.debug("-------------------- <RESOURCES> ----------------------")
        for resource in autoload_details.resources:
            self.logger.debug(
                "{0:15}, {1:20}, {2}".format(resource.relative_address, resource.name, resource.unique_identifier))
        self.logger.debug("-------------------- </RESOURCES> ----------------------")

        self.logger.debug("-------------------- <ATTRIBUTES> ---------------------")
        for attribute in autoload_details.attributes:
            self.logger.debug("-- {0:15}, {1:60}, {2}".format(attribute.relative_address, attribute.attribute_name,
                                                              attribute.attribute_value))
        self.logger.debug("-------------------- </ATTRIBUTES> ---------------------")

    def _is_valid_device_os(self, supported_os):
        """Validate device OS using snmp
            :return: True or False
        """

        system_description = self.snmp_handler.get_property('SNMPv2-MIB', 'sysDescr', '0')
        self.logger.debug('Detected system description: \'{0}\''.format(system_description))
        result = re.search(r"({0})".format("|".join(supported_os)),
                           system_description,
                           flags=re.DOTALL | re.IGNORECASE)

        if result:
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for \'{0}\' operation system(s)'. \
                format(str(tuple(supported_os)))
            self.logger.error(error_message)
            return False

    def _get_device_model(self):
        """Get device model form snmp SNMPv2 mib

        :return: device model
        :rtype: str
        """

        result = ''
        match_name = re.search(r'::(?P<model>\S+$)', self.snmp_handler.get_property('SNMPv2-MIB', 'sysObjectID', '0'))
        if match_name:
            result = match_name.groupdict()['model'].capitalize()
        return result

    def _get_device_os_version(self):
        """Get device OS Version form snmp SNMPv2 mib

        :return: device model
        :rtype: str
        """

        result = ""
        matched = re.search(r"Version (?P<os_version>.*?),",
                            self.snmp_handler.get_property('SNMPv2-MIB', 'sysDescr', '0'))
        if matched:
            result = matched.groupdict().get("os_version", "")
        return result

    def _get_device_details(self):
        """ Get root element attributes """

        self.logger.info("Building Root")
        vendor = "Cisco"

        self.resource.contact_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysContact', '0')
        self.resource.system_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysName', '0')
        self.resource.location = self.snmp_handler.get_property('SNMPv2-MIB', 'sysLocation', '0')
        self.resource.os_version = self._get_device_os_version()
        self.resource.model = self._get_device_model()
        self.resource.vendor = vendor

    def _load_snmp_tables(self):
        """ Load all cisco required snmp tables

        :return:
        """

        self.logger.info('Start loading MIB tables:')
        self.if_table = self.snmp_handler.get_table('IF-MIB', self.IF_ENTITY)
        self.logger.info('{0} table loaded'.format(self.IF_ENTITY))
        self.entity_table = self._get_entity_table()
        if len(self.entity_table.keys()) < 1:
            raise Exception('Cannot load entPhysicalTable. Autoload cannot continue')
        self.logger.info('Entity table loaded')

        self.lldp_remote_table = self.snmp_handler.get_table('LLDP-MIB', 'lldpRemSysName')
        self.lldp_local_table = dict()
        lldp_local_table = self.snmp_handler.get_table('LLDP-MIB', 'lldpLocPortDesc')
        if lldp_local_table:
            self.lldp_local_table = dict([(v['lldpLocPortDesc'].lower(), k) for k, v in lldp_local_table.iteritems()])
        self.cdp_table = self.snmp_handler.get_table('CISCO-CDP-MIB', 'cdpCacheDeviceId')
        self.duplex_table = self.snmp_handler.get_table('EtherLike-MIB', 'dot3StatsIndex')
        self.ip_v4_table = self.snmp_handler.get_table('IP-MIB', 'ipAddrTable')
        self.ip_v6_table = self.snmp_handler.get_table('IPV6-MIB', 'ipv6AddrEntry')
        self.port_channel_ports = self.snmp_handler.get_table('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID')

        self.logger.info('MIB Tables loaded successfully')

    def _get_entity_table(self):
        """Read Entity-MIB and filter out device's structure and all it's elements, like ports, modules, chassis, etc.

        :rtype: QualiMibTable
        :return: structured and filtered EntityPhysical table.
        """

        result_dict = QualiMibTable('entPhysicalTable')

        entity_table_critical_port_attr = {'entPhysicalContainedIn': 'str', 'entPhysicalClass': 'str',
                                           'entPhysicalVendorType': 'str'}
        entity_table_optional_port_attr = {'entPhysicalDescr': 'str', 'entPhysicalName': 'str'}

        physical_indexes = self.snmp_handler.get_table('ENTITY-MIB', 'entPhysicalParentRelPos')
        for index in physical_indexes.keys():
            is_excluded = False
            if physical_indexes[index]['entPhysicalParentRelPos'] == '':
                self.exclusion_list.append(index)
                continue
            temp_entity_table = physical_indexes[index].copy()
            temp_entity_table.update(self.snmp_handler.get_properties('ENTITY-MIB', index, entity_table_critical_port_attr)
                                     [index])
            if temp_entity_table['entPhysicalContainedIn'] == '':
                is_excluded = True
                self.exclusion_list.append(index)

            for item in self.entity_table_black_list:
                if item in temp_entity_table['entPhysicalVendorType'].lower():
                    is_excluded = True
                    break

            if is_excluded is True:
                continue

            temp_entity_table.update(self.snmp_handler.get_properties('ENTITY-MIB', index, entity_table_optional_port_attr)
                                     [index])

            if temp_entity_table['entPhysicalClass'] == '':
                vendor_type = self.snmp_handler.get_property('ENTITY-MIB', 'entPhysicalVendorType', index)
                index_entity_class = None
                if vendor_type == '':
                    continue
                if 'cevcontainer' in vendor_type.lower():
                    index_entity_class = 'container'
                elif 'cevchassis' in vendor_type.lower():
                    index_entity_class = 'chassis'
                elif 'cevmodule' in vendor_type.lower():
                    index_entity_class = 'module'
                elif 'cevport' in vendor_type.lower():
                    index_entity_class = 'port'
                elif 'cevpowersupply' in vendor_type.lower():
                    index_entity_class = 'powerSupply'
                if index_entity_class:
                    temp_entity_table['entPhysicalClass'] = index_entity_class
            elif 'powershelf' in temp_entity_table['entPhysicalVendorType'].lower():
                temp_entity_table['entPhysicalClass'] = 'container'
            else:
                temp_entity_table['entPhysicalClass'] = temp_entity_table['entPhysicalClass'].replace("'", "")

            if re.search(r'stack|chassis|module|port|powerSupply|container|backplane',
                         temp_entity_table['entPhysicalClass']):
                result_dict[index] = temp_entity_table

            if temp_entity_table['entPhysicalClass'] == 'chassis':
                self.chassis_list.append(index)
            elif temp_entity_table['entPhysicalClass'] == 'port':
                if not re.search(self.port_exclude_pattern, temp_entity_table['entPhysicalName'], re.IGNORECASE) \
                        and not re.search(self.port_exclude_pattern, temp_entity_table['entPhysicalDescr'],
                                          re.IGNORECASE):
                    port_id = self._get_mapping(index, temp_entity_table[self.ENTITY_PHYSICAL])
                    if port_id and port_id in self.if_table and port_id not in self.port_mapping.values():
                        self.port_mapping[index] = port_id
                        self.port_list.append(index)
            elif temp_entity_table['entPhysicalClass'] == 'powerSupply':
                self.power_supply_list.append(index)

        self._filter_entity_table(result_dict)
        return result_dict

    def _filter_lower_bay_containers(self):
        """
        Filter rare cases when device have multiple bays with separate containers in each bay

        """
        upper_container = None
        lower_container = None
        containers = self.entity_table.filter_by_column('Class', "container").sort_by_column('ParentRelPos').keys()
        for container in containers:
            vendor_type = self.snmp_handler.get_property('ENTITY-MIB', 'entPhysicalVendorType', container)
            if 'uppermodulebay' in vendor_type.lower():
                upper_container = container
            if 'lowermodulebay' in vendor_type.lower():
                lower_container = container
        if lower_container and upper_container:
            child_upper_items_len = len(self.entity_table.filter_by_column('ContainedIn', str(upper_container)
                                                                           ).sort_by_column('ParentRelPos').keys())
            child_lower_items = self.entity_table.filter_by_column('ContainedIn', str(lower_container)
                                                                   ).sort_by_column('ParentRelPos').keys()
            for child in child_lower_items:
                self.entity_table[child]['entPhysicalContainedIn'] = upper_container
                self.entity_table[child]['entPhysicalParentRelPos'] = str(child_upper_items_len + int(
                    self.entity_table[child]['entPhysicalParentRelPos']))

    def _add_relative_addresss(self):
        """Build dictionary of relative paths for each module and port

        :return:
        """

        port_list = list(self.port_list)
        module_list = list(self.module_list)
        for module in module_list:
            if module not in self.exclusion_list:
                self.relative_address[module] = self.get_relative_address(module) + '/' + self._get_resource_id(module)
            else:
                self.module_list.remove(module)
        for port in port_list:
            if port not in self.exclusion_list:
                self.relative_address[port] = self._get_port_relative_address(
                    self.get_relative_address(port) + '/' + self._get_resource_id(port))
            else:
                self.port_list.remove(port)

    def _get_port_relative_address(self, relative_id):
        """
        Workaround for an issue when port and sub-module located on the same module and have same relative ids

        :param relative_id:
        :return: relative_address
        """
        if relative_id in self.relative_address.values():
            if '/' in relative_id:
                ids = relative_id.split('/')
                ids[-1] = str(int(ids[-1]) + 1000)
                result = '/'.join(ids)
            else:
                result = str(int(relative_id.split()[-1]) + 1000)
            if relative_id in self.relative_address.values():
                result = self._get_port_relative_address(result)
        else:
            result = relative_id
        return result

    def _add_element(self, relative_path, resource, parent_id=""):
        """Add object data to resources and attributes lists

        :param resource: object which contains all required data for certain resource
        """

        rel_seq = relative_path.split("/")

        if len(rel_seq) == 1:  # Chassis connected directly to root
            self.resource.add_sub_resource(relative_path, resource)
        else:
            if parent_id:
                parent_object = self.elements.get(parent_id, self.resource)
            else:
                parent_object = self.elements.get("/".join(rel_seq[:-1]), self.resource)

            rel_path = re.search(r"\d+", rel_seq[-1]).group()
            parent_object.add_sub_resource(rel_path, resource)
            # parent_object.add_sub_resource(rel_seq[-1], resource)

        self.elements.update({relative_path: resource})

    def _get_module_list(self):
        """Set list of all modules from entity mib table for provided list of ports

        :return:
        """

        for port in self.port_list:
            modules = []
            modules.extend(self._get_module_parents(port))
            for module in modules[::-1]:
                if module in self.module_list:
                    continue
                vendor_type = self.snmp_handler.get_property('ENTITY-MIB', 'entPhysicalVendorType', module)
                if not re.search(self.module_exclude_pattern, vendor_type.lower()):
                    if module not in self.exclusion_list and module not in self.module_list:
                        self.module_list.append(module)
                else:
                    self._excluded_models.append(module)

    def _get_module_parents(self, module_id):
        """
        Retrieve all parent modules for a specific module

        :param module_id:
        :return list: parent modules
        """
        result = []
        parent_id = int(self.entity_table[module_id]['entPhysicalContainedIn'])
        if parent_id > 0 and parent_id in self.entity_table:
            if re.search(r'module', self.entity_table[parent_id]['entPhysicalClass']):
                result.append(parent_id)
                result.extend(self._get_module_parents(parent_id))
            elif re.search(r'chassis', self.entity_table[parent_id]['entPhysicalClass']):
                return result
            else:
                result.extend(self._get_module_parents(parent_id))
        return result

    def _get_resource_id(self, item_id):
        parent_id = int(self.entity_table[item_id]['entPhysicalContainedIn'])
        if parent_id > 0 and parent_id in self.entity_table:
            if re.search(r'container|backplane', self.entity_table[parent_id]['entPhysicalClass']):
                result = self.entity_table[parent_id]['entPhysicalParentRelPos']
            elif parent_id in self._excluded_models:
                result = self._get_resource_id(parent_id)
            else:
                result = self.entity_table[item_id]['entPhysicalParentRelPos']
        else:
            result = self.entity_table[item_id]['entPhysicalParentRelPos']
        return result

    def _get_chassis_attributes(self):
        """ Get Chassis element attributes """

        self.logger.info("Building Chassis")
        for chassis in self.chassis_list:
            chassis_id = self.relative_address[chassis]

            chassis_object = GenericChassis(shell_name=self.shell_name,
                                            name="Chassis {}".format(chassis_id),
                                            unique_id="{}.{}.{}".format(self.resource_name, "chassis", chassis))

            chassis_object.model = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalModelName", chassis) or \
                                   self.entity_table[chassis]["entPhysicalDescr"]
            chassis_object.serial_number = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalSerialNum", chassis)

            relative_address = "{0}".format(chassis_id)

            self._add_element(relative_path=relative_address, resource=chassis_object)

            self.logger.info("Added " + self.entity_table[chassis]["entPhysicalDescr"] + " Chassis")
        self.logger.info("Building Chassis completed")

    def _get_module_attributes(self):
        """ Set attributes for all discovered modules """

        self.logger.info("Building Modules")
        for module in self.module_list:
            module_id = self.relative_address[module]
            module_index = self._get_resource_id(module)

            if "/" in module_id and len(module_id.split("/")) < 3:
                module_object = GenericModule(shell_name=self.shell_name,
                                              name="Module {}".format(module_index),
                                              unique_id="{0}.{1}.{2}".format(self.resource_name, "module", module))

            else:
                module_object = GenericSubModule(shell_name=self.shell_name,
                                                 name="SubModule {}".format(module_index),
                                                 unique_id="{0}.{1}.{2}".format(self.resource_name, "sub_module",
                                                                                module))

            module_object.model = self.entity_table[module]["entPhysicalDescr"]
            module_object.version = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalSoftwareRev", module)
            module_object.serial_number = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalSerialNum", module)

            self._add_element(relative_path=module_id, resource=module_object)
            self.logger.info("Module {} added".format(self.entity_table[module]["entPhysicalDescr"]))

        self.logger.info("Building Modules completed")

    def _filter_power_port_list(self):
        """Get power supply relative path

        :return: string relative path
        """

        power_supply_list = list(self.power_supply_list)
        for power_port in power_supply_list:
            parent_index = int(self.entity_table[power_port]['entPhysicalContainedIn'])
            if 'powerSupply' in self.entity_table[parent_index]['entPhysicalClass']:
                if parent_index in self.power_supply_list:
                    self.power_supply_list.remove(power_port)

    def _get_power_supply_parent_id(self, port):
        """
        Retrieve power port relative address, handles exceptional cases

        :param port:
        :return:
        """
        parent_index = int(self.entity_table[port]['entPhysicalContainedIn'])
        result = int(self.entity_table[parent_index]['entPhysicalParentRelPos'])
        return result

    def _get_power_ports(self):
        """Get attributes for power ports provided in self.power_supply_list

        :return:
        """

        self.logger.info("Building PowerPorts")
        self._filter_power_port_list()
        for port in self.power_supply_list:
            port_id = self.entity_table[port]["entPhysicalParentRelPos"]
            parent_index = int(self.entity_table[port]["entPhysicalContainedIn"])
            chassis_id = self.get_relative_address(parent_index)
            relative_address = "{0}/PP{1}".format(chassis_id, port_id)

            power_port = GenericPowerPort(shell_name=self.shell_name,
                                          name="PP{0}".format(self.power_supply_list.index(port)),
                                          unique_id="{0}.{1}.{2}".format(self.resource_name, "power_port", port))

            power_port.model = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalModelName", port)
            power_port.port_description = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalDescr", port)
            power_port.version = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalHardwareRev", port)
            power_port.serial_number = self.snmp_handler.get_property("ENTITY-MIB", "entPhysicalSerialNum", port)

            self._add_element(relative_path=relative_address, resource=power_port, parent_id=chassis_id)

            self.logger.info("Added " + self.entity_table[port]["entPhysicalName"].strip(" \t\n\r") + " Power Port")
        self.logger.info("Building Power Ports completed")

    def _get_port_channels(self):
        """Get all port channels and set attributes for them

        :return:
        """

        if not self.if_table:
            return
        port_channel_dic = {index: port for index, port in self.if_table.iteritems() if
                            "channel" in port[self.IF_ENTITY] and "." not in port[self.IF_ENTITY]}
        self.logger.info("Building Port Channels")
        for key, value in port_channel_dic.iteritems():
            interface_model = value[self.IF_ENTITY]
            match_object = re.search(r"\d+$", interface_model)
            if match_object:
                interface_id = "{0}".format(match_object.group(0))
                port_channel = GenericPortChannel(shell_name=self.shell_name,
                                                  name=interface_model,
                                                  unique_id="{0}.{1}.{2}".format(self.resource_name,
                                                                                 "port_channel",
                                                                                 interface_id))

                port_channel.port_description = self.snmp_handler.get_property("IF-MIB", "ifAlias", key)
                port_channel.ipv4_address = self._get_ipv4_interface_address(key)
                port_channel.ipv6_address = self._get_ipv6_interface_address(key)
                port_channel.associated_ports = self._get_associated_ports(key)

                self._add_element(relative_path=interface_id, resource=port_channel)
                self.logger.info("Added " + interface_model + " Port Channel")

            else:
                self.logger.error("Adding of {0} failed. Name is invalid".format(interface_model))
 
        self.logger.info("Building Port Channels completed")

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

    def _get_ports_attributes(self):
        """Get resource details and attributes for every port in self.port_list

        :return:
        """

        self.logger.info("Load Ports:")
        for port in self.port_list:
            if_table_port_attr = {"ifType": "str", "ifPhysAddress": "str", "ifMtu": "int", "ifHighSpeed": "int"}
            if_table = self.if_table[self.port_mapping[port]].copy()
            if_table.update(self.snmp_handler.get_properties("IF-MIB", self.port_mapping[port], if_table_port_attr))
            interface_name = self.if_table[self.port_mapping[port]][self.IF_ENTITY].replace("'", "")
            if interface_name == "":
                interface_name = self.entity_table[port]["entPhysicalName"]
            if interface_name == "":
                continue

            port_object = GenericPort(shell_name=self.shell_name,
                                      name=interface_name.replace("/", "-"),
                                      unique_id="{0}.{1}.{2}".format(self.resource_name, "port", port))

            port_object.port_description = self.snmp_handler.get_property("IF-MIB", "ifAlias", self.port_mapping[port])
            port_object.l2_protocol_type = if_table[self.port_mapping[port]]["ifType"].replace("/", "").replace("'", "")
            port_object.mac_address = if_table[self.port_mapping[port]]["ifPhysAddress"]
            port_object.mtu = if_table[self.port_mapping[port]]["ifMtu"]
            port_object.bandwidth = if_table[self.port_mapping[port]]["ifHighSpeed"]
            port_object.ipv4_address = self._get_ipv4_interface_address(self.port_mapping[port])
            port_object.ipv6_address = self._get_ipv6_interface_address(self.port_mapping[port])
            port_object.duplex = self._get_port_duplex(self.port_mapping[port])
            port_object.auto_negotiation = self._get_port_autoneg(self.port_mapping[port])
            port_object.adjacent = self._get_adjacent(self.port_mapping[port])

            self._add_element(relative_path=self.relative_address[port], resource=port_object)
            self.logger.info("Added " + interface_name + " Port")

        self.logger.info("Building Ports completed")

    def get_relative_address(self, item_id):
        """Build relative path for received item

        :param item_id:
        :return:
        """

        result = ''
        if item_id not in self.chassis_list:
            parent_id = int(self.entity_table[item_id]['entPhysicalContainedIn'])
            if parent_id not in self.relative_address.keys():
                if parent_id in self.module_list:
                    result = self._get_resource_id(parent_id)
                if result != '':
                    result = self.get_relative_address(parent_id) + '/' + result
                else:
                    result = self.get_relative_address(parent_id)
            else:
                result = self.relative_address[parent_id]
        else:
            result = self.relative_address[item_id]

        return result

    def _filter_entity_table(self, raw_entity_table):
        """Filters out all elements if their parents, doesn't exist, or listed in self.exclusion_list

        :param raw_entity_table: entity table with unfiltered elements
        """

        elements = raw_entity_table.filter_by_column('ContainedIn').sort_by_column('ParentRelPos').keys()
        for element in reversed(elements):
            parent_id = int(self.entity_table[element]['entPhysicalContainedIn'])

            if parent_id not in raw_entity_table or parent_id in self.exclusion_list:
                self.exclusion_list.append(element)

    def _get_ipv4_interface_address(self, port_index):
        """Get IP address details for provided port

        :param port_index: port index in ifTable
        :return interface_details: detected info for provided interface dict{'IPv4 Address': '', 'IPv6 Address': ''}
        """

        if self.ip_v4_table and len(self.ip_v4_table) > 1:
            for key, value in self.ip_v4_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == port_index:
                    return key

    def _get_ipv6_interface_address(self, port_index):
        if self.ip_v6_table and len(self.ip_v6_table) > 1:
            for key, value in self.ip_v6_table.iteritems():
                if 'ipAdEntIfIndex' in value and int(value['ipAdEntIfIndex']) == port_index:
                    return key

    def _get_port_duplex(self, port_index):
        for key, value in self.duplex_table.iteritems():
            if 'dot3StatsIndex' in value.keys() and value['dot3StatsIndex'] == str(port_index):
                interface_duplex = self.snmp_handler.get_property('EtherLike-MIB', 'dot3StatsDuplexStatus', key)
                if 'fullDuplex' in interface_duplex:
                    return 'Full'

    def _get_port_autoneg(self, port_index):
        try:
            auto_negotiation = self.snmp_handler.get(('MAU-MIB', 'ifMauAutoNegAdminStatus', port_index, 1)).values()[0]
            if 'enabled' in auto_negotiation.lower():
                return 'True'
        except Exception as e:
            self.logger.error('Failed to load auto negotiation property for interface {0}'.format(e.message))
            return 'False'

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
                port = self.snmp_handler.get_property('CISCO-CDP-MIB', 'cdpCacheDevicePort', key)
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
                            remoute_port_name = self.snmp_handler.get_property('LLDP-MIB', 'lldpRemPortDesc', port_id)
                            if remoute_port_name and remoute_sys_name:
                                result = result_template.format(remote_host=remoute_sys_name,
                                                                remote_port=remoute_port_name)
                                break
        return result

    def _get_mapping(self, port_index, port_descr):
        """Get mapping from entPhysicalTable to ifTable.
        Build mapping based on ent_alias_mapping_table if exists else build manually based on
        entPhysicalDescr <-> ifDescr mapping.

        :return: simple mapping from entPhysicalTable index to ifTable index:
        |        {entPhysicalTable index: ifTable index, ...}
        """

        port_id = None
        try:
            ent_alias_mapping_identifier = self.snmp_handler.get(('ENTITY-MIB', 'entAliasMappingIdentifier', port_index, 0))
            port_id = int(ent_alias_mapping_identifier['entAliasMappingIdentifier'].split('.')[-1])
        except Exception as e:
            self.logger.error(e.message)

            if_table_re = "/".join(re.findall('\d+', port_descr))
            for interface in self.if_table.values():
                if interface[self.IF_ENTITY].endswith(if_table_re):
                    port_id = int(interface['suffix'])
                    break
        return port_id
