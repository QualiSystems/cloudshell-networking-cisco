#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.firmware_runner import FirmwareRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flows.cisco_load_firmware_flow import CiscoLoadFirmwareFlow


class CiscoFirmwareRunner(FirmwareRunner):
    RELOAD_TIMEOUT = 500

    def __init__(self, cli, logger, resource_config, api):
        """Handle firmware upgrade process

        :param CLI cli: Cli object
        :param qs_logger logger: logger
        :param CloudShellAPISession api: cloudshell api object
        :param GenericNetworkingResource resource_config:
        """

        super(CiscoFirmwareRunner, self).__init__(logger)
        self.cli = cli
        self.api = api
        self.resource_config = resource_config

    @property
    def cli_handler(self):
        return CiscoCliHandler(self.cli, self.resource_config, self._logger, self.api)

    @property
    def load_firmware_flow(self):
        return CiscoLoadFirmwareFlow(self.cli_handler, self._logger)
