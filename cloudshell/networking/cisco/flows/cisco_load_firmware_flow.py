#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.devices.flows.action_flows import LoadFirmwareFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions
from cloudshell.networking.cisco.command_actions.system_actions import SystemActions, FirmwareActions


class CiscoLoadFirmwareFlow(LoadFirmwareFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoLoadFirmwareFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param path: The path to the firmware file, including the firmware file name
        :param vrf: Virtual Routing and Forwarding Name
        :param timeout:
        :return:
        """

        full_path_dict = UrlParser().parse_url(path)
        firmware_file_name = full_path_dict.get(UrlParser.FILENAME)
        if not firmware_file_name:
            raise Exception(self.__class__.__name__, "Unable to find firmware file")

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            system_action = SystemActions(enable_session, self._logger)
            iface_action = IFaceActions(enable_session, self._logger)
            system_action.copy(path, "flash:/", vrf=vrf)

            current_boot_settings = system_action.get_current_boot_config()
            current_boot_settings = re.sub("boot-start-marker|boot-end-marker", "", current_boot_settings)
            iface_action.clean_interface_switchport_config(current_boot_settings)
            with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                firmware_action = FirmwareActions(config_session, self._logger)
                firmware_action.install_firmware(firmware_file_name)

            output = system_action.get_current_boot_config()

            if output.find(firmware_file_name) == -1:
                raise Exception(self.__class__.__name__,
                                "Can't add firmware '{}' for boot!".format(firmware_file_name))

            system_action.copy("running-config", "startup-config", vrf=vrf)
            system_action.reload_device(timeout)

            os_version = system_action.get_current_os_version()
            if os_version.find(firmware_file_name) == -1:
                raise Exception(self.__class__.__name__, "Failed to load firmware, Please check logs")
