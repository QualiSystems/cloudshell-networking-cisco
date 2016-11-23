from cloudshell.networking.cisco.cisco_command_actions import CiscoCommandActions
from cloudshell.networking.devices.flows.configuration_flows import RestoreConfigurationFlow


class CiscoRestoreFlow(RestoreConfigurationFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoRestoreFlow, self).__init__(cli_handler, logger)
        self._command_actions = CiscoCommandActions()
