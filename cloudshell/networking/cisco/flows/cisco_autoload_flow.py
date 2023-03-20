import os
import re
from collections import OrderedDict

from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import (
    CiscoGenericSNMPAutoload,
)
from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow

from cloudshell.snmp.autoload.constants import entity_constants

entity_constants.ENTITY_VENDOR_TYPE_TO_CLASS_MAP = OrderedDict(
    [
        (re.compile(r"^\S+cevcontainer", re.IGNORECASE), "container"),
        (re.compile(r"^\S+cevchassis", re.IGNORECASE), "chassis"),
        (re.compile(r"^\S+cevmodule", re.IGNORECASE), "module"),
        (re.compile(r"^\S+cevport", re.IGNORECASE), "port"),
        (re.compile(r"^\S+cevpowersupply", re.IGNORECASE), "powerSupply"),
    ]
)


class CiscoSnmpAutoloadFlow(AbstractAutoloadFlow):
    CISCO_MIBS_FOLDER = os.path.join(os.path.dirname(__file__), os.pardir, "mibs")
    DEVICE_NAMES_MAP_FILE = os.path.join(CISCO_MIBS_FOLDER, "device_names_map.csv")

    def __init__(self, logger, snmp_handler):
        super().__init__(logger)
        self._snmp_handler = snmp_handler

    def _autoload_flow(self, supported_os, resource_model):
        with self._snmp_handler.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(self.CISCO_MIBS_FOLDER)
            snmp_service.load_mib_tables(
                ["CISCO-PRODUCTS-MIB", "CISCO-ENTITY-VENDORTYPE-OID-MIB"]
            )
            cisco_snmp_autoload = CiscoGenericSNMPAutoload(
                snmp_handler=snmp_service,
                logger=self._logger,
                resource_model=resource_model,
            )
            cisco_snmp_autoload.port_table_service.PORT_EXCLUDE_LIST.append(
                r"stack|engine|management|dwdm|virtual|odu-group|virtual\s*interface|"
                r"mgmt|voice|vlan|foreign|group-async|GigECtrlr|ptp\d*\S*r(s)*p\d*|"
                r"control\s*ethernet(\s*port)*|null|eobc|^(nu|vl|lo)\d+|vi\d+|lpts|"
                r"console\s*port|\.|loopback|cpp|bdi|optics\d|nvFabric-(Ten)*Gig"
            )
            cisco_snmp_autoload.port_table_service.PORT_VALID_TYPE_LIST.extend(
                [
                    "ethernet|other|propPointToPointSerial"
                    "|fastEther|opticalChannel|^otn|pos|sonet$"
                ]
            )
            cisco_snmp_autoload.port_table_service.PORT_CHANNEL_EXCLUDE_LIST = [r"\."]
            cisco_snmp_autoload.physical_table_service.MODULE_EXCLUDE_LIST = [
                r"powershelf|cevsfp|cevxfr|cevSensor|cevCpuTypeCPU|"
                r"cevxfp|cevContainer10GigBasePort|cevModuleDIMM|"
                r"cevModulePseAsicPlim|cevModule\S+Storage$|"
                r"cevModuleFabricTypeAsic|cevModuleCommonCardsPSEASIC|"
                r"cevFan|cevSensor"
            ]
            cisco_snmp_autoload.physical_table_service.CONTAINER_EXCLUDE_LIST = [
                r"powershelf|cevsfp|cevxfr|"
                r"cevxfp|cevContainer10GigBasePort|"
                r"cevFan|cevSensor|cevCpu|cevContainerDaughterCard"
            ]

            cisco_snmp_autoload.system_info_service.set_model_name_map_file_path(
                self.DEVICE_NAMES_MAP_FILE
            )
            return cisco_snmp_autoload.discover(supported_os)
