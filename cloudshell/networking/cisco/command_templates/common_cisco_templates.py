# ToDo all previously defined cisco commands, left commented for future use

# SWITCHPORT = CommandTemplate('switchport')
# IP = CommandTemplate('ip {0}', validate_ip, 'Wrong ip address!')
# IP_ADDRESS = CommandTemplate('ip address {0} {1}', [validate_ip, validate_ip],
#                              ['Wrong ip address!', 'Wrong ip mask!'])
# DESCRIPTION = CommandTemplate('description {0}', r'[\w ]+', 'Wrong description!')
#
# TRUNK_ENCAPSULATION = CommandTemplate('switchport trunk encapsulation {0}', [r'\bdot1q\b|\bisl\b|\bnegotiate\b'],
#                                       'Wrong encapsulation name!')
# EXIT = CommandTemplate('exit')
#
# SPANNING_TREE_TYPE = CommandTemplate('spanning-tree {0} type {1}',
#                                      [validate_spanning_tree_type, r'\bedge\b|\bnetwork\b'],
#                                      ['Wrong description!', 'Wrong description!'])
# CHANNEL_GROUP = CommandTemplate('channel-group {0}', r'[\w ]+', 'Wrong mode number')
# CHANNEL_GROUP_MODE = CommandTemplate('channel-group {0} mode {1}', [r'[\w ]+', r'\bactive\b|\bpassive\b|\bon\b'],
#                                      ['Wrong mode number', 'Wrong state'])
#
# COMMANDS_TEMPLATE = {
#     'ip_address': CommandTemplate('ip address {0} {1}', [validateIP, validateIP],
#                                   ['Wrong ip address!', 'Wrong ip mask!']),
#     'vrf_member': CommandTemplate('vrf member {0}', r'[\w ]+', 'Wrong membership!'),
#     'description': CommandTemplate('description {0}', r'[\w ]+', 'Wrong description!'),
#     #'clock_timezone': CommandTemplate('clock timezone {0} {1} {2}', [r'[0-9]+', r'[0-9]+', r'[0-9]+'],
#     #                                 ['Wrong hours number!', 'Wrong minutes number!', 'Wrong seconds number!']),
#     'no_shutdown': CommandTemplate('no shutdown'),
#     'switchport_mode' : CommandTemplate('switchport mode {0}', r'[\w]+',
#                                         'Wrong switchport mode!'),
#     'vpc' : CommandTemplate('vpc {0}', r'[0-9]+|peer-link', 'Wrong vpc id!'),
#     'allow_trunk_vlan' : CommandTemplate('switchport trunk allowed vlan {0}', r'[0-9]+',
#                                          'Wrong allowed vlan id!'),
#     'spanning_tree' : CommandTemplate('spanning-tree {0} {1}', [r'[\w ]+', r'[\w ]+'],
#                                       ['Wrong spanning-tree parameter!', 'Wrong spanning-tree value']),
#     'speed' : CommandTemplate('speed {0}', r'[0-9]+', 'Wrong speed number!'),
#     'untagged' : CommandTemplate('untagged {0} {1}', [r'\w+', r'[0-9]+'],
#                                  ['Wrong untagged parameter!', 'Wrong untagged value!'])
# }
# TEMPLATE_COMMANDS = {'description': 'description {0}',
#                      'ip': 'ip {0}|SOmeReGEXP',
#                      'ip address': 'ip address {0} {1}',
#                      'hsrp': "hsrp {0}",
#                      'preempt': 'preempt',
#                      'priority': 'priority {0}',
#                      'authentication': 'authentication {0}',
#                      'track': 'track {0} decrement {1}',
#                      'mode trunk': 'switchport mode trunk',
#                      'allow trunk vlan': 'switchport trunk allowed vlan {0}',
#                      'access vlan': 'switchport access vlan {0}',
#                      'no swithcport': 'no switchport',
#                      'no shutdown': 'no shutdown',
#                      'shutdown': 'shutdown',
#                      'spanning tree port type': 'spanning-tree port type {0}',
#                      'channel group': 'channel-group {0}',
#                      'channel group mode': 'channel-group {0} mode {1}',
#                      'vpc': 'vpc {0}',
#                      'configure interface': 'interface {0} {1}',
#                      'speed': 'speed {0}'}