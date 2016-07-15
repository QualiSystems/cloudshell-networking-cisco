from unittest import TestCase
from mock import MagicMock
import re
from cloudshell.networking.cisco.cisco_configuration_operations import CiscoConfigurationOperations

__author__ = 'CoYe'

class TestCiscoHandlerBase(TestCase):
    def _get_handler(self):
        self.output = """C6504e-1-CE7#copy running-config tftp:
        Address or name of remote host []? 10.10.10.10
        Destination filename [c6504e-1-ce7-confg]? 6504e1
        !!
        23518 bytes copied in 0.904 secs (26015 bytes/sec)
        C6504e-1-CE7#"""
        self.cli = MagicMock()
        self.snmp = MagicMock()
        self.api = MagicMock()
        self.logger = MagicMock()
        return CiscoConfigurationOperations(cli=self.cli, logger=self.logger, api=self.api,
                                            resource_name='resource_name')

    def test_save_validates_source_filename_parameter(self):
        handler = self._get_handler()
        handler.cli.send_command = MagicMock(return_value=self.output)
        self.assertRaises(Exception, handler.save_configuration, 'tftp://10.10.10.10//////CloudShell/Configs/Gold/Test1/',
                          'runsning')

    def test_save_should_handle_source_filename_not_case_sensitive(self):
        handler = self._get_handler()
        handler.cli.send_command = MagicMock(return_value=self.output)
        self.assertIsNotNone(handler.save_configuration('tftp://10.10.10.10//////CloudShell/Configs/Gold/Test1/',
                                                          'running'))
        self.assertIsNotNone(handler.save_configuration('tftp://10.10.10.10//////CloudShell/Configs/Gold/Test1/',
                                                          'RUNNING'))

    def test_save_validates_destination_host_host_parameter(self):
        handler = self._get_handler()
        handler.cli.send_command = MagicMock(return_value=self.output)
        self.assertRaises(Exception, handler.save_configuration, 'tftp://10.10.1as0.10//////CloudShell/Configs/Gold/Test1/',
                          'running')
        self.assertRaises(Exception, handler.save_configuration, 'tftp://10.10.1120.10//////CloudShell/Configs/Gold/Test1/',
                          'running')
        self.assertRaises(Exception, handler.save_configuration, 'tftp://10.10.10//////CloudShell/Configs/Gold/Test1/',
                          'running')

    # ToDo define how tftp:// should be verified
    # def test_save_validates_destination_host_filesystem_parameter(self):
    #     handler = self._get_handler()
    #     handler.cli.send_command = MagicMock(return_value=self.output)
    #     self.assertRaises(Exception, handler.save_configuration, 'tftasdp://10.10.10.10/CloudShell/Configs/Gold/Test1/',
    #                       'running')

