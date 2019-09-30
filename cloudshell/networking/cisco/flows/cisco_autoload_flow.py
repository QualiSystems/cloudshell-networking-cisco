#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow

from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import (
    CiscoGenericSNMPAutoload,
)
from cloudshell.networking.cisco.autoload.cisco_port_attrs_service import (
    CiscoSnmpPortAttrTables,
)
from cloudshell.networking.cisco.autoload.cisco_snmp_if_port import CiscoSnmpIfPort
from cloudshell.networking.cisco.autoload.cisco_snmp_if_port_channel import (
    CiscoIfPortChannel,
)


class CiscoSnmpAutoloadFlow(AbstractAutoloadFlow):
    CISCO_MIBS_FOLDER = os.path.join(os.path.dirname(__file__), os.pardir, "mibs")
    DEVICE_NAMES_MAP_FILE = os.path.join(CISCO_MIBS_FOLDER, "device_names_map.csv")

    def __init__(self, logger, snmp_handler):
        super(CiscoSnmpAutoloadFlow, self).__init__(logger)
        self._snmp_handler = snmp_handler

    def _autoload_flow(self, supported_os, resource_model):
        with self._snmp_handler.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(self.CISCO_MIBS_FOLDER)
            snmp_service.load_mib_tables(
                ["CISCO-PRODUCTS-MIB", "CISCO-ENTITY-VENDORTYPE-OID-MIB"]
            )
            cisco_snmp_autoload = CiscoGenericSNMPAutoload(snmp_service, self._logger)
            cisco_snmp_autoload.entity_table_service.set_port_exclude_pattern(
                r"stack|engine|management|"
                r"mgmt|voice|foreign|cpu|"
                r"control\s*ethernet\s*port|"
                r"console\s*port"
            )
            cisco_snmp_autoload.entity_table_service.set_module_exclude_pattern(
                r"powershelf|cevsfp|cevxfr|"
                r"cevxfp|cevContainer10GigBasePort|"
                r"cevModulePseAsicPlim"
            )
            (
                cisco_snmp_autoload.if_table_service.port_attributes_service
            ) = CiscoSnmpPortAttrTables(snmp_service, self._logger)
            cisco_snmp_autoload.if_table_service.if_port_type = CiscoSnmpIfPort
            cisco_snmp_autoload.if_table_service.if_port_channel_type = (
                CiscoIfPortChannel
            )

            cisco_snmp_autoload.system_info_service.set_model_name_map_file_path(
                self.DEVICE_NAMES_MAP_FILE
            )
            return cisco_snmp_autoload.discover(
                supported_os, resource_model, validate_module_id_by_port_name=True
            )
