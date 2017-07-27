import re

from cloudshell.snmp.quali_snmp import QualiMibTable


class CiscoSNMPEntityTable(object):
    ENTITY_PHYSICAL = "entPhysicalDescr"
    # ENTITY_VENDOR_TYPE_TO_CLASS_MAP = OrderedDict(("cevcontainer", "container"), ("cevchassis", "chassis"),
    #                                               ("cevmodule", "module"), ("cevport", "port"), ("cevpowersupply",
    #                                                                                              "powerSupply"))

    def __init__(self, snmp_handler, logger):
        self._snmp = snmp_handler
        self._logger = logger
        self._entity_table = None
        self._port_list = []
        self._chassis_list = []
        self._module_list = []
        self.relative_address = {}
        self.port_mapping = {}
        self.exclusion_list = []
        self._excluded_models = []
        self._filtered_chassis_list = []
        self._filtered_module_list = []
        self._power_supply_list = []
        self._filtered_power_supply_list = []
        self.entity_table_black_list = []
        self.port_exclude_pattern = r'stack|engine|management|mgmt|voice|foreign|cpu|control\s*ethernet\s*port'
        self.module_exclude_pattern = r'cevsfp|cevxfr|cevxfp|cevContainer10GigBasePort'
        self.entity_to_container_pattern = "powershelf|cevModuleCommonCards$"
        self.ignore_entity_pattern = "cevModulePseAsicPlim|cevModule$"
        self.ignore_entities_dict = dict()

    @property
    def get_chassis(self):
        if not self._filtered_chassis_list:
            if len(self._chassis_list) < 1:
                self._logger.error('Entity table error, no chassis found')
                raise Exception('Cannot load entPhysicalTable. Autoload cannot continue')

            for chassis in self._chassis_list:
                if chassis not in self.exclusion_list:
                    chassis_id = self.get_resource_id(chassis)
                    if chassis_id == '-1':
                        chassis_id = '0'
                    self.relative_address[chassis] = chassis_id
                    self._filtered_chassis_list.append(chassis)

        return self._filtered_chassis_list

    @property
    def get_port_list(self):
        return self._port_list

    @property
    def get_power_port_list(self):
        return self._power_supply_list

    @property
    def get_module_list(self):
        """Set list of all modules from entity mib table for provided list of ports

        :return:
        """
        if not self._filtered_module_list:
            for port in self._port_list:
                modules = []
                modules.extend(self._get_module_parents(port))
                for module in modules:
                    if module in self._module_list:
                        continue
                    # vendor_type = self._snmp.get_property('ENTITY-MIB', 'entPhysicalVendorType', module)
                    vendor_type = self._entity_table[module].get("entPhysicalVendorType")
                    if not re.search(self.module_exclude_pattern, vendor_type.lower()):
                        if module not in self.exclusion_list and module not in self._filtered_module_list:
                            self._filtered_module_list.append(module)
                    else:
                        self._excluded_models.append(module)
        return self._filtered_module_list

    def get_entity_table(self):
        self._entity_table = self._get_entity_table()
        self._filter_lower_bay_containers()

        return self._entity_table

    def _get_entity_table(self):
        """Read Entity-MIB and filter out device's structure and all it's elements, like ports, modules, chassis, etc.

        :rtype: QualiMibTable
        :return: structured and filtered EntityPhysical table.
        """

        result_dict = QualiMibTable('entPhysicalTable')

        entity_table_critical_port_attr = {'entPhysicalContainedIn': 'str', 'entPhysicalClass': 'str',
                                           'entPhysicalVendorType': 'str'}
        entity_table_optional_port_attr = {'entPhysicalDescr': 'str', 'entPhysicalName': 'str'}

        physical_indexes = self._snmp.get_table('ENTITY-MIB', 'entPhysicalParentRelPos')
        for index in physical_indexes.keys():
            is_excluded = False
            if physical_indexes[index]['entPhysicalParentRelPos'] == '':
                self.exclusion_list.append(index)
                continue
            temp_entity_table = physical_indexes[index].copy()
            temp_entity_table.update(self._snmp.get_properties('ENTITY-MIB', index, entity_table_critical_port_attr)
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

            temp_entity_table.update(self._snmp.get_properties('ENTITY-MIB', index, entity_table_optional_port_attr)
                                     [index])

            if temp_entity_table['entPhysicalClass'] == '' or "other" in temp_entity_table['entPhysicalClass']:
                vendor_type = temp_entity_table['entPhysicalVendorType']
                if not vendor_type:
                    vendor_type = self._snmp.get_property('ENTITY-MIB', 'entPhysicalVendorType', index)
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
            if re.search(self.entity_to_container_pattern, temp_entity_table['entPhysicalVendorType'].lower(),
                           re.IGNORECASE):
                temp_entity_table['entPhysicalClass'] = 'container'
            else:
                temp_entity_table['entPhysicalClass'] = temp_entity_table['entPhysicalClass'].replace("'", "")

            if re.search(self.ignore_entity_pattern, temp_entity_table['entPhysicalVendorType'].lower(),
                         re.IGNORECASE):
                # parent_id = temp_entity_table['entPhysicalContainedIn']
                # if int(parent_id) in self.ignore_entities_dict:
                #     self.ignore_entities_dict[index] = self.ignore_entities_dict[parent_id]
                # else:
                self.ignore_entities_dict[index] = temp_entity_table['entPhysicalContainedIn']

            if re.search(r'stack|chassis|module|port|powerSupply|container|backplane',
                         temp_entity_table['entPhysicalClass']):
                result_dict[index] = temp_entity_table

            if temp_entity_table['entPhysicalClass'] == 'chassis':
                self._chassis_list.append(index)
            elif temp_entity_table['entPhysicalClass'] == 'port':
                if not re.search(self.port_exclude_pattern, temp_entity_table['entPhysicalName'], re.IGNORECASE) \
                        and not re.search(self.port_exclude_pattern, temp_entity_table['entPhysicalDescr'],
                                          re.IGNORECASE):
                    self._port_list.append(index)
            elif temp_entity_table['entPhysicalClass'] == 'powerSupply':
                self._power_supply_list.append(index)

        self._filter_entity_table(result_dict)
        return result_dict

    def _filter_lower_bay_containers(self):
        """
        Filter rare cases when device have multiple bays with separate containers in each bay

        """
        upper_container = None
        lower_container = None
        containers = self._entity_table.filter_by_column('Class', "container").sort_by_column('ParentRelPos').keys()
        for container in containers:
            vendor_type = self._entity_table[container].get("entPhysicalVendorType")
            # self._snmp.get_property('ENTITY-MIB', 'entPhysicalVendorType', container)
            if 'uppermodulebay' in vendor_type.lower():
                upper_container = container
            if 'lowermodulebay' in vendor_type.lower():
                lower_container = container
        if lower_container and upper_container:
            child_upper_items_len = len(self._entity_table.filter_by_column('ContainedIn', str(upper_container)
                                                                            ).sort_by_column('ParentRelPos').keys())
            child_lower_items = self._entity_table.filter_by_column('ContainedIn', str(lower_container)
                                                                    ).sort_by_column('ParentRelPos').keys()
            for child in child_lower_items:
                self._entity_table[child]['entPhysicalContainedIn'] = upper_container
                self._entity_table[child]['entPhysicalParentRelPos'] = str(child_upper_items_len + int(
                    self._entity_table[child]['entPhysicalParentRelPos']))

    def get_resource_id(self, item_id):
        parent_id = int(self._entity_table[item_id]['entPhysicalContainedIn'])
        if parent_id > 0 and parent_id in self._entity_table:
            if re.search(r'container|backplane', self._entity_table[parent_id]['entPhysicalClass']):
                result = self._entity_table[parent_id]['entPhysicalParentRelPos']
            elif parent_id in self._excluded_models:
                result = self.get_resource_id(parent_id)
            else:
                result = self._entity_table[item_id]['entPhysicalParentRelPos']
        else:
            result = self._entity_table[item_id]['entPhysicalParentRelPos']
        return result

    def get_relative_address(self, item_id):
        """Build relative path for received item

        :param item_id:
        :return:
        """

        result = ''
        if int(item_id) not in self._filtered_chassis_list:
            parent_id = int(self._entity_table[item_id]['entPhysicalContainedIn'])
            if parent_id not in self.relative_address.keys():
                if parent_id in self._filtered_module_list:
                    result = self.get_resource_id(parent_id)
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

        elements = raw_entity_table.sort_by_column('ParentRelPos').keys()
        for element in reversed(elements):
            parent_id = int(raw_entity_table[element]['entPhysicalContainedIn'])
            if parent_id in self.ignore_entities_dict.keys():
                raw_entity_table[element]["entPhysicalContainedIn"] = self.ignore_entities_dict[parent_id]
                parent_id = self.ignore_entities_dict[parent_id]
            if self.exclusion_list and raw_entity_table[element]["entPhysicalContainedIn"] != "chassis":
                if parent_id not in raw_entity_table or parent_id in self.exclusion_list:
                    self.exclusion_list.append(element)
        return raw_entity_table

    def add_relative_addresss(self):
        """Build dictionary of relative paths for each module and port

        :return:
        """

        port_list = list(self._port_list)
        module_list = list(self._filtered_module_list)
        for module in module_list:
            if module not in self.exclusion_list:
                self.relative_address[module] = self.get_relative_address(module) + '/' + self.get_resource_id(module)
            else:
                self._filtered_module_list.remove(module)
        for port in port_list:
            if port not in self.exclusion_list:
                self.relative_address[port] = self._get_port_relative_address(
                    self.get_relative_address(port) + '/' + self.get_resource_id(port))
            else:
                self._port_list.remove(port)

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

    def _get_module_parents(self, module_id):
        """
        Retrieve all parent modules for a specific module

        :param module_id:
        :return list: parent modules
        """

        result = []
        parent_id = int(self._entity_table[module_id]['entPhysicalContainedIn'])
        if parent_id > 0 and parent_id in self._entity_table:
            if re.search(r'module', self._entity_table[parent_id]['entPhysicalClass']):
                result.append(parent_id)
                result.extend(self._get_module_parents(parent_id))
            elif re.search(r'chassis', self._entity_table[parent_id]['entPhysicalClass']):
                return result
            else:
                result.extend(self._get_module_parents(parent_id))
        return result
