from unittest import TestCase
from mock import MagicMock
import re
from cloudshell.networking.cisco.cisco_configuration_operations import CiscoConfigurationOperations

__author__ = 'CoYe'

class TestCiscoHandlerBase(TestCase):
    def _get_handler(self):
        self.cli = MagicMock()
        self.snmp = MagicMock()
        self.api = MagicMock()
        self.logger = MagicMock()
        return CiscoConfigurationOperations(cli=self.cli, logger=self.logger, api=self.api, resource_name='resource_name')

    def test_save_raises_exception(self):
        #output = '%Error opening tftp://10.10.10.10//CloudShell\n/Configs/Gold/Test1/ASR1004-2-running-180516-101627 (Timed out)'
        output = '%Error opening tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/ASR1004-2-running-180516-101627 (Timed out)'
        handler = self._get_handler()
        handler.cli.send_command = MagicMock(return_value=output)
        self.assertRaises(Exception, handler.save_configuration, 'tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/',
                                                       'running')

    def test_save_raises_exception_error_message(self):
        # output = '%Error opening tftp://10.10.10.10//CloudShell\n/Configs/Gold/Test1/ASR1004-2-running-180516-101627 (Timed out)'
        output = '%Error opening tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/ASR1004-2-running-180516-101627 (Timed out)'
        handler = self._get_handler()
        handler.cli.send_command = MagicMock(return_value=output)
        try:
            handler.save_configuration('tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/', 'running')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertTrue(output.replace('%', '') in e.message)

    def test_save_cisco_nexus_5k_customer_report(self):
        resource_name = 'Very_long name with Spaces'
        config_type = 'running'
        output = """N5K-L3-Sw1#
        N5K-L3-Sw1# copy running-config tftp:
        Enter destination filename: [N5K-L3-Sw1-running-config] N5K1
        Enter vrf (If no input, current vrf 'default' is considered): management
        Enter hostname for the tftp server: 10.10.10.10
        Trying to connect to tftp server......
        Connection to Server Established.

        [                         ]         0.50KB
        [#                        ]         4.50KB

         TFTP put operation was successful
         Copy complete, now saving to disk (please wait)...
         N5K-L3-Sw1#"""
        handler = self._get_handler()
        handler.resource_name = resource_name
        responce_template = '{0}-{1}-{2}'.format(resource_name.replace(' ', '_')[:23], config_type, '\d+\-\d+')
        handler.cli.send_command = MagicMock(return_value=output)
        responce = handler.save_configuration('tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/',
                                                config_type, 'management')
        self.assertIsNotNone(responce)
        self.assertTrue(re.search(responce_template, responce))

    def test_save_cisco_nexus_6k_customer_report(self):
        resource_name = 'Very_long name with Spaces'
        config_type = 'running'
        output = """N6K-Sw1-S1# copy running-config tftp:
        Enter destination filename: [N6K-Sw1-S1-running-config] TestName
        Enter vrf (If no input, current vrf 'default' is considered): management
        Enter hostname for the tftp server: 10.10.10.10Trying to connect to tftp server......
        Connection to Server Established.

        [                         ]         0.50KB
        [#                        ]         4.50KB

         TFTP put operation was successful
         Copy complete, now saving to disk (please wait)...

        N6K-Sw1-S1#"""
        handler = self._get_handler()
        handler.resource_name = resource_name
        responce_template = '{0}-{1}-{2}'.format(resource_name.replace(' ', '_')[:23], config_type, '\d+\-\d+')
        handler.cli.send_command = MagicMock(return_value=output)
        responce = handler.save_configuration('tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/',
                                                config_type, 'management')
        self.assertIsNotNone(responce)
        self.assertTrue(re.search(responce_template, responce))

    def test_save_cisco_asr_1k_no_error_customer_report(self):
        output = """ASR1004-2#copy running-config tftp:
        Address or name of remote host []?
        10.10.10.10
        Destination filename [asr1004-2-confg]?
        ASR1004-2-running-100516-084841
        .....
        %Error opening tftp://10.10.10.10/ASR1004-2-running-100516-084841 (Timed out)
        ASR1004-2#"""
        handler = self._get_handler()
        handler.cli.send_command = MagicMock(return_value=output)
        self.assertRaises(Exception, handler.save_configuration, 'tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/',
                  'running')

    def test_save_cisco_6504_customer_report(self):
        resource_name = 'Very_long name with Spaces'
        config_type = 'running'
        output = """C6504e-1-CE7#copy running-config tftp:
        Address or name of remote host []? 10.10.10.10
        Destination filename [c6504e-1-ce7-confg]? 6504e1
        !!
        23518 bytes copied in 0.904 secs (26015 bytes/sec)
        C6504e-1-CE7#"""
        handler = self._get_handler()
        handler.resource_name = resource_name
        responce_template = '{0}-{1}-{2}'.format(resource_name.replace(' ', '_')[:23], config_type, '\d+\-\d+')
        handler.cli.send_command = MagicMock(return_value=output)
        responce = handler.save_configuration('tftp://10.10.10.10/CloudShell/Configs/Gold/Test1/',
                                                config_type, 'management')
        self.assertIsNotNone(responce)
        self.assertTrue(re.search(responce_template, responce))

    def test_save_cisco_custom_output(self):
        resource_name = 'Very_long name with Spaces'
        config_type = 'running'
        output = """C6504e-1-CE7#copy running-config tftp:
        Address or name of remote host []? 10.10.10.10
        Destination filename [c6504e-1-ce7-confg]? 6504e1
        !!
        [OK - 1811552 bytes]
        1811552 bytes copied in 53.511 secs (34180 bytes/sec)
        C6504e-1-CE7#"""
        handler = self._get_handler()
        handler.resource_name = resource_name
        responce_template = '{0}-{1}-{2}'.format(resource_name.replace(' ', '_')[:23], config_type, '\d+\-\d+')
        handler.cli.send_command = MagicMock(return_value=output)
        responce = handler.save_configuration('tftp://10.10.10.10/CloudShell/Configs/Gold/Test1/',
                                                config_type, 'management')
        self.assertIsNotNone(responce)
        self.assertTrue(re.search(responce_template, responce))
