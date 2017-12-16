#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flows.cisco_disable_snmp_flow import CiscoDisableSnmpFlow
from cloudshell.networking.cisco.flows.cisco_enable_snmp_flow import CiscoEnableSnmpFlow
from cloudshell.devices.snmp_handler import SnmpHandler


class CiscoSnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        super(CiscoSnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        return CiscoEnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return CiscoDisableSnmpFlow(self.cli_handler, self._logger)
