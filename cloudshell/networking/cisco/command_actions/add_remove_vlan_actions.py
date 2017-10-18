#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.cli.cli_service import CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.cisco.command_templates import add_remove_vlan as vlan_command_template
from cloudshell.networking.cisco.command_templates import iface as iface_command_template


class AddRemoveVlanActions(object):
    def __init__(self, cli_service, logger):
        """ Add remove vlan

        :param cli_service: config mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """

        self._cli_service = cli_service
        self._logger = logger

    @staticmethod
    def verify_interface_configured(vlan_range, current_config):
        """ Verify interface configuration

        :param vlan_range:
        :param current_config:
        :return: True or False
        """

        return re.search("switchport.*vlan.*{0}".format(str(vlan_range)), current_config,
                         re.MULTILINE | re.IGNORECASE | re.DOTALL)

    def create_vlan(self, vlan_range, action_map=None, error_map=None):
        """Create vlan entity on the device

        :param vlan_range: range of vlans to be created
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        CommandTemplateExecutor(self._cli_service,
                                vlan_command_template.CONFIGURE_VLAN,
                                action_map=action_map,
                                error_map=error_map).execute_command(vlan_id=vlan_range)

        CommandTemplateExecutor(self._cli_service,
                                iface_command_template.STATE_ACTIVE,
                                action_map=action_map,
                                error_map=error_map).execute_command()
        CommandTemplateExecutor(self._cli_service,
                                iface_command_template.NO_SHUTDOWN,
                                action_map=action_map,
                                error_map=error_map).execute_command()

    def set_vlan_to_interface(self, vlan_range, port_mode, port_name, qnq, c_tag,
                              action_map=None,
                              error_map=None):

        """Assign vlan to a certain interface

        :param vlan_range: range of vlans to be assigned
        :param port_mode: switchport mode
        :param port_name: interface name
        :param qnq: qinq settings (dot1q tunnel)
        :param c_tag: selective qnq
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        CommandTemplateExecutor(self._cli_service,
                                iface_command_template.CONFIGURE_INTERFACE).execute_command(port_name=port_name)

        CommandTemplateExecutor(self._cli_service,
                                iface_command_template.NO_SHUTDOWN,
                                action_map=action_map,
                                error_map=error_map).execute_command()

        if qnq:
            port_mode = 'dot1q-tunnel'

        CommandTemplateExecutor(self._cli_service,
                                vlan_command_template.SWITCHPORT_MODE,
                                action_map=action_map,
                                error_map=error_map).execute_command()

        CommandTemplateExecutor(self._cli_service,
                                vlan_command_template.SWITCHPORT_MODE,
                                action_map=action_map,
                                error_map=error_map).execute_command(port_mode=port_mode)
        if qnq:
            self._get_l2_protocol_tunnel_cmd(action_map, error_map).execute_command()

        if 'trunk' not in port_mode:
            CommandTemplateExecutor(self._cli_service,
                                    vlan_command_template.SWITCHPORT_ALLOW_VLAN,
                                    action_map=action_map,
                                    error_map=error_map).execute_command(port_mode_access='', vlan_range=vlan_range)
        else:
            CommandTemplateExecutor(self._cli_service,
                                    vlan_command_template.SWITCHPORT_ALLOW_VLAN,
                                    action_map=action_map,
                                    error_map=error_map).execute_command(port_mode_trunk='', vlan_range=vlan_range)

    def _get_l2_protocol_tunnel_cmd(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(self._cli_service,
                                vlan_command_template.L2_TUNNEL,
                                action_map=action_map,
                                error_map=error_map)
