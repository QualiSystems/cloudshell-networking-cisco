from unittest import TestCase

from cloudshell.cli.service.cli_service_impl import CliServiceImpl

from cloudshell.networking.cisco.command_actions.add_remove_vlan_actions import (
    AddRemoveVlanActions,
)
from cloudshell.networking.cisco.command_templates.add_remove_vlan import L2_TUNNEL

try:
    from unittest.mock import MagicMock, create_autospec, patch
except ImportError:
    from unittest.mock import MagicMock, create_autospec, patch


class TestAddRemoveVlanActions(TestCase):
    def setUp(self):
        self._cli_service = create_autospec(CliServiceImpl)
        self._handler = AddRemoveVlanActions(self._cli_service, MagicMock())

    def test_verify_interface_configured(self):
        vlan_id = "11"
        vlan_id_2 = "1"
        vlan_id_3 = "111"
        current_config = """Building configuration...

        Current configuration : 118 bytes
        !
        interface FastEthernet0/22
         switchport trunk allowed vlan 11
         switchport mode trunk
         channel-group 1 mode auto
        end
        Boogie#
        """
        self.assertTrue(
            self._handler.verify_interface_has_vlan_assigned(vlan_id, current_config)
        )
        self.assertFalse(
            self._handler.verify_interface_has_vlan_assigned(vlan_id_2, current_config)
        )
        self.assertFalse(
            self._handler.verify_interface_has_vlan_assigned(vlan_id_3, current_config)
        )

    def test_verify_interface_has_any_vlan(self):
        current_config = """Building configuration...

        Current configuration : 118 bytes
        !
        interface FastEthernet0/22
         switchport trunk allowed vlan 11
         switchport mode trunk
         channel-group 1 mode auto
        end
        Boogie#
        """
        self.assertTrue(self._handler.verify_interface_configured(current_config))
        current_config = """Building configuration...

        Current configuration : 118 bytes
        !
        interface FastEthernet0/22
         channel-group 1 mode auto
        end
        Boogie#
        """
        self.assertFalse(self._handler.verify_interface_configured(current_config))

    def test_verify_interface_has_no_vlan_assigned_with_default_vlan_1_trunk(self):
        """Test that VLAN 1 on trunk is considered as no VLANs assigned (default state)."""
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
        # VLAN 1 is the default state, should be considered as "no VLANs assigned"
        self.assertTrue(
            self._handler.verify_interface_has_no_vlan_assigned(current_config)
        )

    def test_verify_interface_has_no_vlan_assigned_with_default_vlan_1_access(self):
        """Test that VLAN 1 on access port is considered as no VLANs assigned (default state)."""
        current_config = """Building configuration...

        Current configuration : 100 bytes
        !
        interface GigabitEthernet1/0/4
         switchport
         switchport access vlan 1
        end
        """
        # VLAN 1 is the default state, should be considered as "no VLANs assigned"
        self.assertTrue(
            self._handler.verify_interface_has_no_vlan_assigned(current_config)
        )

    def test_verify_interface_has_no_vlan_assigned_without_explicit_vlan(self):
        """Test that interface without explicit VLAN config is considered as no VLANs assigned."""
        current_config = """Building configuration...

        Current configuration : 85 bytes
        !
        interface TenGigabitEthernet1/5/10
         description SPIRENT Port 2/10
         switchport
        end
        """
        # No explicit VLAN, should be considered as "no VLANs assigned"
        self.assertTrue(
            self._handler.verify_interface_has_no_vlan_assigned(current_config)
        )

    def test_verify_interface_has_no_vlan_assigned_with_non_default_vlan(self):
        """Test that non-default VLAN is detected as VLANs assigned."""
        current_config = """Building configuration...

        Current configuration : 100 bytes
        !
        interface GigabitEthernet1/0/1
         switchport
         switchport trunk allowed vlan 10
        end
        """
        # VLAN 10 is not the default, should be considered as "VLANs assigned"
        self.assertFalse(
            self._handler.verify_interface_has_no_vlan_assigned(current_config)
        )

    def test_verify_interface_has_no_vlan_assigned_with_multiple_vlans(self):
        """Test that multiple VLANs including VLAN 1 is detected as VLANs assigned."""
        current_config = """Building configuration...

        Current configuration : 110 bytes
        !
        interface GigabitEthernet1/0/2
         switchport
         switchport trunk allowed vlan 1,10,20
        end
        """
        # Multiple VLANs, should be considered as "VLANs assigned"
        self.assertFalse(
            self._handler.verify_interface_has_no_vlan_assigned(current_config)
        )

    def test_verify_interface_has_no_vlan_assigned_with_vlan_range(self):
        """Test that VLAN range is detected as VLANs assigned."""
        current_config = """Building configuration...

        Current configuration : 105 bytes
        !
        interface GigabitEthernet1/0/3
         switchport
         switchport trunk allowed vlan 10-20
        end
        """
        # VLAN range, should be considered as "VLANs assigned"
        self.assertFalse(
            self._handler.verify_interface_has_no_vlan_assigned(current_config)
        )

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_create_vlan(self, cte_mock):
        conf_vlan_mock = MagicMock()
        state_vlan_mock = MagicMock()
        no_shut_mock = MagicMock()
        conf_vlan_mock.execute_command.return_value = ""
        state_vlan_mock.execute_command.return_value = ""
        no_shut_mock.execute_command.return_value = ""
        cte_mock.side_effect = [conf_vlan_mock, state_vlan_mock, no_shut_mock]
        vlan_range = "10"

        self._handler.create_vlan(vlan_range)

        no_shut_mock.execute_command.assert_called()
        state_vlan_mock.execute_command.assert_called()
        conf_vlan_mock.execute_command.assert_called_with(vlan_id=vlan_range)

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_create_multiple_vlan(self, cte_mock):
        conf_vlan_mock = MagicMock()
        state_vlan_mock = MagicMock()
        no_shut_mock = MagicMock()
        conf_vlan_mock.execute_command.return_value = ""
        state_vlan_mock.execute_command.return_value = ""
        no_shut_mock.execute_command.return_value = ""
        response = [conf_vlan_mock, state_vlan_mock, no_shut_mock]
        cte_mock.side_effect = [conf_vlan_mock, state_vlan_mock, no_shut_mock]
        vlan_range = "10, 20, 30"
        cte_mock.side_effect = response

        self._handler.create_vlan(vlan_range)

        no_shut_mock.execute_command.assert_called()
        state_vlan_mock.execute_command.assert_called()

        conf_vlan_mock.execute_command.assert_called_once_with(vlan_id=vlan_range)

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_create_vlan_range(self, cte_mock):
        conf_vlan_mock = MagicMock()
        state_vlan_mock = MagicMock()
        no_shut_mock = MagicMock()
        conf_vlan_mock.execute_command.return_value = ""
        state_vlan_mock.execute_command.return_value = ""
        no_shut_mock.execute_command.return_value = ""
        cte_mock.side_effect = [conf_vlan_mock, state_vlan_mock, no_shut_mock]
        vlan_range = "150-151"

        self._handler.create_vlan(vlan_range)

        no_shut_mock.execute_command.assert_called()
        state_vlan_mock.execute_command.assert_called()
        conf_vlan_mock.execute_command.assert_called_with(vlan_id=vlan_range)

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_get_l2_protocol_tunnel_cmd(self, cte_mock):
        result = self._handler._get_l2_protocol_tunnel_cmd()
        cte_mock.assert_called_once_with(
            self._cli_service, L2_TUNNEL, action_map=None, error_map=None
        )
        self.assertEqual(result, cte_mock.return_value)

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_config_vlan_on_interface_qnq(self, cte_mock):
        vlan_range = 11
        port_name = "Ehternet2/25"
        port_mode = "access"

        conf_interface_mock = MagicMock()
        no_shut_mock = MagicMock()
        enable_switchport_mock = MagicMock()
        switchport_mode_mock = MagicMock()
        switchport_mode_mock.execute_command.return_value = "Ok"
        switchport_allow_vlan_mock = MagicMock()

        cte_mock.side_effect = [
            conf_interface_mock,
            no_shut_mock,
            enable_switchport_mock,
            switchport_mode_mock,
            MagicMock(),
            switchport_allow_vlan_mock,
        ]

        self._handler.set_vlan_to_interface(
            vlan_range=vlan_range,
            port_name=port_name,
            port_mode=port_mode,
            qnq=True,
            c_tag=None,
        )

        conf_interface_mock.execute_command.assert_called_once_with(port_name=port_name)
        no_shut_mock.execute_command.assert_called_once()
        enable_switchport_mock.execute_command.assert_called_once_with()
        switchport_mode_mock.execute_command.assert_called_once_with(
            port_mode="dot1q-tunnel"
        )
        switchport_allow_vlan_mock.execute_command.assert_called_once_with(
            port_mode_access="", vlan_range=vlan_range
        )

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_config_vlan_on_interface_no_qnq_access(self, cte_mock):
        vlan_range = 11
        port_name = "Ehternet2/25"
        port_mode = "access"

        conf_interface_mock = MagicMock()
        no_shut_mock = MagicMock()
        enable_switchport_mock = MagicMock()
        switchport_mode_mock = MagicMock()
        switchport_mode_mock.execute_command.return_value = "Ok"
        switchport_allow_vlan_mock = MagicMock()

        cte_mock.side_effect = [
            conf_interface_mock,
            no_shut_mock,
            enable_switchport_mock,
            switchport_mode_mock,
            switchport_allow_vlan_mock,
        ]

        self._handler.set_vlan_to_interface(
            vlan_range=vlan_range,
            port_name=port_name,
            port_mode=port_mode,
            qnq=False,
            c_tag=None,
        )

        conf_interface_mock.execute_command.assert_called_once_with(port_name=port_name)
        no_shut_mock.execute_command.assert_called_once()
        enable_switchport_mock.execute_command.assert_called_once_with()
        switchport_mode_mock.execute_command.assert_called_once_with(
            port_mode=port_mode
        )
        switchport_allow_vlan_mock.execute_command.assert_called_once_with(
            port_mode_access="", vlan_range=vlan_range
        )

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_config_vlan_on_interface_no_qnq_trunk_auto(self, cte_mock):
        vlan_range = 11
        port_name = "Ehternet2/25"
        port_mode = "trunk"
        error = (
            "Command rejected: "
            'An interface whose trunk encapsulation is "Auto" '
            'can not be configured to "trunk" mode.'
        )

        conf_interface_mock = MagicMock()
        no_shut_mock = MagicMock()
        enable_switchport_mock = MagicMock()
        switchport_mode_mock = MagicMock()
        disable_trunk_auto_mock = MagicMock()
        switchport_mode_mock_w_error = MagicMock()
        switchport_mode_mock_w_error.execute_command.return_value = error
        switchport_allow_vlan_mock = MagicMock()

        cte_mock.side_effect = [
            conf_interface_mock,
            no_shut_mock,
            enable_switchport_mock,
            switchport_mode_mock_w_error,
            disable_trunk_auto_mock,
            switchport_mode_mock,
            switchport_allow_vlan_mock,
        ]

        self._handler.set_vlan_to_interface(
            vlan_range=vlan_range,
            port_name=port_name,
            port_mode=port_mode,
            qnq=False,
            c_tag=None,
        )

        conf_interface_mock.execute_command.assert_called_once_with(port_name=port_name)
        no_shut_mock.execute_command.assert_called_once()
        enable_switchport_mock.execute_command.assert_called_once_with()
        switchport_mode_mock_w_error.execute_command.assert_called_once_with(
            port_mode=port_mode
        )
        disable_trunk_auto_mock.execute_command.assert_called_once()
        switchport_mode_mock.execute_command.assert_called_once_with(
            port_mode=port_mode
        )
        switchport_allow_vlan_mock.execute_command.assert_called_once_with(
            port_mode_trunk="", vlan_range=vlan_range
        )

    @patch(
        "cloudshell.networking.cisco.command_actions.add_remove_vlan_actions"
        ".CommandTemplateExecutor"
    )
    def test_config_vlan_on_interface_no_qnq_trunk(self, cte_mock):
        vlan_range = 11
        port_name = "Ehternet2/25"
        port_mode = "trunk"

        conf_interface_mock = MagicMock()
        no_shut_mock = MagicMock()
        enable_switchport_mock = MagicMock()
        switchport_mode_mock = MagicMock()
        switchport_mode_mock.execute_command.return_value = "Ok"
        switchport_allow_vlan_mock = MagicMock()

        cte_mock.side_effect = [
            conf_interface_mock,
            no_shut_mock,
            enable_switchport_mock,
            switchport_mode_mock,
            switchport_allow_vlan_mock,
        ]

        self._handler.set_vlan_to_interface(
            vlan_range=vlan_range,
            port_name=port_name,
            port_mode=port_mode,
            qnq=False,
            c_tag=None,
        )

        conf_interface_mock.execute_command.assert_called_once_with(port_name=port_name)
        no_shut_mock.execute_command.assert_called_once()
        enable_switchport_mock.execute_command.assert_called_once_with()
        switchport_mode_mock.execute_command.assert_called_once_with(
            port_mode=port_mode
        )
        switchport_allow_vlan_mock.execute_command.assert_called_once_with(
            port_mode_trunk="", vlan_range=vlan_range
        )

        @patch(
            "cloudshell.networking.cisco.command_actions.iface_actions"
            ".CommandTemplateExecutor"
        )
        def test_config_vlan_on_interface_qnq(self, cte_mock):
            vlan_range = 11
            port_name = "Ehternet2/25"
            port_mode = "access"

            conf_interface_mock = MagicMock()
            no_shut_mock = MagicMock()
            enable_switchport_mock = MagicMock()
            switchport_mode_mock = MagicMock()
            switchport_allow_vlan_mock = MagicMock()

            cte_mock.side_effect = [
                conf_interface_mock,
                no_shut_mock,
                enable_switchport_mock,
                switchport_mode_mock,
                MagicMock(),
                switchport_allow_vlan_mock,
            ]

            self._handler.set_vlan_to_interface(
                vlan_range=vlan_range,
                port_name=port_name,
                port_mode=port_mode,
                qnq=True,
                c_tag=None,
            )

            conf_interface_mock.execute_command.assert_called_once_with(
                port_name=port_name
            )
            no_shut_mock.execute_command.assert_called_once()
            enable_switchport_mock.execute_command.assert_called_once_with()
            switchport_mode_mock.execute_command.assert_called_once_with(
                port_mode="dot1q-tunnel"
            )
            switchport_allow_vlan_mock.execute_command.assert_called_once_with(
                port_mode_access="", vlan_range=vlan_range
            )

        @patch(
            "cloudshell.networking.cisco.command_actions.iface_actions"
            ".CommandTemplateExecutor"
        )
        def test_config_vlan_on_interface_no_qnq_access(self, cte_mock):
            vlan_range = 11
            port_name = "Ehternet2/25"
            port_mode = "access"

            conf_interface_mock = MagicMock()
            no_shut_mock = MagicMock()
            enable_switchport_mock = MagicMock()
            switchport_mode_mock = MagicMock()
            switchport_allow_vlan_mock = MagicMock()

            cte_mock.side_effect = [
                conf_interface_mock,
                no_shut_mock,
                enable_switchport_mock,
                switchport_mode_mock,
                switchport_allow_vlan_mock,
            ]

            self._handler.set_vlan_to_interface(
                vlan_range=vlan_range,
                port_name=port_name,
                port_mode=port_mode,
                qnq=False,
                c_tag=None,
            )

            conf_interface_mock.execute_command.assert_called_once_with(
                port_name=port_name
            )
            no_shut_mock.execute_command.assert_called_once()
            enable_switchport_mock.execute_command.assert_called_once_with()
            switchport_mode_mock.execute_command.assert_called_once_with(
                port_mode=port_mode
            )
            switchport_allow_vlan_mock.execute_command.assert_called_once_with(
                port_mode_access="", vlan_range=vlan_range
            )

        @patch(
            "cloudshell.networking.cisco.command_actions.iface_actions"
            ".CommandTemplateExecutor"
        )
        def test_config_vlan_on_interface_no_qnq_trunk(self, cte_mock):
            vlan_range = 11
            port_name = "Ehternet2/25"
            port_mode = "trunk"

            conf_interface_mock = MagicMock()
            no_shut_mock = MagicMock()
            enable_switchport_mock = MagicMock()
            switchport_mode_mock = MagicMock()
            switchport_allow_vlan_mock = MagicMock()

            cte_mock.side_effect = [
                conf_interface_mock,
                no_shut_mock,
                enable_switchport_mock,
                switchport_mode_mock,
                switchport_allow_vlan_mock,
            ]

            self._handler.set_vlan_to_interface(
                vlan_range=vlan_range,
                port_name=port_name,
                port_mode=port_mode,
                qnq=False,
                c_tag=None,
            )

            conf_interface_mock.execute_command.assert_called_once_with(
                port_name=port_name
            )
            no_shut_mock.execute_command.assert_called_once()
            enable_switchport_mock.execute_command.assert_called_once_with()
            switchport_mode_mock.execute_command.assert_called_once_with(
                port_mode=port_mode
            )
            switchport_allow_vlan_mock.execute_command.assert_called_once_with(
                port_mode_trunk="", vlan_range=vlan_range
            )
