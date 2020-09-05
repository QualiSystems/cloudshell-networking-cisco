from unittest import TestCase

from cloudshell.cli.session.session_exceptions import CommandExecutionException

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
    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow."
        "CiscoConnectivityFlow._add_sub_interface_vlan"
    )
    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow."
        "CiscoConnectivityFlow._add_switchport_vlan"
    )
    def test_add_vlan_router_flow(
        self, add_vlan_mock, add_sub_iface_mock, iface_mock, vlan_actions_mock
    ):
        port_mode = "trunk"
        port_name = "Ethernet4-5"
        converted_port_name = "Ethernet4/5"
        vlan_id = "45"
        qnq = False
        c_tag = ""
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        add_vlan_mock.side_effect = [CommandExecutionException("failed")]
        add_sub_iface_mock.return_value = "interface {}.{}".format(
            converted_port_name, vlan_id
        )

        self._handler._add_vlan_flow(vlan_id, port_mode, port_name, qnq, c_tag)

        iface_mock.return_value.get_port_name.assert_called_once_with(port_name)

        add_sub_iface_mock.assert_called_once_with(
            vlan_actions_mock.return_value,
            iface_mock.return_value,
            vlan_id,
            converted_port_name,
            port_mode,
            qnq,
            c_tag,
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow.AddRemoveVlanActions"
    )
    @patch("cloudshell.networking.cisco.flows.cisco_connectivity_flow.IFaceActions")
    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow."
        "CiscoConnectivityFlow._add_switchport_vlan"
    )
    def test_add_vlan_switch_flow(self, add_vlan_mock, iface_mock, vlan_actions_mock):
        port_mode = "trunk"
        port_name = "Ethernet4-5"
        response = MagicMock()
        converted_port_name = "Ethernet4/5"
        vlan_id = "45"
        qnq = False
        c_tag = ""
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        add_vlan_mock.return_value = response

        self._handler._add_vlan_flow(vlan_id, port_mode, port_name, qnq, c_tag)
        iface_mock.return_value.get_port_name.assert_called_once_with(port_name)
        add_vlan_mock.assert_called_once_with(
            vlan_actions_mock.return_value,
            iface_mock.return_value,
            vlan_id,
            converted_port_name,
            port_mode,
            qnq,
            c_tag,
        )
        vlan_mock = vlan_actions_mock.return_value
        vlan_mock.verify_interface_has_vlan_assigned.assert_called_once_with(
            vlan_id, response
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow.AddRemoveVlanActions"
    )
    @patch("cloudshell.networking.cisco.flows.cisco_connectivity_flow.IFaceActions")
    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow."
        "CiscoConnectivityFlow._remove_sub_interface"
    )
    def test_remove_flow_router(self, rm_sub_iface_mock, iface_mock, vlan_actions_mock):
        port_mode = "trunk"
        port_name = "Ethernet4-5"
        converted_port_name = "Ethernet4/5"
        converted_sub_port_name = "Ethernet4/5.45"
        vlan_id = "45"
        output = "ip address 10.0.0.0/24"
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_port_name.return_value = converted_port_name
        iface_obj_mock.check_sub_interface_has_vlan.return_value = False
        iface_obj_mock.get_current_interface_config.return_value = output
        iface_obj_mock.get_sub_interfaces_config.return_value = [
            converted_sub_port_name
        ]

        self._handler._remove_vlan_flow(vlan_id, port_name, port_mode)

        iface_obj_mock = iface_mock.return_value

        iface_obj_mock.get_port_name.assert_called_once_with(port_name)
        iface_obj_mock.get_current_interface_config.assert_called_with(
            converted_sub_port_name
        )

        rm_sub_iface_mock.assert_called_once_with(
            converted_sub_port_name, iface_obj_mock
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow.AddRemoveVlanActions"
    )
    @patch("cloudshell.networking.cisco.flows.cisco_connectivity_flow.IFaceActions")
    def test_remove_flow_switch(self, iface_mock, vlan_actions_mock):
        port_mode = "trunk"
        port_name = "Ethernet4-5"
        converted_port_name = "Ethernet4/5"
        vlan_id = "45"
        output = "switchport"
        result = "switchport allow vlan 45"
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        vlan_mock = vlan_actions_mock.return_value
        vlan_mock.verify_interface_has_vlan_assigned.return_value = False
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_current_interface_config.side_effect = [output, result]

        self._handler._remove_vlan_flow(vlan_id, port_name, port_mode)

        iface_obj_mock.get_port_name.assert_called_once_with(port_name)
        iface_obj_mock.get_current_interface_config.assert_called_with(
            converted_port_name
        )
        iface_mock.return_value.enter_iface_config_mode.assert_called_once_with(
            converted_port_name
        )
        iface_obj_mock.clean_interface_switchport_config.assert_called_once()
        self.assertTrue(iface_obj_mock.get_current_interface_config.call_count == 2)

        iface_obj_mock.enter_iface_config_mode.assert_called_once_with(
            converted_port_name
        )
        iface_obj_mock.clean_interface_switchport_config.assert_called_once_with(output)
        vlan_mock = vlan_actions_mock.return_value
        vlan_mock.verify_interface_has_vlan_assigned.assert_called_once_with(
            vlan_id, result
        )

    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow.AddRemoveVlanActions"
    )
    @patch("cloudshell.networking.cisco.flows.cisco_connectivity_flow.IFaceActions")
    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow."
        "CiscoConnectivityFlow._remove_vlan_from_sub_interface"
    )
    def test_remove_all_flow_router(
        self, rm_sub_iface_mock, iface_mock, vlan_actions_mock
    ):
        port_name = "Ethernet4-5"
        converted_port_name = "Ethernet4/5"
        output = "ip address 10.0.0.0/24"

        iface_mock.return_value.get_port_name.return_value = converted_port_name
        vlan_actions_mock.return_value.verify_interface_configured.return_value = False
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_current_interface_config.return_value = output
        iface_obj_mock.get_sub_interfaces_config.return_value = [
            converted_port_name + ".45"
        ]

        self._handler._remove_all_vlan_flow(port_name)

        iface_obj_mock.get_port_name.assert_called_once_with(port_name)
        iface_obj_mock.get_current_interface_config.assert_called_once_with(
            converted_port_name
        )
        iface_obj_mock.get_sub_interfaces_config.assert_called_once()
        iface_obj_mock.check_sub_interface_has_vlan.assert_called_once()

        rm_sub_iface_mock.assert_called_once_with(converted_port_name, iface_obj_mock)

    @patch(
        "cloudshell.networking.cisco.flows.cisco_connectivity_flow.AddRemoveVlanActions"
    )
    @patch("cloudshell.networking.cisco.flows.cisco_connectivity_flow.IFaceActions")
    def test_remove_all_flow_switch(self, iface_mock, vlan_actions_mock):
        port_name = "Ethernet4-5"
        converted_port_name = "Ethernet4/5"
        output = "switchport"
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        vlan_actions_mock.return_value.verify_interface_configured.return_value = False
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_current_interface_config.return_value = output

        self._handler._remove_all_vlan_flow(port_name)

        iface_obj_mock.get_port_name.assert_called_once_with(port_name)
        iface_obj_mock.get_current_interface_config.assert_called_with(
            converted_port_name
        )
        iface_mock.return_value.enter_iface_config_mode.assert_called_once_with(
            converted_port_name
        )
        iface_obj_mock.clean_interface_switchport_config.assert_called_once()
        self.assertTrue(iface_obj_mock.get_current_interface_config.call_count == 2)

        iface_obj_mock.enter_iface_config_mode.assert_called_once_with(
            converted_port_name
        )
        iface_obj_mock.clean_interface_switchport_config.assert_called_once_with(output)
