#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.autoload_runner import AutoloadRunner

from cloudshell.networking.cisco.flows.cisco_autoload_flow import CiscoSnmpAutoloadFlow
from cloudshell.networking.cisco.snmp.cisco_snmp_handler import CiscoSnmpHandler


class CiscoAutoloadRunner(AutoloadRunner):
    def __init__(self, cli, logger, resource_config, api):
        super(CiscoAutoloadRunner, self).__init__(resource_config)
        self._cli = cli
        self._api = api
        self._logger = logger

    @property
    def snmp_handler(self):
        return CiscoSnmpHandler(self._cli, self.resource_config, self._logger, self._api)

    @property
    def autoload_flow(self):
        return CiscoSnmpAutoloadFlow(self.snmp_handler, self._logger)
