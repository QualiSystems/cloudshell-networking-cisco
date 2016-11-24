from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flow.cisco_run_command_flow import CiscoRunCustomCommand
from cloudshell.networking.devices.operations.interfaces.run_command_interface import RunCommandInterface


class CiscoRunCommandOperations(RunCommandInterface):
    def __init__(self, cli, context, logger, api):
        """Create CiscoIOSHandlerBase

        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._logger = logger
        self._run_command_flow = CiscoRunCustomCommand(self._cli_handler, self._logger)

    def run_custom_command(self, command):
        return self._run_command_flow.execute_flow(custom_command=command)

    def run_custom_config_command(self, command):
        return self._run_command_flow.execute_flow(custom_command=command, is_config=True)
