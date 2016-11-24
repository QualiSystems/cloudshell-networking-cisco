from cloudshell.api.cloudshell_api import CloudShellAPISession

from cloudshell.core.logger import qs_logger
from cloudshell.cli.cli import CLI
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.cisco_command_modes import get_session, EnableCommandMode, ConfigCommandMode
from cloudshell.networking.cisco.cisco_configuration_operations import CiscoConfigurationOperations
from cloudshell.networking.cisco.flow.cisco_load_firmware_flow import CiscoLoadFirmwareFlow
from cloudshell.networking.cisco.runners.cisco_state_operations import CiscoStateOperations
from cloudshell.networking.cisco.firmware_data.cisco_firmware_data import CiscoFirmwareData
from cloudshell.networking.devices.networking_utils import UrlParser
from cloudshell.networking.operations.interfaces.firmware_operations_interface import FirmwareOperationsInterface
from cloudshell.shell.core.context import ResourceCommandContext


def _remove_old_boot_system_config(session):
    """Clear boot system parameters in current configuration
    """

    data = session.send_command('do show run | include boot')
    start_marker_str = 'boot-start-marker'
    index_begin = data.find(start_marker_str)
    index_end = data.find('boot-end-marker')

    if index_begin == -1 or index_end == -1:
        return

    data = data[index_begin + len(start_marker_str):index_end]
    data_list = data.split('\n')

    for line in data_list:
        if line.find('boot system') != -1:
            session.send_command(command='no ' + line, expected_str='(config)#')


class CiscoFirmwareOperations(FirmwareOperationsInterface):
    RELOAD_TIMEOUT = 500

    def __init__(self, cli, logger, api, context):
        """Handle firmware upgrade process

        :param CLI cli: Cli object
        :param qs_logger logger: logger
        :param CloudShellAPISession api: cloudshell api object
        :param ResourceCommandContext context: command context
        """

        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._logger = logger
        self._load_firmware_flow = CiscoLoadFirmwareFlow(self._cli_handler, self._logger)

    def load_firmware(self, path, vrf_management_name=None):
        """Update firmware version on device by loading provided image, performs following steps:

            1. Copy bin file from remote tftp server.
            2. Clear in run config boot system section.
            3. Set downloaded bin file as boot file and then reboot device.
            4. Check if firmware was successfully installed.

        :param path: full path to firmware file on ftp/tftp location
        :param vrf_management_name: VRF Name
        :return: status / exception
        """

        url = UrlParser.parse_url(path)
        required_keys = [UrlParser.FILENAME, UrlParser.HOSTNAME, UrlParser.SCHEME]

        if not url or not all(key in url for key in required_keys):
            raise Exception('CiscoFirmwareOperations', 'Path is wrong or empty')

        self._load_firmware_flow.execute_flow(path, vrf_management_name, self.RELOAD_TIMEOUT)

