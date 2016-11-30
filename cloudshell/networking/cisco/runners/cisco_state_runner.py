from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.devices.runners.state_runner import StateRunner


class CiscoStateRunner(StateRunner):
    def __init__(self, cli, logger, api, context):
        """

        :param cli:
        :param logger:
        :param api:
        :param context:
        """

        super(CiscoStateRunner, self).__init__(logger, api, context)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
