from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.cisco.flow.cisco_add_vlan_flow import CiscoAddVlanFlow
from cloudshell.networking.cisco.flow.cisco_remove_vlan_flow import CiscoRemoveVlanFlow
from cloudshell.networking.devices.operations.connectivity_operations import ConnectivityOperations


class CiscoConnectivityOperations(ConnectivityOperations):
    def __init__(self, cli, logger, api, context):
        """
        Handle add/remove vlan flows

        :param cli:
        :param logger:
        :param api:
        :param context:
        :param supported_os:
        """

        super(CiscoConnectivityOperations, self).__init__(logger)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._save_flow = CiscoAddVlanFlow(cli_handler=self._cli_handler,
                                           logger=self._logger)
        self._restore_flow = CiscoRemoveVlanFlow(cli_handler=self._cli_handler,
                                                 logger=self._logger)
