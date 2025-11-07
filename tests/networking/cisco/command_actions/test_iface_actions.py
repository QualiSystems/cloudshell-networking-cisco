from unittest import TestCase

from cloudshell.cli.service.cli_service_impl import CliServiceImpl

from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions

try:
    from unittest.mock import MagicMock, create_autospec, patch
except ImportError:
    from unittest.mock import MagicMock, create_autospec, patch


class TestAddRemoveVlanActions(TestCase):
    def setUp(self):
        self._cli_service = create_autospec(CliServiceImpl)
        self._handler = IFaceActions(self._cli_service, MagicMock())

    def test_verify_interface_configured(self):
        port_name = "10.10.10.10/Chassis 0/Ethernet1-24"
        port_name_2 = (
            "1.1.1.1/Chassis 0/Module 0/Sub-Module 0/GigabiteEthernet 0-0-0-0-1"
        )
        port_name_3 = "10.10.10.10/port-channel 248"
        port_name_4 = "10.10.10.10/Port-cHannel 248"

        self.assertEqual(
            port_name.split("/")[-1].replace("-", "/"),
            self._handler.get_port_name(port_name),
        )
        self.assertEqual(
            port_name_2.split("/")[-1].replace("-", "/"),
            self._handler.get_port_name(port_name_2),
        )
        self.assertEqual(
            port_name_3.split("/")[-1], self._handler.get_port_name(port_name_3)
        )
        self.assertEqual(
            port_name_4.split("/")[-1], self._handler.get_port_name(port_name_4)
        )
        try:
            self._handler.get_port_name(None)
        except Exception as e:
            self.assertEqual(e.args[-1], "Failed to get port name.")

    @patch(
        "cloudshell.networking.cisco.command_actions.iface_actions"
        ".CommandTemplateExecutor"
    )
    @patch(
        "cloudshell.networking.cisco.command_actions.iface_actions" ".add_remove_vlan"
    )
    def test_get_no_l2_protocol_tunnel_cmd(self, vlan_templates_mock, cte_mock):
        result = self._handler._get_no_l2_protocol_tunnel_cmd()
        cte_mock.assert_called_once_with(
            self._cli_service,
            vlan_templates_mock.NO_L2_TUNNEL,
            action_map=None,
            error_map=None,
        )
        self.assertEqual(result, cte_mock.return_value)

    @patch(
        "cloudshell.networking.cisco.command_actions.iface_actions"
        ".CommandTemplateExecutor"
    )
    def test_clean_interface_switchport_config_preserves_vlan_1(self, cte_mock):
        """Test that switchport trunk allowed vlan 1 is not removed (default state)."""
        current_config = """Building configuration...

Current configuration : 144 bytes
!
interface GigabitEthernet110/1/0/6
 description KG-255X-06-PT
 switchport
 switchport trunk allowed vlan 1
 switchport mode dynamic auto
end
"""
        executor_mock = MagicMock()
        cte_mock.return_value = executor_mock

        self._handler.clean_interface_switchport_config(current_config)

        # Verify that execute_command was called for other switchport lines but not for vlan 1
        calls = executor_mock.execute_command.call_args_list
        # Should be called once for "switchport mode dynamic auto"
        # but NOT for "switchport trunk allowed vlan 1"
        # Note: "switchport" alone (without trailing space) is not matched by the pattern
        self.assertEqual(len(calls), 1)

        # Verify the command that was issued
        called_commands = [call[1]["command"] for call in calls]
        self.assertIn("switchport mode dynamic auto", called_commands)
        # Ensure vlan 1 line was NOT processed (would appear as "switchport trunk allowed vlan" after regex)
        for cmd in called_commands:
            self.assertNotIn("trunk allowed vlan", cmd)

    @patch(
        "cloudshell.networking.cisco.command_actions.iface_actions"
        ".CommandTemplateExecutor"
    )
    def test_clean_interface_switchport_config_removes_other_vlans(self, cte_mock):
        """Test that switchport trunk allowed vlan with other VLANs are removed."""
        current_config = """Building configuration...

Current configuration : 144 bytes
!
interface GigabitEthernet110/1/0/6
 description KG-255X-06-PT
 switchport
 switchport trunk allowed vlan 100
 switchport mode trunk
end
"""
        executor_mock = MagicMock()
        cte_mock.return_value = executor_mock

        self._handler.clean_interface_switchport_config(current_config)

        # Verify that execute_command was called for all switchport lines including vlan 100
        calls = executor_mock.execute_command.call_args_list
        # Should be called twice: "switchport trunk allowed vlan", "switchport mode trunk"
        # Note: "switchport" alone (without trailing space) is not matched by the pattern
        self.assertEqual(len(calls), 2)

        # Verify the commands that were issued
        called_commands = [call[1]["command"] for call in calls]
        self.assertIn("switchport trunk allowed vlan", called_commands)
        self.assertIn("switchport mode trunk", called_commands)

    @patch(
        "cloudshell.networking.cisco.command_actions.iface_actions"
        ".CommandTemplateExecutor"
    )
    def test_clean_interface_switchport_config_removes_vlan_1_in_range(self, cte_mock):
        """Test that VLAN 1 in a range or list is still removed (not default state)."""
        current_config = """Building configuration...

Current configuration : 144 bytes
!
interface GigabitEthernet110/1/0/6
 description Test Port
 switchport trunk allowed vlan 1,2,3
 switchport mode trunk
end
"""
        executor_mock = MagicMock()
        cte_mock.return_value = executor_mock

        self._handler.clean_interface_switchport_config(current_config)

        # Verify that execute_command was called for VLAN range including vlan 1
        calls = executor_mock.execute_command.call_args_list
        # Should be called twice: "switchport trunk allowed vlan", "switchport mode trunk"
        self.assertEqual(len(calls), 2)

        # Verify the commands that were issued - vlan 1,2,3 should be removed
        called_commands = [call[1]["command"] for call in calls]
        self.assertIn("switchport trunk allowed vlan", called_commands)
        self.assertIn("switchport mode trunk", called_commands)
