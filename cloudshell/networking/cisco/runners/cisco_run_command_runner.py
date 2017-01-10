from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.devices.runners.run_command_runner import RunCommandRunner


class CiscoRunCommandRunner(RunCommandRunner):
    def __init__(self, cli, context, logger, api):
        """Create CiscoRunCommandOperations

        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        super(CiscoRunCommandRunner, self).__init__(logger)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
