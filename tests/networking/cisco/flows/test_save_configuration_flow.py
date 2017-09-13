from unittest import TestCase

from mock import MagicMock
from cloudshell.networking.cisco.flows.cisco_save_flow import CiscoSaveFlow


class TestCiscoSaveConfigurationFlow(TestCase):
    def _get_handler(self, output):
        cli = MagicMock()
        self.session = MagicMock()
        self.session.send_command.return_value = output
        cliservice = MagicMock()
        cliservice.__enter__.return_value = self.session
        cli.get_cli_service.return_value = cliservice
        logger = MagicMock()
        return CiscoSaveFlow(cli_handler=cli, logger=logger)

    def test_save_configuration(self):
        save_flow = self._get_handler("""N5K-L3-Sw1#
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
         N5K-L3-Sw1#""")

        save_flow.execute_flow('tftp://127.0.0.1', 'startup')
        self.session.send_command.assert_called_once()

    def test_save_configuration_with_vrf(self):
        save_flow = self._get_handler("""N5K-L3-Sw1#
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
         N5K-L3-Sw1#""")

        save_flow.execute_flow('tftp://127.0.0.1', 'running', vrf_management_name='management')
        self.session.send_command.assert_called_once()
