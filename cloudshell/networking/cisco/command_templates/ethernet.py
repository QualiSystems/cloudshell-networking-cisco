__author__ = 'wise__000'

from cloudshell.networking.utils import *
from cloudshell.networking.cisco.command_templates.cisco_interface \
    import CiscoInterface, ParametersService, CommandTemplate

class Ethernet(CiscoInterface):
    COMMANDS_TEMPLATE = {
        'ip': CommandTemplate('ip {0}', validateIP, 'Wrong ip address!'),
        'ip_address': CommandTemplate('ip address {0} {1}', [validateIP, validateIP],
                                      ['Wrong ip address!', 'Wrong ip mask!']),
        'description': CommandTemplate('description {0}', r'[\w ]+', 'Wrong description!'),
        'switchport_mode_trunk': CommandTemplate('switchport mode trunk'),
        'trunk_encapsulation': CommandTemplate('switchport trunk encapsulation {0}',
                                               [r'\bdot1q\b|\bisl\b|\bnegotiate\b'],
                                               'Wrong encapsulation name!'),
        'trunk_allow_vlan': CommandTemplate('switchport trunk allowed vlan {0}',
                                            validateVlanRange, 'Wrong description!'),
        'trunk_remove_vlan': CommandTemplate('switchport trunk allowed vlan remove {0}',
                                             validateVlanRange, 'Wrong description!'),
        'access_allow_vlan': CommandTemplate('switchport access vlan {0}',
                                             validateVlanRange, 'Wrong description!'),
        'access_remove_vlan': CommandTemplate('no switchport access vlan {0}',
                                              validateVlanRange, 'Wrong description!'),
        'spanning_tree_type': CommandTemplate('spanning-tree {0} type {1}',
                                              [validateSpanningTreeType, r'\bedge\b|\bnetwork\b'],
                                              ['Wrong description!', 'Wrong description!']),
        'channel_group': CommandTemplate('channel-group {0}', r'[\w ]+', 'Wrong mode number'),
        'channel_group_mode': CommandTemplate('channel-group {0} mode {1}', [r'[\w ]+', r'\bactive\b|\bpassive\b|\bon\b'],
                                              ['Wrong mode number', 'Wrong state']),
        'no_shutdown': CommandTemplate('no shutdown'),
        'qnq': CommandTemplate('switchport mode dot1q-tunnel'),
        'mode_trunk': CommandTemplate('mode trunk')
    }

    def get_commands_list(self, **kwargs):
        prepared_commands = CiscoInterface.get_commands_list(self, **kwargs)

        for command, value in kwargs.items():
            if command in Ethernet.COMMANDS_TEMPLATE:
                command_template = Ethernet.COMMANDS_TEMPLATE[command]
                prepared_commands.append(ParametersService.get_validate_list(command_template, value))

        return prepared_commands