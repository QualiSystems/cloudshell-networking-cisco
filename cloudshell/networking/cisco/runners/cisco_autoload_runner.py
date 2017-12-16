#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.autoload_runner import AutoloadRunner

from cloudshell.networking.cisco.flows.cisco_autoload_flow import CiscoSnmpAutoloadFlow


class CiscoAutoloadRunner(AutoloadRunner):
    def __init__(self, logger, resource_config, snmp_handler):
        super(CiscoAutoloadRunner, self).__init__(resource_config)
        self._logger = logger
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        return CiscoSnmpAutoloadFlow(self.snmp_handler, self._logger)
