#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.devices.flows.action_flows import RemoveVlanFlow


class CiscoRemoveVlanFlow(RemoveVlanFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoRemoveVlanFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        self._logger.info(self.__class__.__name__, "Remove Vlan {} configuration started".format(vlan_range))
        with self._cli_handler.get_cli_operations(self._cli_handler.enable_mode) as session:
            current_config = self._command_actions.get_current_interface_config(session, logger=self._logger,
                                                                                port_name=port_name)
            with session.enter_mode(self._cli_handler.config_mode) as config_sesison:
                self._command_actions.clean_interface_switchport_config(config_session=config_sesison,
                                                                        current_config=current_config,
                                                                        logger=self._logger,
                                                                        port_name=port_name)
            current_config = self._command_actions.get_current_interface_config(session, logger=self._logger,
                                                                                port_name=port_name)
            if self._command_actions.verify_interface_configured(vlan_range, current_config):
                raise Exception(self.__class__.__name__, "[FAIL] VLAN(s) {} removing failed".format(vlan_range))
            self._logger.info("VLAN(s) {} removing completed successfully".format(vlan_range))
            return "[ OK ] VLAN(s) {} removing completed successfully".format(vlan_range)
