from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flow import CiscoSaveFlow
from cloudshell.networking.cisco.flow.cisco_restore_flow import CiscoRestoreFlow
from cloudshell.networking.devices.runners.configuration_operations import ConfigurationOperations


class CiscoConfigurationOperations(ConfigurationOperations):
    def __init__(self, cli, logger, context, api):
        super(CiscoConfigurationOperations, self).__init__(logger, context, api)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._save_flow = CiscoSaveFlow(cli_handler=self._cli_handler,
                                        logger=self._logger,
                                        resource_name=self._resource_name)
        self._restore_flow = CiscoRestoreFlow(cli_handler=self._cli_handler,
                                              logger=self._logger)

    # def save_configuration(self, folder_path, configuration_type=None, vrf_management_name=None):
    #     """Proxy method for Save command, to modify output according to networking standard
    #
    #     :param folder_path:  tftp/ftp server where file be saved
    #     :param configuration_type: type of configuration that will be saved (StartUp or Running)
    #     :param vrf_management_name: Virtual Routing and Forwarding management nam
    #     :return:
    #     """
    #     response = CiscoSaveFlow(self._cli_handler)
    #     return response.identifier.split('/')[-1]
