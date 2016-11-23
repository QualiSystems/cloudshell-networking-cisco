from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

# IP_ADDRESS = CommandTemplate('ip address {ip} {mask}')
CONFIGURE_VLAN = CommandTemplate('vlan {vlan_id}',
                                 error_map=OrderedDict({"%.*\.": Exception('CONFIGURE_VLAN', "Error")}))
STATE_ACTIVE = CommandTemplate('state active')
NO_SHUTDOWN = CommandTemplate('no shutdown')
# HSRP = CommandTemplate('hsrp {0}', ['[0-9]+'],
#                        ['Wrong router protocol id!'])
# AUTHENTICATION = CommandTemplate('authentication {0}', [r'\w+'],
#                                  ['Wrong authentication name!'])
# IP = CommandTemplate('ip {0}', [validate_ip],
#                      ['Wrong ip address!'])

# PREEMPT = CommandTemplate('preempt')
# PRIORITY = CommandTemplate('priority {0}', ['[0-9]+'], ['Wrong priority number!'])
# TRACK = CommandTemplate('track {0} decrement {1}', [r'[0-9]+', r'[0-9]+'],
#                         ['Wrong track number!', 'Wrong track decrement number!'])
