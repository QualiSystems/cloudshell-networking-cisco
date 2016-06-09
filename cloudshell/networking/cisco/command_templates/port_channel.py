__author__ = 'g8y3e'

from cloudshell.networking.utils import *
from cloudshell.networking.cisco.command_templates.cisco_interface \
    import CiscoInterface, CommandTemplateValidator, CommandTemplate

class PortChannel(CiscoInterface):
    COMMANDS_TEMPLATE = {
        'description' : CommandTemplate('description {0}', r'[\w ]+', 'Wrong description!'),
        'switchport_mode' : CommandTemplate('switchport mode {0}', r'[\w]+',
                                            'Wrong switchport mode!'),
        'vpc' : CommandTemplate('vpc {0}', r'[0-9]+|peer-link', 'Wrong vpc id!'),
        'allow_trunk_vlan' : CommandTemplate('switchport trunk allowed vlan {0}', r'[0-9]+',
                                             'Wrong allowed vlan id!'),
        'spanning_tree' : CommandTemplate('spanning-tree {0} {1}', [r'[\w ]+', r'[\w ]+'],
                                          ['Wrong spanning-tree parameter!', 'Wrong spanning-tree value']),
        'speed' : CommandTemplate('speed {0}', r'[0-9]+', 'Wrong speed number!'),
        'untagged' : CommandTemplate('untagged {0} {1}', [r'\w+', r'[0-9]+'],
                                    ['Wrong untagged parameter!', 'Wrong untagged value!'])
    }

    def get_commands_list(self, **kwargs):
        prepared_commands = CiscoInterface.get_commands_list(self, **kwargs)

        for command, value in kwargs.items():
            if command in PortChannel.COMMANDS_TEMPLATE:
                command_tamplate = PortChannel.COMMANDS_TEMPLATE[command]

                if 'allow_trunk_vlan' in command:
                    prepared_commands.append('switchport')

                prepared_commands.append(CommandTemplateValidator.get_validate_list(command_tamplate, value))

        return prepared_commands




