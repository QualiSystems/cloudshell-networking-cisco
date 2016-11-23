from cloudshell.networking.cisco.cisco_command_actions import CiscoCommandActions
from cloudshell.networking.devices.flows.configuration_flows import AddVlanFlow


class CiscoAddVlanFlow(AddVlanFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoAddVlanFlow, self).__init__(cli_handler, logger)
        self._mode = self._cli_handler
        self._command_actions = CiscoCommandActions()
