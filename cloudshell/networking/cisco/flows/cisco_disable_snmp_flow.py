#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.networking.cisco.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters


class CiscoDisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
          Enable snmp flow
          :param cli_handler:
          :type cli_handler: JuniperCliHandler
          :param logger:
          :return:
          """
        super(CiscoDisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters=None):

        if not isinstance(snmp_parameters, SNMPV2Parameters):
            self._logger.debug("Unsupported SNMP version. Disable SNMP skipped")

        with self._cli_handler.config_mode_service() as session:
            snmp_actions = EnableDisableSnmpActions(session, self._logger)
            self._logger.debug("Start Disable SNMP")
            snmp_actions.disable_snmp(snmp_parameters.snmp_community)
