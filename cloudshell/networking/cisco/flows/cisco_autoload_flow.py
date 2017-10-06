#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow
from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload


class CiscoSnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snmp_service:
            cisco_snmp_autoload = CiscoGenericSNMPAutoload(snmp_service,
                                                           shell_name,
                                                           shell_type,
                                                           resource_name,
                                                           self._logger)
            return cisco_snmp_autoload.discover(supported_os)
