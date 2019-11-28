#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.networking.cisco.command_templates import add_remove_vlan, iface


class AddRemoveVlanActions(object):
    CREATE_VLAN_VALIDATION_PATTERN = re.compile(
        r"[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected", re.IGNORECASE
    )
    CREATE_VLAN_ERROR_PATTERN = re.compile(r"%.*\\.", re.IGNORECASE)

    def __init__(self, cli_service, logger):
        """Add remove vlan.

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
        """Verify interface configuration.

        :param vlan_range:
        :param current_config:
        :return: True or False
        """
        return re.search(
            r"switchport.*vlan\s+{0}$".format(str(vlan_range)),
            current_config,
            re.MULTILINE | re.IGNORECASE | re.DOTALL,
        )

    def create_vlan(self, vlan_range, action_map=None, error_map=None):
        """Create vlan entity on the device.

        :param vlan_range: range of vlans to be created
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        result = CommandTemplateExecutor(
            self._cli_service,
            add_remove_vlan.CONFIGURE_VLAN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(vlan_id=vlan_range)
        if self.CREATE_VLAN_VALIDATION_PATTERN.search(result):
            self._logger.info("Unable to create vlan, proceeding")
            return
        elif self.CREATE_VLAN_ERROR_PATTERN.search(result):
            raise Exception("Failed to configure vlan: Unable to create vlan")

        CommandTemplateExecutor(
            self._cli_service,
            iface.STATE_ACTIVE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()
        CommandTemplateExecutor(
            self._cli_service,
            iface.NO_SHUTDOWN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def set_vlan_to_interface(
        self,
        vlan_range,
        port_mode,
        port_name,
        qnq,
        c_tag,
        action_map=None,
        error_map=None,
    ):
        """Assign vlan to a certain interface.

        :param vlan_range: range of vlans to be assigned
        :param port_mode: switchport mode
        :param port_name: interface name
        :param qnq: qinq settings (dot1q tunnel)
        :param c_tag: selective qnq
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        CommandTemplateExecutor(
            self._cli_service, iface.CONFIGURE_INTERFACE
        ).execute_command(port_name=port_name)

        CommandTemplateExecutor(
            self._cli_service,
            iface.NO_SHUTDOWN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        if qnq:
            port_mode = "dot1q-tunnel"

        CommandTemplateExecutor(
            self._cli_service,
            add_remove_vlan.SWITCHPORT_MODE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        CommandTemplateExecutor(
            self._cli_service,
            add_remove_vlan.SWITCHPORT_MODE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(port_mode=port_mode)
        if qnq:
            self._get_l2_protocol_tunnel_cmd(action_map, error_map).execute_command()

        if "trunk" not in port_mode:
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.SWITCHPORT_ALLOW_VLAN,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(port_mode_access="", vlan_range=vlan_range)
        else:
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.SWITCHPORT_ALLOW_VLAN,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(port_mode_trunk="", vlan_range=vlan_range)

    def enter_interface_config_id(self, port_name, l2_transport=None):
        l2transport = None
        if l2_transport:
            l2transport = ""
        CommandTemplateExecutor(
            self._cli_service, iface.CONFIGURE_INTERFACE
        ).execute_command(port_name=port_name, l2transport=l2transport)

    def _get_l2_protocol_tunnel_cmd(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            self._cli_service,
            add_remove_vlan.L2_TUNNEL,
            action_map=action_map,
            error_map=error_map,
        )

    def set_vlan_to_sub_interface(
        self,
        vlan_range,
        port_mode,
        port_name,
        qnq,
        c_tag,
        l2_transport=None,
        is_untagged=None,
        action_map=None,
        error_map=None,
    ):
        """Assign vlan to a certain interface.

        :param vlan_range: range of vlans to be assigned
        :param port_mode: switchport mode
        :param port_name: interface name
        :param qnq: qinq settings (dot1q tunnel)
        :param c_tag: selective qnq
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        untagged = None

        if is_untagged:
            untagged = ""

        CommandTemplateExecutor(
            self._cli_service,
            iface.NO_SHUTDOWN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        if qnq:
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.VLAN_SUB_IFACE,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(vlan_id=vlan_range, qnq="")
        else:
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.VLAN_SUB_IFACE,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(vlan_id=vlan_range, untagged=untagged)

    def clean_vlan_sub_interface(self, port_name):
        CommandTemplateExecutor(
            self._cli_service, iface.REMOVE_INTERFACE
        ).execute_command(port_name=port_name)
