# flake8: noqa
from unittest import TestCase

from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.snmp.old.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV2ReadParameters

from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import (
    CiscoGenericSNMPAutoload,
)


class TestCiscoAutoload(TestCase):
    SUPPORTED_OS = ["cisco"]

    def _get_handler(self, ip, shell_name="", shell_type="", community="public"):
        logger = get_qs_logger(log_file_prefix=ip)
        snmp = QualiSnmp(
            SNMPV2ReadParameters(ip=ip, snmp_read_community=community), logger=logger
        )
        handler = CiscoGenericSNMPAutoload(
            shell_name=shell_name,
            shell_type=shell_type,
            logger=logger,
            snmp_handler=snmp,
            resource_name=ip,
        )
        return handler

    def test_is_loads_router_7600_correctly(self):
        print("-----------7600------------")
        ip = "192.168.73.8"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        port_channels = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port Channel"
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(ports) == 5)
        self.assertTrue(len(modules) == 2)
        self.assertTrue(len(sub_modules) == 1)
        self.assertTrue(len(port_channels) == 0)
        self.assertTrue(len(power_ports) == 1)
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))

    def test_is_loads_nexuss_correctly(self):
        print("-----------7600------------")
        ip = "192.168.73.54"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        port_channels = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port Channel"
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(ports) == 54)
        self.assertTrue(len(modules) == 2)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(len(port_channels) == 1)
        self.assertTrue(len(power_ports) == 2)
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))

    def test_is_loads_multichassis_nexus_correctly(self):
        print("-----------7600------------")
        ip = "192.168.73.66"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        port_channels = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port Channel"
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))
        self.assertTrue(len(chassis) == 8)
        self.assertTrue(len(ports) == 390)
        self.assertTrue(len(modules) == 9)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(len(port_channels) == 10)
        self.assertTrue(len(power_ports) == 16)
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))

    def test_is_loads_switch_C2950V_correctly(self):
        print("-----------C2950V------------")
        ip = "192.168.73.98"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        port_channels = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port Channel"
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(ports) == 7)
        self.assertTrue(len(modules) == 1)
        self.assertTrue(len(sub_modules) == 2)
        self.assertTrue(len(port_channels) == 0)
        self.assertTrue(len(power_ports) == 1)
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))

    def test_is_loads_switch_C2950V2_correctly(self):
        print("-----------C2950V2------------")
        ip = "192.168.73.99"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        port_channels = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port Channel"
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(ports) == 9)
        self.assertTrue(len(modules) == 1)
        self.assertTrue(len(sub_modules) == 2)
        self.assertTrue(len(port_channels) == 0)
        self.assertTrue(len(power_ports) == 1)
        self.assertFalse(len(trash_chrs) > 0)
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))

    def test_is_loads_router_7609_correctly(self):
        print("-----------7609------------")
        ip = "192.168.73.10"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        port_channels = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port Channel"
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 6)
        self.assertTrue(len(ports) == 73)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(len(port_channels) == 5)
        self.assertTrue(len(power_ports) == 1)
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(port_channels))
        print(len(power_ports))

    def test_is_loads_nexus_3k_correctly(self):
        print("-----------nexus_3k------------")
        ip = "192.168.73.6"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 1)
        self.assertTrue(len(ports) == 54)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))

    def test_is_loads_nexus_7k_correctly(self):
        print("-----------nexus_3k------------")
        ip = "192.168.73.2"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 2)
        self.assertTrue(len(ports) == 54)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))

    def test_is_loads_nexus_7k_chassis_issue_correctly(self):
        print("-----------nexus_7k------------")
        ip = "192.168.73.4"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 5)
        self.assertTrue(len(ports) == 240)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))

    def test_is_loads_7609_12_correctly(self):
        print("-----------7609_12------------")
        ip = "192.168.73.67"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 7)
        self.assertTrue(len(ports) == 64)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))

    def test_is_loads_some_IOS_correctly(self):
        print("-----------some_IOS------------")
        ip = "192.168.73.88"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 2)
        self.assertTrue(len(ports) == 52)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))

    def test_is_loads_2950_correctly(self):
        print("-----------2950------------")
        ip = "192.168.42.235"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 0)
        self.assertTrue(len(ports) == 26)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))

    def test_is_loads_2950_Gen2_correctly(self):
        print("-----------2950------------")
        ip = "192.168.42.235"
        result = self._get_handler(ip, "Cisco IOS Switch 2G", "CS_Switch").discover(
            self.SUPPORTED_OS
        )
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if "GenericModule" in resource.model
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model.endswith("GenericPort")
        ]
        sub_modules = [
            resource for resource in result.resources if "SubModule" in resource.name
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 0)
        self.assertTrue(len(ports) == 26)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))

    def test_is_loads_ncs_5500_correctly(self):
        print("-----------ncs_5500------------")
        ip = "192.168.73.92"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        exced_rel_path = [
            resource
            for resource in result.resources
            if len(resource.relative_address.split("/")) > 4
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(power_ports))

        self.assertFalse(len(trash_chrs) > 0)
        self.assertFalse(len(exced_rel_path) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 2)
        self.assertTrue(len(ports) == 78)
        self.assertTrue(len(sub_modules) == 12)

    def test_is_loads_ncs_6000_correctly(self):
        print("-----------ncs_6000------------")
        ip = "192.168.73.84"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        exced_rel_path = [
            resource
            for resource in result.resources
            if len(resource.relative_address.split("/")) > 4
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(power_ports))

        self.assertFalse(len(trash_chrs) > 0)
        self.assertFalse(len(exced_rel_path) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 2)
        self.assertTrue(len(ports) == 20)
        self.assertTrue(len(sub_modules) == 10)

    def test_is_loads_ncs_5500_2_correctly(self):
        print("-----------ncs_5500_2------------")
        ip = "192.168.73.94"
        result = self._get_handler(ip).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        exced_rel_path = [
            resource
            for resource in result.resources
            if len(resource.relative_address.split("/")) > 4
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        self.assertTrue(self._check_relative_path(result.resources))
        self.assertTrue(self._check_names(result.resources))
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(power_ports))

        self.assertFalse(len(trash_chrs) > 0)
        self.assertFalse(len(exced_rel_path) > 0)
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(modules) == 2)
        self.assertTrue(len(ports) == 78)
        self.assertTrue(len(sub_modules) == 12)

    def test_is_loads_ciscos_correctly(self):
        print("-----------ncs_4000------------")
        ip_list = xrange(2, 130)
        ip_address = "192.168.73.111"
        result = self._get_handler(ip_address).discover(self.SUPPORTED_OS)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [
            resource for resource in result.resources if "Chassis" in resource.name
        ]
        modules = [
            resource
            for resource in result.resources
            if resource.model == "Generic Module"
        ]
        ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Port"
        ]
        sub_modules = [
            resource for resource in result.resources if "Sub Module" in resource.name
        ]
        power_ports = [
            resource
            for resource in result.resources
            if resource.model == "Generic Power Port"
        ]
        exceed_rel_path = [
            resource
            for resource in result.resources
            if len(resource.relative_address.split("/")) > 4
        ]
        trash_chrs = [
            attribute
            for attribute in result.attributes
            if type(attribute.attribute_value) is str
            and "\\s" in attribute.attribute_value
        ]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print(
                    char.relative_address
                    + ": "
                    + char.attribute_name
                    + " = "
                    + char.attribute_value
                )
        self.assertTrue(self._check_relative_path(result.resources))
        check_names = self._check_names(result.resources)
        if not check_names:
            self.assertTrue(self._check_names(result.resources))
        self.assertFalse(
            any(
                [
                    resource
                    for resource in result.resources
                    if not self.is_valid_element(resource)
                ]
            )
        )
        print("-" * 32)
        print(len(chassis))
        print(len(ports))
        print(len(modules))
        print(len(sub_modules))
        print(len(power_ports))
        print("-" * 32)
        self.assertFalse(len(trash_chrs) > 0)
        self.assertFalse(len(exceed_rel_path) > 0)
