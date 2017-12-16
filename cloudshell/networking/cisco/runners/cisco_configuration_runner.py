#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flows.cisco_restore_flow import CiscoRestoreFlow
from cloudshell.networking.cisco.flows.cisco_save_flow import CiscoSaveFlow


class CiscoConfigurationRunner(ConfigurationRunner):
    @property
    def restore_flow(self):
        return CiscoRestoreFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def save_flow(self):
        return CiscoSaveFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def file_system(self):
        return "flash:"
