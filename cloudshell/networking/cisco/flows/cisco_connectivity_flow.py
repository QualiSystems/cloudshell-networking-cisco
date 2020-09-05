#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.shell.flows.connectivity.basic_flow import AbstractConnectivityFlow

from cloudshell.networking.cisco.command_actions.add_remove_vlan_actions import (
    AddRemoveVlanActions,
)
from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions


class CiscoConnectivityFlow(AbstractConnectivityFlow):
    CISCO_SUB_INTERFACE_ERROR = "Vlan range is not supported for IOS Router devices"

    def __init__(
        self,
        cli_handler,
        logger,
        support_vlan_range_str=False,
        support_multi_vlan_str=False,
    ):
        super(CiscoConnectivityFlow, self).__init__(logger)
        self._cli_handler = cli_handler
        self.IS_VLAN_RANGE_SUPPORTED = support_vlan_range_str
        self.IS_MULTI_VLAN_SUPPORTED = support_multi_vlan_str

    def _get_vlan_actions(self, config_session):
        return AddRemoveVlanActions(config_session, self._logger)

    def _get_iface_actions(self, config_session):
        return IFaceActions(config_session, self._logger)

    def _add_vlan_flow(self, vlan_range, port_mode, full_name, qnq, c_tag, vm_uid=None):
        """Configures VLANs on multiple ports or port-channels.

        :param vlan_range: VLAN or VLAN range
        :param port_mode: mode which will be configured on port.
            Possible Values are trunk and access
        :param port_name: full port name
        :param qnq:
        :param c_tag:
        :return:
        """
        success = True
        self._logger.info("Add VLAN(s) {} configuration started".format(vlan_range))

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            iface_action = self._get_iface_actions(config_session)
            vlan_actions = self._get_vlan_actions(config_session)
            port_name = iface_action.get_port_name(full_name)
            vlan_range = vlan_range.replace(" ", "")

            try:
                current_config = self._add_switchport_vlan(
                    vlan_actions,
                    iface_action,
                    vlan_range,
                    port_name,
                    port_mode,
                    qnq,
                    c_tag,
                )
                if not vlan_actions.verify_interface_has_vlan_assigned(
                    vlan_range, current_config
                ):
                    success = False
            except CommandExecutionException:
                current_config = self._add_sub_interface_vlan(
                    vlan_actions,
                    iface_action,
                    vlan_range,
                    port_name,
                    port_mode,
                    qnq,
                    c_tag,
                )

                if not "{}.{}".format(port_name, vlan_range) in current_config:
                    success = False
            if not success:
                raise Exception(
                    self.__class__.__name__,
                    "[FAIL] VLAN(s) {} configuration failed".format(vlan_range),
                )

        self._logger.info(
            "VLAN(s) {} configuration completed successfully".format(vlan_range)
        )
        return "[ OK ] VLAN(s) {} configuration completed successfully".format(
            vlan_range
        )

    def _add_switchport_vlan(
        self, vlan_actions, iface_actions, vlan_range, port_name, port_mode, qnq, c_tag
    ):
        vlan_actions.create_vlan(vlan_range)
        vlan_actions.set_vlan_to_interface(vlan_range, port_mode, port_name, qnq, c_tag)
        current_config = iface_actions.get_current_interface_config(port_name)
        return current_config

    def _add_sub_interface_vlan(
        self, vlan_actions, iface_actions, vlan_range, port_name, port_mode, qnq, c_tag
    ):
        if port_name and "-" not in vlan_range:
            sub_port_name = "{}.{}".format(port_name, vlan_range)
        else:
            raise Exception(self.__class__.__name__, self.CISCO_SUB_INTERFACE_ERROR)

        iface_actions.enter_iface_config_mode(sub_port_name)
        vlan_actions.set_vlan_to_sub_interface(
            vlan_range, port_mode, sub_port_name, qnq, c_tag
        )
        current_config = iface_actions.get_current_interface_config(sub_port_name)
        return current_config

    def _remove_all_vlan_flow(self, full_name, vm_uid=None):
        """Remove configuration of VLANs on multiple ports or port-channels.

        :param port_name: full port name
            Possible Values are trunk and access
        :return:
        """
        self._logger.info(
            "Interface {} configuration cleanup started".format(full_name)
        )
        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            iface_action = self._get_iface_actions(config_session)
            vlan_actions = self._get_vlan_actions(config_session)
            port_name = iface_action.get_port_name(full_name)

            current_config = iface_action.get_current_interface_config(port_name)
            if "switchport" not in current_config:
                self._remove_vlan_from_sub_interface(port_name, iface_action)
                sub_interfaces_list = iface_action.get_sub_interfaces_config(port_name)
                for interface in sub_interfaces_list:
                    if iface_action.check_sub_interface_has_vlan(interface):
                        self._logger.error(
                            "[FAIL] Unable to clean sub interface: {}".format(interface)
                        )
            else:
                iface_action.enter_iface_config_mode(port_name)
                iface_action.clean_interface_switchport_config(current_config)
                current_config = iface_action.get_current_interface_config(port_name)
                if vlan_actions.verify_interface_configured(current_config):
                    self._logger.error(
                        "[FAIL] VLAN(s) cleanup failed for {}".format(port_name)
                    )

        self._logger.info(
            "[ OK ] All VLAN(s) were removed successfully from {}".format(port_name)
        )

    def _remove_vlan_flow(self, vlan_range, full_name, port_mode, vm_uid=None):
        """Remove configuration of VLANs on multiple ports or port-channels.

        :param vlan_range: VLAN or VLAN range
        :param full_name: full port name
        :param port_mode: mode which will be configured on port.
            Possible Values are trunk and access
        :return:
        """
        self._logger.info("Remove Vlan {} configuration started".format(vlan_range))
        is_failed = False
        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            iface_action = self._get_iface_actions(config_session)
            vlan_actions = self._get_vlan_actions(config_session)
            port_name = iface_action.get_port_name(full_name)

            current_config = iface_action.get_current_interface_config(port_name)
            if "switchport" not in current_config:
                sub_interface_name = "{}.{}".format(port_name, vlan_range)
                self._remove_sub_interface(sub_interface_name, iface_action)
                sub_interfaces_list = iface_action.get_current_interface_config(
                    sub_interface_name
                )
                if sub_interface_name in sub_interfaces_list:
                    is_failed = True
                    self._logger.error(
                        "Failed to remove sub interface: {}".format(sub_interface_name)
                    )
            else:
                iface_action.enter_iface_config_mode(port_name)
                iface_action.clean_interface_switchport_config(current_config)
                current_config = iface_action.get_current_interface_config(port_name)
                if vlan_actions.verify_interface_has_vlan_assigned(
                    vlan_range, current_config
                ):
                    is_failed = True

            if is_failed:
                raise Exception(
                    self.__class__.__name__,
                    "[FAIL] VLAN(s) {} removal failed".format(vlan_range),
                )

        self._logger.info(
            "VLAN(s) {} removal completed successfully".format(vlan_range)
        )
        return "[ OK ] VLAN(s) {} removal completed successfully".format(vlan_range)

    def _remove_vlan_from_sub_interface(self, port_name, iface_actions):
        sub_interfaces_list = iface_actions.get_sub_interfaces_config(port_name)
        for sub_int in sub_interfaces_list:
            iface_actions.clean_vlan_sub_iface_config(sub_int)

    def _remove_sub_interface(self, port_name, iface_actions):
        iface_actions.clean_vlan_sub_iface_config(port_name)

    def _remove_vlan_from_interface(self, port_name, iface_actions):
        current_config = iface_actions.get_current_interface_config(port_name)
        iface_actions.enter_iface_config_mode(port_name)
        iface_actions.clean_interface_switchport_config(current_config)
