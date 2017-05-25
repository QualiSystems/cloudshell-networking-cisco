from unittest import TestCase

from mock import MagicMock
from cloudshell.networking.cisco.command_templates.cisco_configuration_templates import CONFIGURE_REPLACE

from cloudshell.networking.cisco.runners.cisco_configuration_runner import CiscoConfigurationRunner
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails


class CiscoConfigurationOperationsRestore(TestCase):
    def test_configure_replace_validates_error_output(self):
        output = """Command: configure replace ftp://admin:KPlab123@10.233.30.222/CloudShell/configs/Base/3750-1_Catalyst37xxstack.cfg
            This will apply all necessary additions and deletions
            to replace the current running configuration with the
            contents of the specified configuration file, which is
            assumed to be a complete configuration, not a partial
            configuration. Enter Y if you are sure you want to proceed. ? [no]: y
            Loading CloudShell/configs/Base/3750-1_Catalyst37xxstack.cfg !
            [OK - 3569/4096 bytes]
            Loading CloudShell/configs/Base/3750-1_Catalyst37xxstack.cfg !
            [OK - 3569/4096 bytes]
            %The input file is not a valid config file.
            37501#
            """
        configure_replace = CONFIGURE_REPLACE.get_command(path='ftp://admin:KPlab123@10.233.30.222/CloudShell/config')
        self.assertRegexpMatches(output, "|".join(configure_replace['error_map'].keys()))

    def test_configure_replace_validates_apply_error_output(self):
        output = """configure replace ftp://admin:KPlab123@10.233.30.222/CloudShell/config
            This will apply all necessary additions and deletions
            to replace the current running configuration with the
            contents of the specified configuration file, which is
            assumed to be a complete configuration, not a partial
            configuration. Enter Y if you are sure you want to proceed. ? [no]: y
            Loading CloudShell/configs/3750.cfg !
            [OK - 8973/4096 bytes]
            Loading CloudShell/configs/3750.cfg !
            Total number of passes: 0
            Rollback Done
            37501#
            """
        configure_replace = CONFIGURE_REPLACE.get_command(path='ftp://admin:KPlab123@10.233.30.222/CloudShell/config')
        self.assertRegexpMatches(output, "|".join(configure_replace['error_map'].keys()))
