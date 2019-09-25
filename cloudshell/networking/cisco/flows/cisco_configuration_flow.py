#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.shell.flows.configuration.basic_flow import AbstractConfigurationFlow

from cloudshell.networking.cisco.cisco_constants import DEFAULT_FILE_SYSTEM
from cloudshell.networking.cisco.command_actions.system_actions import SystemActions


class CiscoConfigurationFlow(AbstractConfigurationFlow):
    STARTUP_CONFIG_NAME = "startup_config"
    STARTUP_LOCATION = "nvram:startup_config"

    def __init__(self, cli_handler, resource_config, logger):
        super(CiscoConfigurationFlow, self).__init__(logger, resource_config)
        self._cli_handler = cli_handler

    @property
    def _file_system(self):
        return DEFAULT_FILE_SYSTEM

    def _save_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """Execute flow which save selected file to the provided destination.

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """
        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            save_action = SystemActions(enable_session, self._logger)
            action_map = save_action.prepare_action_map(configuration_type, folder_path)
            save_action.copy(
                configuration_type,
                folder_path,
                vrf=vrf_management_name,
                action_map=action_map,
            )

    def _restore_flow(
        self, path, configuration_type, restore_method, vrf_management_name
    ):
        """Execute flow which save selected file to the provided destination.

        :param path: the path to the configuration file, including the configuration
            file name
        :param restore_method: the restore method to use when restoring the
            configuration file. Possible Values are append and override
        :param configuration_type: the configuration type to restore.
            Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """
        if "-config" not in configuration_type:
            configuration_type += "-config"

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            restore_action = SystemActions(enable_session, self._logger)
            copy_action_map = restore_action.prepare_action_map(
                path, configuration_type
            )

            if "startup" in configuration_type:
                if restore_method == "override":
                    del_action_map = {
                        "[Dd]elete [Ff]ilename ": lambda s, l: s.send_line(
                            self.STARTUP_CONFIG_NAME, l
                        )
                    }
                    restore_action.delete_file(
                        path=self.STARTUP_LOCATION, action_map=del_action_map
                    )
                    restore_action.copy(
                        path,
                        configuration_type,
                        vrf=vrf_management_name,
                        action_map=copy_action_map,
                    )
                else:
                    restore_action.copy(
                        path,
                        configuration_type,
                        vrf=vrf_management_name,
                        action_map=copy_action_map,
                    )

            elif "running" in configuration_type:
                if restore_method == "override":
                    restore_action.override_running(path)
                else:
                    restore_action.copy(
                        path,
                        configuration_type,
                        vrf=vrf_management_name,
                        action_map=copy_action_map,
                    )
