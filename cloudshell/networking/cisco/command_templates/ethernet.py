from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.networking_utils import validateIP, validateVlanNumber, validateVlanRange, validateSpanningTreeType

ETHERNET_COMMANDS_TEMPLATES = {
    'switchport': CommandTemplate('switchport'),
    'ip': CommandTemplate('ip {0}', validateIP, 'Wrong ip address!'),
    'ip_address': CommandTemplate('ip address {0} {1}', [validateIP, validateIP],
                                  ['Wrong ip address!', 'Wrong ip mask!']),
    'description': CommandTemplate('description {0}', r'[\w ]+', 'Wrong description!'),
    'switchport_mode_trunk': CommandTemplate('switchport mode trunk'),
    'switchport_mode_access': CommandTemplate('switchport mode access'),
    'trunk_encapsulation': CommandTemplate('switchport trunk encapsulation {0}',
                                           [r'\bdot1q\b|\bisl\b|\bnegotiate\b'],
                                           'Wrong encapsulation name!'),
    'exit': CommandTemplate('exit'),
    'trunk_allow_vlan': CommandTemplate('switchport trunk allowed vlan {0}',
                                        validateVlanRange, 'Wrong vlan number(s)!'),
    'trunk_remove_vlan': CommandTemplate('switchport trunk allowed vlan remove {0}',
                                         validateVlanRange, 'Wrong vlan number!'),
    'access_allow_vlan': CommandTemplate('switchport access vlan {0}',
                                         validateVlanNumber, 'Wrong vlan number!'),
    'access_remove_vlan': CommandTemplate('no switchport access vlan {0}',
                                          validateVlanNumber, 'Wrong vlan number!'),
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
