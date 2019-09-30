from unittest import TestCase

from cloudshell.cli.service.cli_service_impl import CliServiceImpl

from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions

try:
    from unittest.mock import MagicMock, create_autospec, patch
except ImportError:
    from mock import MagicMock, create_autospec, patch


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
