#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.networking.cisco.cisco_command_actions import get_port_name, get_current_interface_config, \
    clean_interface_switchport_config, verify_interface_configured

from cloudshell.networking.devices.flows.action_flows import RemoveVlanFlow


class CiscoRemoveVlanFlow(RemoveVlanFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoRemoveVlanFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        """ Remove configuration of VLANs on multiple ports or port-channels

        :param vlan_range: VLAN or VLAN range
        :param port_name: full port name
        :param port_mode: mode which will be configured on port. Possible Values are trunk and access
        :param action_map:
        :param error_map:
        :return:
        """

        port_name = get_port_name(self._logger, port_name)
        self._logger.info("Remove Vlan {} configuration started".format(vlan_range))
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
            current_config = get_current_interface_config(session, logger=self._logger,
                                                          port_name=port_name)
            with session.enter_mode(self._cli_handler.config_mode) as config_sesison:
                clean_interface_switchport_config(config_session=config_sesison,
                                                  current_config=current_config,
                                                  logger=self._logger,
                                                  port_name=port_name)
            current_config = get_current_interface_config(session, logger=self._logger,
                                                          port_name=port_name)
            if verify_interface_configured(vlan_range, current_config):
                raise Exception(self.__class__.__name__, "[FAIL] VLAN(s) {} removing failed".format(vlan_range))
            self._logger.info("VLAN(s) {} removing completed successfully".format(vlan_range))
            return "[ OK ] VLAN(s) {} removing completed successfully".format(vlan_range)
