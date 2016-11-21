from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

COPY_ACTION_MAP = OrderedDict({
    r'\[confirm\]': lambda session, logger: session.send_line('', logger),
    r'\(y/n\)': lambda session, logger: session.send_line('y', logger),
    r'[Oo]verwrit+e': lambda session, logger: session.send_line('y', logger),
    r'\([Yy]es/[Nn]o\)': lambda session, logger: session.send_line('yes', logger),
    r'\s+[Vv][Rr][Ff]\s+': lambda session, logger: session.send_line('', logger)})

COPY = CommandTemplate('copy {source} {destination}[ vrf {vrf}]',
                       action_map=COPY_ACTION_MAP)

COPY_WITH_VRF = CommandTemplate(COPY._command + " vrf {vrf}",
                                action_map=COPY_ACTION_MAP)
