#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.cisco.cisco_command_actions import CiscoCommandActions
from cloudshell.networking.devices.flows.action_flows import AddVlanFlow


class CiscoAddVlanFlow(AddVlanFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoAddVlanFlow, self).__init__(cli_handler, logger)
        self._mode = self._cli_handler
        self._command_actions = CiscoCommandActions()

    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        self._logger.info(self.__class__.__name__, "Add VLAN(s) {} configuration started".format(vlan_range))
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                self._command_actions.create_vlan(config_session, self._logger, vlan_range, port_mode, qnq, c_tag)

            current_config = self._command_actions.get_current_interface_config(session, logger=self._logger,
                                                                                port_name=port_name)
            with session.enter_mode(self._cli_handler.config_mode) as config_sesison:
                self._command_actions.clean_interface_switchport_config(config_session=config_sesison,
                                                                        current_config=current_config,
                                                                        logger=self._logger,
                                                                        port_name=port_name)
                self._command_actions.set_vlan_to_interface(config_sesison, self._logger, vlan_range, port_mode,
                                                            port_name, qnq, c_tag)
            current_config = self._command_actions.get_current_interface_config(session, logger=self._logger,
                                                                                port_name=port_name)
            if not self._command_actions.verify_interface_configured(vlan_range, current_config):
                raise Exception(self.__class__.__name__, "[FAIL] VLAN(s) {} configuration failed".format(vlan_range))
            self._logger.info("VLAN(s) {} configuration completed successfully".format(vlan_range))
            return "[ OK ] VLAN(s) {} configuration completed successfully".format(vlan_range)
