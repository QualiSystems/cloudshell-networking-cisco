#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import AddVlanFlow
from cloudshell.networking.cisco.command_actions.add_remove_vlan_actions import AddRemoveVlanActions
from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions


class CiscoAddVlanFlow(AddVlanFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoAddVlanFlow, self).__init__(cli_handler, logger)

    def _get_vlan_actions(self, config_session):
        return AddRemoveVlanActions(config_session, self._logger)

    def _get_iface_actions(self, config_session):
        return IFaceActions(config_session, self._logger)

    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        """ Configures VLANs on multiple ports or port-channels

        :param vlan_range: VLAN or VLAN range
        :param port_mode: mode which will be configured on port. Possible Values are trunk and access
        :param port_name: full port name
        :param qnq:
        :param c_tag:
        :return:
        """

        self._logger.info("Add VLAN(s) {} configuration started".format(vlan_range))

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as config_session:
            iface_action = self._get_iface_actions(config_session)
            vlan_actions = self._get_vlan_actions(config_session)
            port_name = iface_action.get_port_name(port_name)
            vlan_actions.create_vlan(vlan_range)

            current_config = iface_action.get_current_interface_config(port_name)

            iface_action.enter_iface_config_mode(port_name)
            iface_action.clean_interface_switchport_config(current_config)
            vlan_actions.set_vlan_to_interface(vlan_range, port_mode, port_name, qnq, c_tag)
            current_config = iface_action.get_current_interface_config(port_name)
            if not vlan_actions.verify_interface_configured(vlan_range, current_config):
                raise Exception(self.__class__.__name__, "[FAIL] VLAN(s) {} configuration failed".format(vlan_range))

        self._logger.info("VLAN(s) {} configuration completed successfully".format(vlan_range))
        return "[ OK ] VLAN(s) {} configuration completed successfully".format(vlan_range)
