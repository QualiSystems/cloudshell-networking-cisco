#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.devices.flows.action_flows import LoadFirmwareFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.networking.cisco.command_actions.system_actions import SystemActions, FirmwareActions


class CiscoLoadFirmwareFlow(LoadFirmwareFlow):
    RUNNING_CONFIG = "running-config"
    STARTUP_CONFIG = "startup-config"
    BOOTFLASH = "bootflash:"
    FLASH = "flash:"

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
            dst_file_system = self.FLASH
            firmware_dst_path = "{0}/{1}".format(dst_file_system, firmware_file_name)
            device_file_system = system_action.get_flash_folders_list()
            self._logger.info("Discovered folders: {}".format(device_file_system))
            if device_file_system:
                if self.BOOTFLASH in device_file_system:
                    self._logger.info("Device has a bootflash folder")
                    firmware_dst_path = "{0}/{1}".format(self.BOOTFLASH, firmware_file_name)
                    self._logger.info("Copying {} image".format(firmware_dst_path))
                    system_action.copy(path, firmware_dst_path, vrf=vrf, action_map=system_action.prepare_action_map(path, firmware_dst_path))
                else:
                    for flash in device_file_system:
                        if "flash-" in  flash:
                            firmware_dst_file_path = "{0}/{1}".format(flash, firmware_file_name)
                            self._logger.info("Copying {} image".format(firmware_dst_file_path))
                            system_action.copy(path, firmware_dst_file_path, vrf=vrf, action_map=system_action.prepare_action_map(path, firmware_dst_file_path))
            else:
                self._logger.info("Copying {} image".format(firmware_dst_path))
                system_action.copy(path, firmware_dst_path, vrf=vrf, action_map=system_action.prepare_action_map(path, firmware_dst_path))

            self._logger.info("Get current boot configuration")
            current_boot = system_action.get_current_boot_image()
            with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                firmware_action = FirmwareActions(config_session, self._logger)
                for boot_conf in current_boot:
                    self._logger.info("Removing '{}' boot config line".format(boot_conf))
                    firmware_action.clean_boot_config(boot_conf)
                self._logger.info("Adding '{}' boot config line".format(firmware_dst_path))
                firmware_action.add_boot_config_file(firmware_dst_path)
                for append_boot in current_boot:
                    if firmware_dst_path not in append_boot:
                        self._logger.info("Adding '{}' boot config line".format(append_boot))
                        firmware_action.add_boot_config(append_boot)

            output = system_action.get_current_boot_config()
            new_boot_settings = re.sub("^.*boot-start-marker|boot-end-marker.*", "", output)
            self._logger.info("Updated boot config lines are: {0}".format(new_boot_settings))

            if output.find(firmware_file_name) == -1:
                raise Exception(self.__class__.__name__,
                                "Can't add firmware '{}' for boot!".format(firmware_file_name))

            system_action.copy(self.RUNNING_CONFIG, self.STARTUP_CONFIG, vrf=vrf, action_map=system_action.prepare_action_map(self.RUNNING_CONFIG, self.STARTUP_CONFIG))
            if "CONSOLE" in enable_session.SESSION_TYPE:
                system_action.reload_device_via_console(timeout)
            else:
                system_action.reload_device(timeout)

            os_version = system_action.get_current_os_version()
            if os_version.find(firmware_file_name) == -1:
                raise Exception(self.__class__.__name__, "Failed to load firmware, Please check logs")
