from unittest import TestCase
from mock import MagicMock
import re
from cloudshell.networking.cisco.cisco_configuration_operations import CiscoConfigurationOperations


class TestCiscoHandlerBase(TestCase):
    output = ''

    def return_output(self, *args, **kwargs):
        result = self.output
        self.output = ''
        return result

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
        self.output = output
        handler = self._get_handler()
        handler.cli.send_command = MagicMock
        handler.cli.send_command = self.return_output
        try:
            handler.save_configuration('tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/', 'running')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertTrue(output.replace('%', '') in e.message)

    def test_save_raises_exception_when_cannot_save_file_error_message(self):
        output = '''sw9003-vpp-10-3# copy running-config tftp://10.87.42.120
        Enter destination filename: [sw9003-vpp-10-3-running-config] 123123
        Enter vrf (If no input, current vrf 'default' is considered):
        Trying to connect to tftp server......
        Connection to Server Established.
        TFTP put operation failed:Access violation'''
        self.output = output
        handler = self._get_handler()
        handler.cli.send_command = MagicMock
        handler.cli.send_command = self.return_output
        try:
            handler.save_configuration('tftp://10.10.10.10//CloudShell/Configs/Gold/Test1/', 'running')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertTrue('Copy Command failed. TFTP put operation failed:Access violation' in e.message)

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

    def test_save_cisco_n6k_customer_report(self):
        resource_name = 'Very_long name with Spaces'
        config_type = 'running'
        output = """
Trying to connect to tftp server......
Connection to Server Established.

[                         ]         0.50KB
[#                        ]         4.50KB
 [##                       ]         8.50KB
  [###                      ]        12.50KB
   [####                     ]        16.50KB
    [#####                    ]        20.50KB
     [######                   ]        24.50KB
      [#######                  ]        28.50KB
       [########                 ]        32.50KB
        [#########                ]        36.50KB

         TFTP get operation was successful
         ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name temp FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-800 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-801 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-802 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-803 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-804 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-805 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-806 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-807 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-808 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-809 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-810 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-811 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-812 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-813 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-814 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-815 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-816 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-817 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-818 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-819 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-820 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-821 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-822 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-823 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-824 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-825 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-826 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-827 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-828 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-829 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-830 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-831 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-832 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-833 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-834 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-835 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-836 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-837 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-838 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-839 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-840 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-841 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-842 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-843 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-844 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-845 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-846 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-847 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-848 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-849 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-850 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-851 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-852 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-853 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-854 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-855 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-856 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-857 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-858 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-859 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-860 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-861 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-862 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-863 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-864 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-865 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-866 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-867 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-868 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-869 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-870 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-871 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-872 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-873 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-874 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-875 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-876 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-877 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-878 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-879 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-880 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-881 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-882 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-883 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-884 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-885 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-886 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-887 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-888 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-889 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-890 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-891 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-892 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-893 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-894 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-895 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-896 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-897 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-898 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-899 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1500 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1501 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1502 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1503 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1504 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1505 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1506 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1507 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1508 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1509 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1510 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1511 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1512 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1513 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1514 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1515 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1516 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1517 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1518 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1519 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1520 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1521 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1522 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1523 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1524 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1525 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1526 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1527 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1528 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1529 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1530 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1531 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1532 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1533 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1534 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1535 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1536 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1537 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1538 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1539 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1540 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1541 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1542 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1543 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1544 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1545 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1546 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1547 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1548 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1549 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1550 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1551 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1552 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1553 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1554 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1555 FAILED
Cannot run commands in the mode at this moment. Please try ag"""
        handler = self._get_handler()
        handler.resource_name = resource_name
        responce_template = '{0}-{1}-{2}'.format(resource_name.replace(' ', '_')[:23], config_type, '\d+\-\d+')
        handler.cli.send_command = MagicMock(return_value=output)
        try:
            responce = handler.save_configuration('tftp://10.10.10.10/CloudShell/Configs/Gold/Test1/',
                                              config_type, 'management')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertTrue(e.message != '')

    def test_save_cisco_n6k_success_customer_report(self):
        resource_name = 'Very_long name with Spaces'
        config_type = 'running'
        output = """
Trying to connect to tftp server......
Connection to Server Established.

[                         ]         0.50KB
[#                        ]         4.50KB
 [##                       ]         8.50KB
  [###                      ]        12.50KB
   [####                     ]        16.50KB
    [#####                    ]        20.50KB
     [######                   ]        24.50KB
      [#######                  ]        28.50KB
       [########                 ]        32.50KB
        [#########                ]        36.50KB

         TFTP get operation was successful
         ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name temp FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-800 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-801 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-802 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-803 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-804 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-805 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-806 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-807 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-808 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-809 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-810 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-811 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-812 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-813 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-814 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-815 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-816 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-817 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-818 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-819 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-820 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-821 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-822 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-823 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-824 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-825 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-826 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-827 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-828 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-829 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-830 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-831 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-832 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-833 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-834 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-835 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-836 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-837 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-838 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-839 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-840 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-841 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-842 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-843 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-844 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-845 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-846 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-847 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-848 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-849 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-850 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-851 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-852 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-853 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-854 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-855 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-856 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-857 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-858 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-859 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-860 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-861 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-862 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-863 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-864 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-865 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-866 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-867 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-868 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-869 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-870 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-871 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-872 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-873 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-874 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-875 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-876 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-877 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-878 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-879 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-880 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-881 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-882 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-883 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-884 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-885 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-886 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-887 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-888 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-889 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-890 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-891 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-892 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-893 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-894 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-895 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-896 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-897 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-898 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name quali-899 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1500 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1501 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1502 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1503 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1504 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1505 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1506 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1507 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1508 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1509 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1510 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1511 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1512 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1513 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1514 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1515 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1516 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1517 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1518 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1519 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1520 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1521 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1522 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1523 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1524 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1525 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1526 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1527 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1528 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1529 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1530 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1531 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1532 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1533 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1534 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1535 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1536 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1537 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1538 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1539 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1540 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1541 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1542 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1543 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1544 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1545 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1546 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1547 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1548 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1549 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1550 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1551 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1552 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1553 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1554 FAILED
Cannot run commands in the mode at this moment. Please try again.
ERROR: VLAN with the same name exists

ERROR : cli_process_vlan_config_exit(283), command name GCP_user_vlan_1555 FAILED
Cannot run commands in the mode at this moment. Please try again.
Copy complete, now saving to disk (please wait)..."""
        self.output = output
        handler = self._get_handler()
        handler.cli.send_command = MagicMock
        handler.cli.send_command = self.return_output
        handler.resource_name = resource_name
        responce_template = '{0}-{1}-{2}'.format(resource_name.replace(' ', '_')[:23], config_type, '\d+\-\d+')
        responce = handler.save_configuration('tftp://10.10.10.10/CloudShell/Configs/Gold/Test1/',
                                                  config_type, 'management')
        self.assertIsNotNone(responce)
        self.assertTrue(re.search(responce_template, responce))
