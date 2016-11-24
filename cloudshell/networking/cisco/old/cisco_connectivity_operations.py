from collections import OrderedDict

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.flow.cisco_add_vlan_flow import CiscoAddVlanFlow
from cloudshell.networking.devices.networking_utils import *
from cloudshell.networking.devices.operations.connectivity_operations import ConnectivityOperations
from cloudshell.cli.command_template.command_template_service import add_templates, get_commands_list


class CiscoConnectivityOperations(ConnectivityOperations):
    def __init__(self, cli, logger, api, context, supported_os):
        """
        Handle add/remove vlan flows

        :param cli:
        :param logger:
        :param api:
        :param context:
        :param supported_os:
        """

        ConnectivityOperations.__init__(self, logger)
        self.cli = cli
        self._logger = logger
        self.api = api
        self.add_vlan_flow = CiscoAddVlanFlow()