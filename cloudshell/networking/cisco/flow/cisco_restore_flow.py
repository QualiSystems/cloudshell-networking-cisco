#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from cloudshell.networking.cisco.cisco_command_actions import CiscoCommandActions
from cloudshell.networking.devices.flows.action_flows import RestoreConfigurationFlow


class CiscoRestoreFlow(RestoreConfigurationFlow):
    STARTUP_LOCATION = "nvram:startup_config"

    def __init__(self, cli_handler, logger):
        super(CiscoRestoreFlow, self).__init__(cli_handler, logger)
        self._command_actions = CiscoCommandActions()

    def execute_flow(self, path, restore_method, configuration, vrf):
        if "-config" not in configuration:
            configuration += "-config"

        with self._cli_handler.get_cli_operations(self._cli_handler.enable_mode) as enable_session:
            if configuration == "startup":
                if restore_method == "override":
                    action_map = OrderedDict({
                        "[Dd]elete [Ff]ilename ": lambda session, logger: session.send_line(configuration, logger)})
                    self._command_actions.delete_file(session=enable_session, logger=self._logger,
                                                      path=self.STARTUP_LOCATION, action_map=action_map)
                    self._command_actions.copy(enable_session, path, restore_method, configuration, vrf)
                else:
                    self._command_actions.copy(enable_session, path, restore_method, configuration, vrf)

            if configuration == "running":
                if restore_method == "override":
                    self._command_actions.override_running(enable_session, path)
                else:
                    self._command_actions.copy(enable_session, path, restore_method, configuration, vrf)
