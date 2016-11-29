from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flow.cisco_restore_flow import CiscoRestoreFlow
from cloudshell.networking.cisco.flow.cisco_save_flow import CiscoSaveFlow
from cloudshell.networking.devices.runners.configuration_runner import ConfigurationRunner


class CiscoConfigurationRunner(ConfigurationRunner):
    def __init__(self, cli, logger, context, api):
        super(CiscoConfigurationRunner, self).__init__(logger, context, api)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._save_flow = CiscoSaveFlow(cli_handler=self._cli_handler,
                                        logger=self._logger)
        self._restore_flow = CiscoRestoreFlow(cli_handler=self._cli_handler,
                                              logger=self._logger)
        self.file_system = 'flash:'
