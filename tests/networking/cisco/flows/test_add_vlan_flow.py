from unittest import TestCase

from cloudshell.networking.cisco.flows.cisco_connectivity_flow import (
    CiscoConnectivityFlow,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoAddVlanFlow(TestCase):
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
        qnq = False
        c_tag = ""
        iface_mock.return_value.get_port_name.return_value = converted_port_name

        self._handler._add_vlan_flow(vlan_id, port_mode, port_name, qnq, c_tag)
        iface_mock.return_value.get_port_name.assert_called_once_with(port_name)
        vlan_actions_mock.return_value.create_vlan.assert_called_once_with(vlan_id)
        iface_mock.return_value.get_current_interface_config.assert_called_with(
            converted_port_name
        )
        self.assertTrue(
            iface_mock.return_value.get_current_interface_config.call_count == 2
        )
        iface_mock.return_value.enter_iface_config_mode.assert_called_once_with(
            converted_port_name
        )
        iface_mock.return_value.clean_interface_switchport_config.assert_called_once()
        vlan_actions_mock.return_value.verify_interface_configured.assert_called_once()
        vlan_actions_mock.return_value.set_vlan_to_interface.assert_called_once_with(
            vlan_id, port_mode, converted_port_name, qnq, c_tag
        )
