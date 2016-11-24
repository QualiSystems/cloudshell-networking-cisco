from collections import OrderedDict
import time
from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.devices.runners.state_operations import StateOperations


class CiscoStateOperations(StateOperations):
    def __init__(self, cli, logger, api, context):
        """

        :param cli:
        :param logger:
        :param api:
        :param context:
        """

        super(CiscoStateOperations, self).__init__(logger, api, context)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._logger = logger
