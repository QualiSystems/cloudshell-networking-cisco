#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.state_runner import StateRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler


class CiscoStateRunner(StateRunner):
    def __init__(self, cli, logger, api, resource_config):
        """

        :param cli:
        :param logger:
        :param api:
        :param resource_config:
        """

        super(CiscoStateRunner, self).__init__(logger, api, resource_config)
        self.cli = cli
        self.api = api

    @property
    def cli_handler(self):
        return CiscoCliHandler(self.cli, self.resource_config, self._logger, self.api)
