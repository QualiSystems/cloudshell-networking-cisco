#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow
from cloudshell.networking.cisco.command_actions.system_actions import SystemActions


class CiscoSaveFlow(SaveConfigurationFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoSaveFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            save_action = SystemActions(enable_session, self._logger)
            action_map = save_action.prepare_action_map(configuration_type, folder_path)
            save_action.copy(configuration_type,
                             folder_path,
                             vrf=vrf_management_name,
                             action_map=action_map)
