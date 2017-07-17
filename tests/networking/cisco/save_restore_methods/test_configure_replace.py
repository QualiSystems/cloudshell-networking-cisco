from unittest import TestCase
from cloudshell.networking.cisco.command_templates.configuration import CONFIGURE_REPLACE


class CiscoConfigurationOperationsRestore(TestCase):

    def setUp(self):
        self.path = "ftp://admin:KPlab123@10.233.30.222/CloudShell/config"

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
        configure_replace = CONFIGURE_REPLACE.get_command(path=self.path)
        self.assertRegexpMatches(output, "|".join(configure_replace['error_map'].keys()))

    def test_configure_replace_ignores_rollback_done_output(self):
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
        configure_replace = CONFIGURE_REPLACE.get_command(path=self.path)
        self.assertNotRegexpMatches(output, "|".join(configure_replace['error_map'].keys()))

    def test_configure_replace_validates_rollback_aborted_output(self):
        output = """configure replace flash:candidate_config.txt force
            The rollback configlet from the last pass is listed below:
            ********
            !List of Rollback Commands:
            adfjasdfadfa
            end
            ********
            Rollback aborted after 5 passes
            The following commands are failed to apply to the IOS image.
            ********
            adfjasdfadfa
            ********
            """
        configure_replace = CONFIGURE_REPLACE.get_command(path=self.path)
        self.assertRegexpMatches(output, "|".join(configure_replace['error_map'].keys()))

    def test_configure_replace_validates_aborting_rollback_output(self):
        output = """configure replace flash:candidate_config.txt force revert trigger error
            Failed to apply command adfjasdfadfa
            Aborting Rollback.
            Rollback failed.Reverting back to the original configuration: flash:pynet-rtr1-cfgJan--6-12-49-44.412-PST-0
            Total number of passes: 1
            Rollback Done
            """
        configure_replace = CONFIGURE_REPLACE.get_command(path=self.path)
        self.assertRegexpMatches(output, "|".join(configure_replace['error_map'].keys()))
