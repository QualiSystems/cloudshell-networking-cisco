#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.networking.cisco.command_templates import (
    add_remove_vlan,
    configuration,
    iface,
)


class IFaceActions(object):
    def __init__(self, cli_service, logger):
        """Add remove vlan.

        :param cli_service: config mode cli_service
        :type cli_service: cloudshell.cli.service.cli_service_impl.CliServiceImpl
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def get_port_name(self, port):
        """Get port name from port resource full name.

        :param port: port resource full address
            (PerfectSwitch/Chassis 0/FastEthernet0-23)
        :return: port name (FastEthernet0/23)
        :rtype: string
        """
        if not port:
            err_msg = "Failed to get port name."
            self._logger.error(err_msg)
            raise Exception("get_port_name", err_msg)

        temp_port_name = port.split("/")[-1]
        if "port-channel" not in temp_port_name.lower():
            temp_port_name = temp_port_name.replace("-", "/")

            self._logger.info(
                "Interface name validation OK, portname = {0}".format(temp_port_name)
            )
        return temp_port_name

    def get_current_interface_config(self, port_name, action_map=None, error_map=None):
        """Retrieve current interface configuration.

        :param port_name:
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return: str
        """
        return CommandTemplateExecutor(
            self._cli_service,
            iface.SHOW_RUNNING,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(port_name=port_name)

    def get_sub_interfaces_config(self, port_name, action_map=None, error_map=None):
        """Retrieve current interface configuration.

        :param port_name:
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return: str
        """
        result = CommandTemplateExecutor(
            self._cli_service,
            iface.SHOW_RUNNING_SUB_INTERFACES,
            action_map=action_map,
            error_map=error_map,
            remove_prompt=True,
        ).execute_command(port_name=port_name)

        return [
            x.replace(" ", "").replace("interface", "")
            for x in result.lower().split("\n")
            if x.strip(" ").startswith("interface")
        ]

    def enter_iface_config_mode(self, port_name):
        """Enter configuration mode for specific interface.

        :param port_name: interface name
        :return:
        """
        CommandTemplateExecutor(
            self._cli_service, iface.CONFIGURE_INTERFACE
        ).execute_command(port_name=port_name)

    def clean_interface_switchport_config(
        self, current_config, action_map=None, error_map=None
    ):
        """Remove current switchport configuration from interface.

        :param current_config: current interface configuration
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        self._logger.debug("Start cleaning interface switchport configuration")

        for line in current_config.splitlines():
            if line.strip(" ").startswith("switchport "):
                line_to_remove = re.sub(r"\s+\d+[-\d+,]+", "", line).strip(" ")
                CommandTemplateExecutor(
                    self._cli_service,
                    configuration.NO,
                    action_map=action_map,
                    error_map=error_map,
                ).execute_command(command=line_to_remove)
        if "switchport mode dot1q-tunnel" in current_config.lower():
            self._get_no_l2_protocol_tunnel_cmd(action_map, error_map).execute_command()
        self._logger.debug("Completed cleaning interface switchport configuration")

    def _get_no_l2_protocol_tunnel_cmd(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            self._cli_service,
            add_remove_vlan.NO_L2_TUNNEL,
            action_map=action_map,
            error_map=error_map,
        )

    def clean_vlan_sub_iface_config(self, port_name, action_map=None, error_map=None):
        """Remove current switchport configuration from interface.

        :param port_name: interface name
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        self._logger.debug("Start cleaning interface switchport configuration")
        if self.check_sub_interface_has_vlan(port_name):
            CommandTemplateExecutor(
                self._cli_service,
                iface.NO_INTERFACE,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(interface_name=port_name)

            self._logger.debug("Completed cleaning vlan sub interface configuration")

    def check_sub_interface_has_vlan(
        self, interface_name, action_map=None, error_map=None
    ):
        current_config = self.get_current_interface_config(interface_name)
        return any(
            x
            for x in current_config.splitlines()
            if x.strip(" ").startswith("encapsulation ")
        )
