__author__ = 'g8y3e'

from qualipy.common.libs.utils import *
from cloudshell.networking.cisco.command_templates.cisco_interface \
    import CiscoInterface, ParametersService, CommandTemplate

class Vlan(CiscoInterface):
    COMMANDS_TEMPLATE = {
        'ip_address': CommandTemplate('ip address {0} {1}', [validateIP, validateIP],
                                      ['Wrong ip address!', 'Wrong ip mask!']),
        'hsrp': CommandTemplate('hsrp {0}', ['[0-9]+'],
                                ['Wrong router protocol id!']),
        'authentication': CommandTemplate('authentication {0}', [r'\w+'],
                                          ['Wrong authentication name!']),
        'ip': CommandTemplate('ip {0}', [validateIP],
                              ['Wrong ip address!']),
        'no_shut': CommandTemplate('no shut'),
        'preempt': CommandTemplate('preempt'),
        'priority': CommandTemplate('priority {0}', ['[0-9]+'], ['Wrong priority number!']),
        'track': CommandTemplate('track {0} decrement {1}', [r'[0-9]+', r'[0-9]+'],
                                  ['Wrong track number!', 'Wrong track decrement number!'])
    }

    def get_commands_list(self, **kwargs):
        prepared_commands = CiscoInterface.get_commands_list(self, **kwargs)

        for command, value in kwargs.items():
            if command in Vlan.COMMANDS_TEMPLATE:
                command_template = Vlan.COMMANDS_TEMPLATE[command]
                prepared_commands.append(ParametersService.get_validate_list(command_template, value))

        return prepared_commands




