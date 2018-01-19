#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.networking.cisco.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions
from cloudshell.networking.cisco.flows.cisco_enable_snmp_flow import CiscoEnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters


class CiscoDisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger, remove_group=True):
        """
          Enable snmp flow
          :param cli_handler:
          :type cli_handler: JuniperCliHandler
          :param logger:
          :return:
          """
        super(CiscoDisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler
        self._remove_group = remove_group

    def execute_flow(self, snmp_parameters=None):
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    current_snmp_user = snmp_actions.get_current_snmp_user()
                    if snmp_parameters.snmp_user in current_snmp_user:
                        if self._remove_group:
                            snmp_actions.remove_snmp_user(snmp_parameters.snmp_user, CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP)
                            current_snmp_config = snmp_actions.get_current_snmp_config()
                            groups = re.findall(CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP, current_snmp_user)
                            if len(groups) < 2:
                                snmp_actions.remove_snmp_group(CiscoEnableSnmpFlow.DEFAULT_SNMP_GROUP)
                                if "snmp-server view {}".format(
                                        CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW) in current_snmp_config:
                                    snmp_actions.remove_snmp_view(CiscoEnableSnmpFlow.DEFAULT_SNMP_VIEW)
                        else:
                            snmp_actions.remove_snmp_user(snmp_parameters.snmp_user)

                else:
                    self._logger.debug("Start Disable SNMP")
                    snmp_actions.disable_snmp(snmp_parameters.snmp_community)
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                # Reentering config mode to perform commit for IOS-XR
                updated_snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    updated_snmp_user = updated_snmp_actions.get_current_snmp_user()
                    if snmp_parameters.snmp_user in updated_snmp_user:
                        raise Exception(self.__class__.__name__, "Failed to remove SNMP v3 Configuration." +
                                        " Please check Logs for details")
                else:
                    updated_snmp_communities = updated_snmp_actions.get_current_snmp_config()
                    if re.search("snmp-server community {}".format(snmp_parameters.snmp_community),
                                 updated_snmp_communities):
                        raise Exception(self.__class__.__name__, "Failed to remove SNMP community." +
                                        " Please check Logs for details")
