__author__ = 'wise__000'

class InterfacesConfigurator:
    TEMPLATE_COMMANDS = {'description': 'description {0}',
                'ip': 'ip {0}|SOmeReGEXP',
                'ip address': 'ip address {0} {1}',
                'hsrp': "hsrp {0}",
                'preempt': 'preempt',
                'priority': 'priority {0}',
                'authentication': 'authentication {0}',
                'track': 'track {0} decrement {1}',
                'mode trunk': 'switchport mode trunk',
                'allow trunk vlan': 'switchport trunk allowed vlan {0}',
                'access vlan': 'switchport access vlan {0}',
                'no swithcport': 'no switchport',
                'no shutdown': 'no shutdown',
                'shutdown': 'shutdown',
                'spanning tree port type': 'spanning-tree port type {0}',
                'channel group': 'channel-group {0}',
                'channel group mode': 'channel-group {0} mode {1}',
                'vpc': 'vpc {0}',
                'configure interface': 'interface {0} {1}',
                'speed': 'speed {0}'}

    def getInterfaceConfigurationCommands(self, incomingArgs):
        prepared_commands = []
        if 'Name' in incomingArgs and incomingArgs['Name'] != '' and 'Id' in incomingArgs and incomingArgs['Id'] != '':
            prepared_commands.append(self.TEMPLATE_COMMANDS['configure interface'].format(incomingArgs['Name'],
                                                                                          incomingArgs['Id']))
            for command, value in incomingArgs.items():
                    if command.lower() in self.TEMPLATE_COMMANDS:
                        if 'track' in command.lower():
                            if 'mode' in command.lower():
                                mode = value
                            else:
                                track = value
                            if 'mode' in locals() and 'track' in locals():
                                prepared_commands.append(self.TEMPLATE_COMMANDS['track'].format(track, mode))
                            continue
                        if 'address' in command.lower():
                            if 'mask' in command.lower():
                                mask = value
                            else:
                                address = value
                            if 'mask' in locals() and 'address' in locals():
                                prepared_commands.append(self.TEMPLATE_COMMANDS['ip address'].format(track, mode))
                            continue
                        if value is not None:
                            prepared_commands.append(self.TEMPLATE_COMMANDS[command.lower()].format(value))
                        else:
                            prepared_commands.append(self.TEMPLATE_COMMANDS[command.lower()])
        return prepared_commands

    def noShutdown(self):
        return 'no shutdown'

    def exit(self):
        return 'exit'
