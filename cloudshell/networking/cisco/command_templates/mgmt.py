__author__ = 'wise__000'

from cloudshell.networking.utils import *
from cloudshell.networking.cisco.command_templates.cisco_interface \
    import CiscoInterface, CommandTemplateValidator, CommandTemplate

class Mgmt(CiscoInterface):
    COMMANDS_TEMPLATE = {
        'ip_address': CommandTemplate('ip address {0} {1}', [validateIP, validateIP],
                                       ['Wrong ip address!', 'Wrong ip mask!']),
        'vrf_member': CommandTemplate('vrf member {0}', r'[\w ]+', 'Wrong membership!'),
        'description': CommandTemplate('description {0}', r'[\w ]+', 'Wrong description!'),
        #'clock_timezone': CommandTemplate('clock timezone {0} {1} {2}', [r'[0-9]+', r'[0-9]+', r'[0-9]+'],
         #                                 ['Wrong hours number!', 'Wrong minutes number!', 'Wrong seconds number!']),
        'no_shutdown': CommandTemplate('no shutdown')
    }

    def get_commands_list(self, **kwargs):
        prepared_commands = CiscoInterface.get_commands_list(self, **kwargs)
        for command, value in kwargs.items():
            if command in Mgmt.COMMANDS_TEMPLATE:
                command_tamplate = Mgmt.COMMANDS_TEMPLATE[command]
                prepared_commands.append(CommandTemplateValidator.get_validate_list(command_tamplate, value))
        return prepared_commands