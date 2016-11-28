#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from cloudshell.networking.cisco.cisco_command_actions import copy, get_current_boot_config, \
    remove_port_configuration_commands, reload_device, get_current_os_version, install_firmware

from cloudshell.networking.devices.flows.action_flows import LoadFirmwareFlow
from cloudshell.networking.devices.networking_utils import UrlParser


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
            copy(enable_session, self._logger, path, "flash:/", vrf)
            current_boot_settings = get_current_boot_config(session=enable_session)
            current_boot_settings = re.sub("boot-start-marker|boot-end-marker", "", current_boot_settings)
            remove_port_configuration_commands(enable_session, current_boot_settings)
            with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                install_firmware(config_session, self._logger, firmware_file_name)
            output = get_current_boot_config(session=enable_session)
            is_boot_firmware = output.find(firmware_file_name) != -1
            if not is_boot_firmware:
                raise Exception(self.__class__.__name__,
                                "Can't add firmware '{}' for boot!".format(firmware_file_name))
            copy(enable_session, self._logger, "running-config", "startup-config", vrf=vrf)
            reload_device(enable_session, self._logger, timeout)
            os_version = get_current_os_version(enable_session)
            if os_version.find(firmware_file_name) == -1:
                raise Exception(self.__class__.__name__, "Failed to load firmware, Please check logs")
