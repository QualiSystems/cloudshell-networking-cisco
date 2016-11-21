from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.devices.networking_utils import validate_ip, validate_vlan_number, validate_vlan_range, \
    validate_spanning_tree_type

SWITCHPORT = CommandTemplate('switchport')
IP = CommandTemplate('ip {0}', validate_ip, 'Wrong ip address!')
IP_ADDRESS = CommandTemplate('ip address {0} {1}', [validate_ip, validate_ip],
                             ['Wrong ip address!', 'Wrong ip mask!'])
DESCRIPTION = CommandTemplate('description {0}', r'[\w ]+', 'Wrong description!')
SWITCHPORT_MODE_TRUNK = CommandTemplate('switchport mode trunk')
SWITCHPORT_MODE_ACCESS = CommandTemplate('switchport mode access')
TRUNK_ENCAPSULATION = CommandTemplate('switchport trunk encapsulation {0}', [r'\bdot1q\b|\bisl\b|\bnegotiate\b'],
                                      'Wrong encapsulation name!')
EXIT = CommandTemplate('exit')
TRUNK_ALLOW_VLAN = CommandTemplate('switchport trunk allowed vlan {0}',
                                   validate_vlan_range, 'Wrong vlan number(s)!')
TRUNK_REMOVE_VLAN = CommandTemplate('switchport trunk allowed vlan remove {0}',
                                    validate_vlan_range, 'Wrong vlan number!')
ACCESS_ALLOW_VLAN = CommandTemplate('switchport access vlan {0}',
                                    validate_vlan_number, 'Wrong vlan number!')
ACCESS_REMOVE_VLAN = CommandTemplate('no switchport access vlan {0}',
                                     validate_vlan_number, 'Wrong vlan number!')
SPANNING_TREE_TYPE = CommandTemplate('spanning-tree {0} type {1}',
                                     [validate_spanning_tree_type, r'\bedge\b|\bnetwork\b'],
                                     ['Wrong description!', 'Wrong description!'])
CHANNEL_GROUP = CommandTemplate('channel-group {0}', r'[\w ]+', 'Wrong mode number')
CHANNEL_GROUP_MODE = CommandTemplate('channel-group {0} mode {1}', [r'[\w ]+', r'\bactive\b|\bpassive\b|\bon\b'],
                                     ['Wrong mode number', 'Wrong state'])
NO_SHUTDOWN = CommandTemplate('no shutdown')
QNQ = CommandTemplate('switchport mode dot1q-tunnel')
MODE_TRUNK = CommandTemplate('mode trunk')
