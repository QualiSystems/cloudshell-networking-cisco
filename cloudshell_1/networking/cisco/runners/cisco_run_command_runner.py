#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.run_command_runner import RunCommandRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler


class CiscoRunCommandRunner(RunCommandRunner):
    def __init__(self, cli, resource_config, logger, api):
        """Create CiscoRunCommandOperations

        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        super(CiscoRunCommandRunner, self).__init__(logger)
        self.cli = cli
        self.api = api
        self.resource_config = resource_config

    @property
    def cli_handler(self):
        return CiscoCliHandler(self.cli, self.resource_config, self._logger, self.api)
