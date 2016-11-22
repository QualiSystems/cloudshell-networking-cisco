import time
from collections import OrderedDict
from posixpath import join
import re

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_command_modes import EnableCommandMode, ConfigCommandMode, get_session
from cloudshell.networking.cisco.new.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.new.flow.save_configuration_flow import CiscoSaveFlow
from cloudshell.networking.devices.operations.configuration_operations import ConfigurationOperations
from cloudshell.shell.core.interfaces.save_restore import OrchestrationSavedArtifact


class CiscoConfigurationOperations(ConfigurationOperations):
    def __init__(self, cli, logger, context):
        super(CiscoConfigurationOperations, self).__init__(logger, context)
        self._cli_handler = CiscoCliHandler(cli, context, logger)
        self._save_flow = CiscoSaveFlow(cli_handler=self._cli_handler,
                                        logger=self._logger,
                                        resource_name=self._resource_name)

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
