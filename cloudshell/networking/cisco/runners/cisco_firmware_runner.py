from cloudshell.api.cloudshell_api import CloudShellAPISession

from cloudshell.core.logger import qs_logger
from cloudshell.cli.cli import CLI
from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flow.cisco_load_firmware_flow import CiscoLoadFirmwareFlow
from cloudshell.networking.devices.runners.firmware_runner import FirmwareRunner
from cloudshell.shell.core.context import ResourceCommandContext


class CiscoFirmwareRunner(FirmwareRunner):
    RELOAD_TIMEOUT = 500

    def __init__(self, cli, logger, api, context):
        """Handle firmware upgrade process

        :param CLI cli: Cli object
        :param qs_logger logger: logger
        :param CloudShellAPISession api: cloudshell api object
        :param ResourceCommandContext context: command context
        """

        super(CiscoFirmwareRunner, self).__init__(logger)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._load_firmware_flow = CiscoLoadFirmwareFlow(self._cli_handler, self._logger)
