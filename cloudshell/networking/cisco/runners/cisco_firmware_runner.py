#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.firmware_runner import FirmwareRunner
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flows.cisco_load_firmware_flow import CiscoLoadFirmwareFlow


class CiscoFirmwareRunner(FirmwareRunner):
    @property
    def load_firmware_flow(self):
        return CiscoLoadFirmwareFlow(self.cli_handler, self._logger)
