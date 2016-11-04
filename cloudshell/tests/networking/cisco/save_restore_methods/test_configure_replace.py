from unittest import TestCase
from mock import MagicMock
from cloudshell.networking.cisco.cisco_configuration_operations import CiscoConfigurationOperations
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails


class CiscoConfigurationOperationsRestore(TestCase):
    def _get_handler(self, output):
        self.output = """C6504e-1-CE7#copy running-config tftp:
        Address or name of remote host []? 10.10.10.10
        Destination filename [c6504e-1-ce7-confg]? 6504e1
        !!
        23518 bytes copied in 0.904 secs (26015 bytes/sec)
        C6504e-1-CE7#"""
        cli = MagicMock()
        session = MagicMock()
        session.send_command.return_value = output
        cliservice = MagicMock()
        cliservice.__enter__.return_value = session
        cli.get_session.return_value = cliservice
        api = MagicMock()
        logger = MagicMock()
        context = ResourceCommandContext()
        context.resource = ResourceContextDetails()
        context.resource.name = 'resource_name'
        context.reservation = ReservationContextDetails()
        context.reservation.reservation_id = 'c3b410cb-70bd-4437-ae32-15ea17c33a74'
        context.resource.attributes = dict()
        context.resource.attributes['CLI Connection Type'] = 'Telnet'
        context.resource.attributes['Sessions Concurrency Limit'] = '1'
        return CiscoConfigurationOperations(cli=cli, logger=logger, api=api, context=context)

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
        handler = self._get_handler(output)
        self.assertRaises(Exception, handler.configure_replace, 'filename')

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
        handler = self._get_handler(output)
        self.assertRaises(Exception, handler.configure_replace, 'filename')
