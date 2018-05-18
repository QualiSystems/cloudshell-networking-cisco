from unittest import TestCase
from mock import MagicMock, patch
from cloudshell.devices.standards.networking.autoload_structure import GenericChassis, GenericPort
from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload
from cloudshell.snmp.quali_snmp import QualiMibTable


class TestsCiscoGenericSNMPAutoload(TestCase):
    def setUp(self):
        self._snmp_handler = MagicMock()
        self._shell_name = ""
        self._shell_type = "CS_switch"
        self._logger = MagicMock()
        self._resource_name = "resource"
        self.cisco_snmp_autoload = CiscoGenericSNMPAutoload(self._snmp_handler,
                                                            self._shell_name,
                                                            self._shell_type,
                                                            self._resource_name,
                                                            self._logger)

    def test_load_cisco_mib(self):
        self.cisco_snmp_autoload.load_cisco_mib()
        self._snmp_handler.update_mib_sources.called_once()

    def test_is_valid_device_os_success(self):
        mib = "SNMPv2-MIB"
        mib_property = "sysDescr"
        mib_index = "0"
        self._snmp_handler.get_property.return_value = "valid"
        self.cisco_snmp_autoload._is_valid_device_os([".*"])
        self._snmp_handler.get_property.called_once_with(mib, mib_property, mib_index)

    def test_is_valid_device_os_raises(self):
        mib = "SNMPv2-MIB"
        mib_property = "sysDescr"
        mib_index = "0"
        supported_os = ["1"]
        self._snmp_handler.get_property.return_value = "valid"
        try:
            self.cisco_snmp_autoload._is_valid_device_os(supported_os)
        except Exception as e:
            self.assertIn('Incompatible driver! Please use this driver for \'{0}\' operation system(s)'.
                          format(str(tuple(supported_os))), e.args)
        self._snmp_handler.get_property.called_once_with(mib, mib_property, mib_index)

    def test_get_device_model(self):
        model_name = "cevModelName"
        mib = 'SNMPv2-MIB'
        mib_property = 'sysObjectID'
        mib_index = '0'
        self._snmp_handler.get_property.return_value = "Cisco::{0}".format(model_name)
        result = self.cisco_snmp_autoload._get_device_model()
        self._snmp_handler.get_property.called_once_with(mib, mib_property, mib_index)
        self.assertEqual(model_name, result)

    def test_get_device_os_version(self):
        version = "12.3.S(3).45"
        mib = 'SNMPv2-MIB'
        mib_property = 'sysDescr'
        mib_index = '0'
        self._snmp_handler.get_property.return_value = "Version {0} ".format(version)
        result = self.cisco_snmp_autoload._get_device_os_version()
        self._snmp_handler.get_property.called_once_with(mib, mib_property, mib_index)
        self.assertEqual(version, result)

    def test_get_device_os_version_with_comma(self):
        version = "12.3.S(3).45"
        mib = 'SNMPv2-MIB'
        mib_property = 'sysDescr'
        mib_index = '0'
        self._snmp_handler.get_property.return_value = (
            "Version {0}, some text").format(version)

        result = self.cisco_snmp_autoload._get_device_os_version()

        self._snmp_handler.get_property.called_once_with(
            mib, mib_property, mib_index)
        self.assertEqual(version, result)

    def test_get_device_model_name(self):
        model_name = "model name"
        with patch(
            "cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload.get_device_name") as get_dev_name_mock:
            self.cisco_snmp_autoload._get_device_model_name(model_name)
            get_dev_name_mock.called_once_with(model_name)

    @patch("cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload.SnmpIfTable")
    @patch("cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload.CiscoSNMPEntityTable")
    def test_load_snmp_tables(self, snmp_ent_tbl_mock, snmp_if_tbl_mock):
        snmp_ent_tbl_mock.get_entity_table.return_value = QualiMibTable("EntPhysicalTable", {1: {"entPhysicalClass": "chassis"}})
        self.cisco_snmp_autoload._load_snmp_tables()
        snmp_if_tbl_mock.return_value.called_once_with(self._snmp_handler, self._logger)
        snmp_ent_tbl_mock.return_value.called_once_with(self._snmp_handler, self._logger, snmp_if_tbl_mock)
        snmp_ent_tbl_mock.return_value.get_entity_table.called_once()

    def test_add_element(self):
        uniqe_id = "{}.{}.{}".format(self._resource_name, "chassis", "some_id")
        relative_path = "0"
        chassis = GenericChassis(shell_name=self._shell_name,
                                 name="Chassis {}".format(0),
                                 unique_id="{}.{}.{}".format(self._resource_name, "chassis", uniqe_id))
        self.cisco_snmp_autoload._add_element(relative_path, chassis)
        self.assertTrue(self.cisco_snmp_autoload.elements[relative_path] == chassis)
        self.assertTrue(self.cisco_snmp_autoload.resource.resources["CH"][relative_path][-1] == chassis)
        port_relative_path = "0/0"
        port_uniqe_id = "{}.{}.{}".format(self._resource_name, "port", "some_id")
        port = GenericPort(shell_name=self._shell_name,
                           name="GigabitEthernet {}".format(port_relative_path),
                           unique_id="{}.{}.{}".format(self._resource_name, "port", port_uniqe_id))
        self.cisco_snmp_autoload._add_element(port_relative_path, port)
        self.assertTrue(self.cisco_snmp_autoload.elements[port_relative_path] == port)
        self.assertTrue(self.cisco_snmp_autoload.resource.resources["CH"][relative_path][-1].resources["P"][relative_path][-1])

    def test_discovery(self):
        pass
