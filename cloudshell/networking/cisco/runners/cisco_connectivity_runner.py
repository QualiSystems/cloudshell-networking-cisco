#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.connectivity_runner import ConnectivityRunner
from cloudshell.networking.cisco.flows.cisco_add_vlan_flow import CiscoAddVlanFlow
from cloudshell.networking.cisco.flows.cisco_remove_vlan_flow import CiscoRemoveVlanFlow


class CiscoConnectivityRunner(ConnectivityRunner):
    @property
    def add_vlan_flow(self):
        return CiscoAddVlanFlow(self.cli_handler, self._logger)

    @property
    def remove_vlan_flow(self):
        return CiscoRemoveVlanFlow(self.cli_handler, self._logger)
