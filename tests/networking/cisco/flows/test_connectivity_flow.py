from unittest import TestCase
from unittest.mock import MagicMock, Mock, create_autospec, patch

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
    ConnectivityTypeEnum,
)

from cloudshell.networking.cisco.flows.cisco_connectivity_flow import (
    CiscoConnectivityFlow,
)


class TestCiscoAddVlanFlow(TestCase):
    def setUp(self):
        self._handler = CiscoConnectivityFlow(MagicMock(), MagicMock())

    def create_vlan_model(
        self,
        action_id="id",
        request_type=ConnectivityTypeEnum.SET_VLAN,
        vlan_id="45",
        port_mode="trunk",
        port_name="Ethernet4-5",
        qnq=False,
        c_tag="",
    ) -> ConnectivityActionModel:
        action = create_autospec(ConnectivityActionModel)
        action.action_id = action_id
        action.type = request_type
        action.connection_params = Mock(
            vlan_id=vlan_id,
            mode=Mock(value=port_mode),
            vlan_service_attrs=Mock(qnq=qnq, ctag=c_tag),
        )
        action.action_target = Mock()
        action.action_target.name = port_name
        return action

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
        action = self.create_vlan_model()
        converted_port_name = action.action_target.name.replace("-", "/")
        iface_mock.return_value.get_port_name.return_value = converted_port_name

        add_vlan_mock.side_effect = [CommandExecutionException("failed")]
        add_sub_iface_mock.return_value = "interface {}.{}".format(
            converted_port_name, action.connection_params.vlan_id
        )

        self._handler._set_vlan(action)

        iface_mock.return_value.get_port_name.assert_called_once_with(
            action.action_target.name
        )

        add_sub_iface_mock.assert_called_once_with(
            vlan_actions_mock.return_value,
            iface_mock.return_value,
            action.connection_params.vlan_id,
            converted_port_name,
            action.connection_params.mode.value,
            action.connection_params.vlan_service_attrs.qnq,
            action.connection_params.vlan_service_attrs.ctag,
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
        action = self.create_vlan_model()
        response = "[ OK ] VLAN(s) {} configuration completed successfully".format(
            action.connection_params.vlan_id
        )
        converted_port_name = action.action_target.name.replace("-", "/")
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        add_vlan_mock.return_value = response

        self._handler._set_vlan(action)
        iface_mock.return_value.get_port_name.assert_called_once_with(
            action.action_target.name
        )
        add_vlan_mock.assert_called_once_with(
            vlan_actions_mock.return_value,
            iface_mock.return_value,
            action.connection_params.vlan_id,
            converted_port_name,
            action.connection_params.mode.value,
            action.connection_params.vlan_service_attrs.qnq,
            action.connection_params.vlan_service_attrs.ctag,
        )
        vlan_mock = vlan_actions_mock.return_value
        vlan_mock.verify_interface_has_vlan_assigned.assert_called_once_with(
            action.connection_params.vlan_id, response
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
        output = "ip address 10.0.0.0/24"
        action = self.create_vlan_model(request_type=ConnectivityTypeEnum.REMOVE_VLAN)
        converted_port_name = action.action_target.name.replace("-", "/")
        converted_sub_port_name = (
            f"{converted_port_name}." f"{action.connection_params.vlan_id}"
        )
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_port_name.return_value = converted_port_name
        iface_obj_mock.check_sub_interface_has_vlan.return_value = False
        iface_obj_mock.get_current_interface_config.return_value = output
        iface_obj_mock.get_sub_interfaces_config.return_value = [
            converted_sub_port_name
        ]

        self._handler._remove_vlan(action)

        iface_obj_mock = iface_mock.return_value

        iface_obj_mock.get_port_name.assert_called_once_with(action.action_target.name)
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
        action = self.create_vlan_model(request_type=ConnectivityTypeEnum.REMOVE_VLAN)
        port_name = action.action_target.name
        converted_port_name = action.action_target.name.replace("-", "/")
        vlan_id = action.connection_params.vlan_id
        output = "switchport"
        result = "switchport allow vlan 45"
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        vlan_mock = vlan_actions_mock.return_value
        vlan_mock.verify_interface_has_vlan_assigned.return_value = False
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_current_interface_config.side_effect = [output, result]

        self._handler._remove_vlan(action)

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
        action = self.create_vlan_model(
            vlan_id="", request_type=ConnectivityTypeEnum.REMOVE_VLAN
        )
        port_name = action.action_target.name
        converted_port_name = action.action_target.name.replace("-", "/")
        output = "ip address 10.0.0.0/24"

        iface_mock.return_value.get_port_name.return_value = converted_port_name
        vlan_actions_mock.return_value.verify_interface_configured.return_value = False
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_current_interface_config.return_value = output
        iface_obj_mock.get_sub_interfaces_config.return_value = [
            converted_port_name + ".45"
        ]

        self._handler._remove_vlan(action)

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
        action = self.create_vlan_model(
            vlan_id="", request_type=ConnectivityTypeEnum.REMOVE_VLAN
        )
        port_name = action.action_target.name
        converted_port_name = action.action_target.name.replace("-", "/")
        output = "switchport"
        iface_mock.return_value.get_port_name.return_value = converted_port_name
        vlan_actions_mock.return_value.verify_interface_has_no_vlan_assigned.return_value = (
            True
        )
        iface_obj_mock = iface_mock.return_value
        iface_obj_mock.get_current_interface_config.return_value = output

        self._handler._remove_vlan(action)

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
