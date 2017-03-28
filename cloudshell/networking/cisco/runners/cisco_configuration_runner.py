#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flows.cisco_restore_flow import CiscoRestoreFlow
from cloudshell.networking.cisco.flows.cisco_save_flow import CiscoSaveFlow


class CiscoConfigurationRunner(ConfigurationRunner):
    def __init__(self, cli, logger, resource_config, api):
        super(CiscoConfigurationRunner, self).__init__(logger, resource_config, api)
        self._cli = cli

    @property
    def cli_handler(self):
        """ CLI Handler property
        :return: CLI handler
        """
        return CiscoCliHandler(self._cli, self.resource_config, self._logger, self._api)

    @property
    def restore_flow(self):
        return CiscoRestoreFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def save_flow(self):
        return CiscoSaveFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def file_system(self):
        return "flash:"
