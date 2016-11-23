from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

CONFIGURE_INTERFACE = CommandTemplate('interface {0}')

SHUTDOWN = CommandTemplate('[no{no}] shutdown')

SWITCHPORT_MODE = CommandTemplate('[no{no}] switchport [mode {port_mode}]',
                                  action_map=OrderedDict(
                                      {'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session: session.send_line('yes'),
                                       '[\[\(][Yy]/[Nn][\)\]]': lambda session: session.send_line('y')}),
                                  error_map={
                                      "[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected":
                                          Exception('SWITCHPORT_MODE', 'Failed to switch port mode'),
                                  })

SWITCHPORT_ALLOW_VLAN = CommandTemplate(
    '[no{no}] switchport [trunk{port_mode_trunk} allowed] [access{port_mode_access}] vlan {vlan_range}',
    action_map=OrderedDict(
        {'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session: session.send_line('yes'),
         '[\[\(][Yy]/[Nn][\)\]]': lambda session: session.send_line('y')}),
    error_map={
        "[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected": Exception('SWITCHPORT_MODE',
                                                                            'Failed to switch port mode')})

ACCESS_ALLOW_VLAN = CommandTemplate('[no{no}] switchport access vlan {0}')
