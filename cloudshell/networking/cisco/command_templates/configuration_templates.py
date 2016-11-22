from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

COPY = CommandTemplate('copy {src} {dst} [vrf {vrf}]',
                       action_map=OrderedDict({
                           r'\[confirm\]': lambda session, logger: session.send_line('', logger),
                           r'\(y/n\)': lambda session, logger: session.send_line('y', logger),
                           r'[Oo]verwrit+e': lambda session, logger: session.send_line('y', logger),
                           r'\([Yy]es/[Nn]o\)': lambda session, logger: session.send_line('yes', logger),
                           r'\s+[Vv][Rr][Ff]\s+': lambda session, logger: session.send_line('', logger)}))
