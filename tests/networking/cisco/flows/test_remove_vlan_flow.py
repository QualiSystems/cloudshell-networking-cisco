from unittest import TestCase

from cloudshell.networking.cisco.flows.cisco_connectivity_flow import (
    CiscoConnectivityFlow,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoRemoveVlanFlow(TestCase):
    def setUp(self):
        self._handler = CiscoConnectivityFlow(MagicMock(), MagicMock())

    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow.AddRemoveVlanActions"
    )
    @patch("cloudshell.networking.cisco.flows.cisco_connectivity_flow.IFaceActions")
    def test_execute_flow(self, iface_mock, vlan_actions_mock):
        port_mode = "trunk"
        port_name = "Ethernet4-5"
        converted_port_name = "Ethernet4/5"
        vlan_id = "45"
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        vlan_actions_mock.return_value.verify_interface_configured.return_value = False

        self._handler._remove_vlan_flow(vlan_id, port_name, port_mode)

        iface_obj_mock = iface_mock.return_value

        iface_obj_mock.get_port_name.assert_called_once_with(port_name)
        iface_obj_mock.get_current_interface_config.assert_called_with(
            converted_port_name
        )
        if_curconf_mock = iface_obj_mock.get_current_interface_config
        self.assertTrue(if_curconf_mock.call_count == 2)
        iface_obj_mock.enter_iface_config_mode.assert_called_once_with(
            converted_port_name
        )
        iface_obj_mock.clean_interface_switchport_config.assert_called_once()
        vlan_actions_mock.return_value.verify_interface_configured.assert_called_once_with(  # noqa: E501
            vlan_id, if_curconf_mock.return_value
        )
