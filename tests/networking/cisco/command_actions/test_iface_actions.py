from unittest import TestCase
from mock import MagicMock, patch, create_autospec

from cloudshell.cli.cli_service_impl import CliServiceImpl
from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions


class TestAddRemoveVlanActions(TestCase):
    def setUp(self):
        self._cli_service = create_autospec(CliServiceImpl)
        self._handler = IFaceActions(self._cli_service, MagicMock())

    def test_verify_interface_configured(self):
        port_name = "10.10.10.10/Chassis 0/Ethernet1-24"
        port_name_2 = "1.1.1.1/Chassis 0/Module 0/Sub-Module 0/GigabiteEthernet 0-0-0-0-1"
        port_name_3 = "10.10.10.10/port-channel 248"
        port_name_4 = "10.10.10.10/Port-cHannel 248"

        self.assertEqual(port_name.split("/")[-1].replace("-", "/"), self._handler.get_port_name(port_name))
        self.assertEqual(port_name_2.split("/")[-1].replace("-", "/"), self._handler.get_port_name(port_name_2))
        self.assertEqual(port_name_3.split("/")[-1], self._handler.get_port_name(port_name_3))
        self.assertEqual(port_name_4.split("/")[-1], self._handler.get_port_name(port_name_4))
        try:
            self._handler.get_port_name(None)
        except Exception as e:
            self.assertEqual(e.args[-1], "Failed to get port name.")

    @patch("cloudshell.networking.cisco.command_actions.iface_actions.CommandTemplateExecutor")
    @patch("cloudshell.networking.cisco.command_actions.iface_actions.CommandTemplateExecutor")
    @patch("cloudshell.networking.cisco.command_actions.iface_actions.vlan_command_template")
    def test_get_no_l2_protocol_tunnel_cmd(self, vlan_templates_mock, cte_mock):
        result = self._handler._get_no_l2_protocol_tunnel_cmd()
        cte_mock.assert_called_once_with(self._cli_service, vlan_templates_mock.NO_L2_TUNNEL, action_map=None, error_map=None)
        self.assertEqual(result, cte_mock.return_value)

    @patch("cloudshell.networking.cisco.command_actions.iface_actions.CommandTemplateExecutor")
    @patch("cloudshell.networking.cisco.command_actions.iface_actions.vlan_command_template")
    def test_get_no_l2_protocol_tunnel_cmd(self, vlan_templates_mock, cte_mock):
        result = self._handler._get_no_l2_protocol_tunnel_cmd()
        cte_mock.return_valueassert_called_once_with(self._cli_service, vlan_templates_mock.NO_L2_TUNNEL, action_map=None, error_map=None)
        self.assertEqual(result, cte_mock.return_value)

    # @patch("cloudshell.networking.cisco.command_actions.iface_actions.CommandTemplateExecutor")
    # def test_config_vlan_on_interface_qnq(self, cte_mock):
    #     vlan_range = 11
    #     port_name = "Ehternet2/25"
    #     port_mode = "access"
    #
    #     conf_interface_mock = MagicMock()
    #     no_shut_mock = MagicMock()
    #     enable_switchport_mock = MagicMock()
    #     switchport_mode_mock = MagicMock()
    #     switchport_allow_vlan_mock = MagicMock()
    #
    #     cte_mock.side_effect = [conf_interface_mock, no_shut_mock, enable_switchport_mock, switchport_mode_mock,
    #                             MagicMock(),
    #                             switchport_allow_vlan_mock]
    #
    #     self._handler.set_vlan_to_interface(vlan_range=vlan_range, port_name=port_name, port_mode=port_mode, qnq=True,
    #                                         c_tag=None)
    #
    #     conf_interface_mock.execute_command.assert_called_once_with(port_name=port_name)
    #     no_shut_mock.execute_command.assert_called_once()
    #     enable_switchport_mock.execute_command.assert_called_once_with()
    #     switchport_mode_mock.execute_command.assert_called_once_with(port_mode="dot1q-tunnel")
    #     switchport_allow_vlan_mock.execute_command.assert_called_once_with(port_mode_access="", vlan_range=vlan_range)

    # @patch("cloudshell.networking.cisco.command_actions.iface_actions.CommandTemplateExecutor")
    # def test_config_vlan_on_interface_no_qnq_access(self, cte_mock):
    #     vlan_range = 11
    #     port_name = "Ehternet2/25"
    #     port_mode = "access"
    #
    #     conf_interface_mock = MagicMock()
    #     no_shut_mock = MagicMock()
    #     enable_switchport_mock = MagicMock()
    #     switchport_mode_mock = MagicMock()
    #     switchport_allow_vlan_mock = MagicMock()
    #
    #     cte_mock.side_effect = [conf_interface_mock, no_shut_mock, enable_switchport_mock, switchport_mode_mock,
    #                             switchport_allow_vlan_mock]
    #
    #     self._handler.set_vlan_to_interface(vlan_range=vlan_range, port_name=port_name, port_mode=port_mode, qnq=False,
    #                                         c_tag=None)
    #
    #     conf_interface_mock.execute_command.assert_called_once_with(port_name=port_name)
    #     no_shut_mock.execute_command.assert_called_once()
    #     enable_switchport_mock.execute_command.assert_called_once_with()
    #     switchport_mode_mock.execute_command.assert_called_once_with(port_mode=port_mode)
    #     switchport_allow_vlan_mock.execute_command.assert_called_once_with(port_mode_access="", vlan_range=vlan_range)

    # @patch("cloudshell.networking.cisco.command_actions.iface_actions.CommandTemplateExecutor")
    # def test_config_vlan_on_interface_no_qnq_trunk(self, cte_mock):
    #     vlan_range = 11
    #     port_name = "Ehternet2/25"
    #     port_mode = "trunk"
    #
    #     conf_interface_mock = MagicMock()
    #     no_shut_mock = MagicMock()
    #     enable_switchport_mock = MagicMock()
    #     switchport_mode_mock = MagicMock()
    #     switchport_allow_vlan_mock = MagicMock()
    #
    #     cte_mock.side_effect = [conf_interface_mock, no_shut_mock, enable_switchport_mock, switchport_mode_mock,
    #                             switchport_allow_vlan_mock]
    #
    #     self._handler.set_vlan_to_interface(vlan_range=vlan_range, port_name=port_name, port_mode=port_mode, qnq=False,
    #                                         c_tag=None)
    #
    #     conf_interface_mock.execute_command.assert_called_once_with(port_name=port_name)
    #     no_shut_mock.execute_command.assert_called_once()
    #     enable_switchport_mock.execute_command.assert_called_once_with()
    #     switchport_mode_mock.execute_command.assert_called_once_with(port_mode=port_mode)
    #     switchport_allow_vlan_mock.execute_command.assert_called_once_with(port_mode_trunk="", vlan_range=vlan_range)
