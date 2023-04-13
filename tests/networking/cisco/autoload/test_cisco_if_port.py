from unittest.mock import Mock

import pytest

from cloudshell.networking.cisco.autoload.cisco_snmp_if_port import CiscoSnmpIfPort

# test_cisco_snmp_if_port.py - Generated by CodiumAI


"""
Code Analysis:
- The CiscoSnmpIfPort class is a subclass of SnmpIfEntity and is used to represent a Cisco network interface port in SNMP.
- The class has a regular expression pattern (PORT_NAME_MATCH) that matches the names of different types of ports (Ethernet, GigE, Serial, Sonet, POS, Port-channel, Bundle-Ether).
- The class has a property called port_name that returns the name of the port. If the name of the port does not match the PORT_NAME_MATCH pattern, it returns the if_name instead. The returned name is modified to replace forward slashes with hyphens and colons with underscores.
- The class inherits several methods and fields from its parent class, SnmpIfEntity, including if_name, if_descr_name, if_index, if_type, if_speed, if_mac, if_admin_status, if_oper_status, if_last_change, if_in_octets, if_out_octets, if_in_ucast_pkts, if_out_ucast_pkts, if_in_nucast_pkts, if_out_nucast_pkts, if_in_discards, if_out_discards, if_in_errors, if_out_errors, if_in_unknown_protos, if_out_q_len, if_alias, if_phys_address, if_mtu, if_high_speed, if_promiscuous_mode, if_duplex, if_autoneg, if_media_type, if_vlan, if_vrf, if_pppoe, if_pppoe_session_id, if_pppoe_remote_mac, if_pppoe_remote_ip, if_pppoe_local_ip, if_pppoe_local_mac, if_pppoe_service_name, if_pppoe_ac_name, if_pppoe_vlan, if_pppoe_max_payload, if_pppoe_mru, if_pppoe_mtu, if_pppoe_relay_session_id, if_pppoe_relay_remote_id, if_pppoe_relay_circuit_id, if_pppoe_relay_remote_mac, if_pppoe_relay_local_mac, if_pppoe_relay_local_ip, if_pppoe_relay_remote_ip, if_pppoe_relay_service_name, if_pppoe_relay_ac_name, if_pppoe_relay_vlan, if_pppoe_relay_max_payload, if_pppoe_relay_mru, if_pppoe_relay_mtu.
"""

"""
Test Plan:
- test_port_name_valid_match(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with a valid name that matches the PORT_NAME_MATCH pattern. Tags: [happy path]
- test_port_name_valid_no_match(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with a valid name that does not match the PORT_NAME_MATCH pattern. Tags: [happy path]
- test_port_name_empty_name(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with an empty name. Tags: [edge case]
- test_port_name_only_slashes_or_colons(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with a name that contains only forward slashes or colons. Tags: [edge case]
- test_inherited_methods_and_fields(): tests that the inherited methods and fields from SnmpIfEntity behave as expected in a CiscoSnmpIfPort instance. Tags: [general behavior]
- test_port_name_slashes_and_colons(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with a name that contains both forward slashes and colons. Tags: [edge case]
- test_port_name_long_name(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with a name that is longer than the maximum allowed length. Tags: [edge case]
- test_port_name_special_characters(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with a name that contains special characters such as spaces or underscores. Tags: [happy path]
- test_port_name_numbers_and_non_alphabetic_characters(): tests that the port_name property returns the expected value for a CiscoSnmpIfPort instance with a name that contains numbers or other non-alphabetic characters. Tags: [happy path]
- test_invalid_arguments(): tests the behavior of the class when instantiated with invalid arguments. Tags: [edge case]
- test_multi_threaded_environment(): tests the behavior of the class when used in a multi-threaded environment. Tags: [edge case]
"""


class TestCiscoSnmpIfPort:
    @pytest.mark.parametrize(
        "row,expected_name",
        [
            (
                {"ifDescr": Mock(safe_value="GigabitEthernet1/0/1")},
                "GigabitEthernet1-0-1",
            ),
            ({"ifDescr": Mock(safe_value="GigE1/0/1")}, "GigE1-0-1"),
            ({"ifDescr": Mock(safe_value="TenGigE1/0/1")}, "TenGigE1-0-1"),
            (
                {"ifDescr": Mock(safe_value="TwentyFiveGigE1/0/1")},
                "TwentyFiveGigE1-0-1",
            ),
            ({"ifDescr": Mock(safe_value="FortyGigE1/0/1")}, "FortyGigE1-0-1"),
            ({"ifDescr": Mock(safe_value="HundredGigE1/0/1")}, "HundredGigE1-0-1"),
            (
                {"ifDescr": Mock(safe_value="FourHundredGigE0/1/0/1")},
                "FourHundredGigE0-1-0-1",
            ),
            ({"ifDescr": Mock(safe_value="Port-Channel0")}, "Port-Channel0"),
            ({"ifDescr": Mock(safe_value="Bundle-Ether421")}, "Bundle-Ether421"),
            ({"ifDescr": Mock(safe_value="Serial0/2/0:0")}, "Serial0-2-0_0"),
        ],
    )
    def test_port_name_valid_match(self, row, expected_name):
        port = CiscoSnmpIfPort("1", row)
        assert port.port_name == expected_name

    @pytest.mark.parametrize(
        "row,expected_name",
        [
            (
                {
                    "ifDescr": Mock(safe_value="A Magic Port GigabitEthernet1/0/1"),
                    "ifName": Mock(safe_value="GigabitEthernet1/0/1"),
                },
                "GigabitEthernet1-0-1",
            ),
            (
                {
                    "ifDescr": Mock(safe_value="A Magic Port GigabitEthernet1/0/1"),
                    "ifName": Mock(safe_value="Gi1/0/1"),
                },
                "Gi1-0-1",
            ),
            (
                {
                    "ifDescr": Mock(safe_value="Backplane-GigabitEthernet1/0/1"),
                    "ifName": Mock(safe_value="GigabitEthernet1/0/1"),
                },
                "Backplane-GigabitEthernet1-0-1",
            ),
            (
                {
                    "ifDescr": Mock(
                        safe_value="Adaptive Security Appliance 'GigabitEthernet0/3' "
                        "interface"
                    ),
                    "ifName": Mock(safe_value="GigabitEthernet0/3"),
                },
                "GigabitEthernet0-3",
            ),
        ],
    )
    def test_port_name_valid_no_match(self, row, expected_name):
        port = CiscoSnmpIfPort("1", row)
        assert port.port_name == expected_name

    def test_port_name_empty_name(self):
        port = CiscoSnmpIfPort(
            "1", {"ifDescr": Mock(safe_value=""), "ifName": Mock(safe_value="")}
        )
        assert port.port_name == ""

    def test_inherited_methods_and_fields(self):
        port = CiscoSnmpIfPort(
            "1", {"ifDescr": Mock(safe_value=""), "ifName": Mock(safe_value="")}
        )
        assert port.if_index == "1"