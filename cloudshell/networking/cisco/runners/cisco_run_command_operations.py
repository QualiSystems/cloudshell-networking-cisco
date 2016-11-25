from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.devices.flows.action_flows import RunCommandFlow
from cloudshell.networking.devices.runners.interfaces.run_command_interface import RunCommandInterface


class CiscoRunCommandOperations(RunCommandInterface):
    def __init__(self, cli, context, logger, api):
        """Create CiscoRunCommandOperations

        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._logger = logger
        self._run_command_flow = RunCommandFlow(self._cli_handler, self._logger)

    def run_custom_command(self, custom_command):
        return self._run_command_flow.execute_flow(custom_command=custom_command)

    def run_custom_config_command(self, custom_command):
        return self._run_command_flow.execute_flow(custom_command=custom_command, is_config=True)
