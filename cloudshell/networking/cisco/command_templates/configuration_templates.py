from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

COPY = CommandTemplate('copy {src} {dst} [vrf {vrf}]',
                       action_map=OrderedDict({
                           r'\[confirm\]': lambda session, logger: session.send_line('', logger),
                           r'\(y/n\)': lambda session, logger: session.send_line('y', logger),
                           r'[Oo]verwrit+e': lambda session, logger: session.send_line('y', logger),
                           r'\([Yy]es/[Nn]o\)': lambda session, logger: session.send_line('yes', logger),
                           r'\s+[Vv][Rr][Ff]\s+': lambda session, logger: session.send_line('', logger)}))

DEL = CommandTemplate('del {target}', action_map=OrderedDict(
    {'[confirm]': lambda session, logger: session.send_line('', logger),
     '\?': lambda session, logger: session.send_line('', logger)}))

CONFIGURE_REPLACE = CommandTemplate('configure replace {path}', action_map=OrderedDict({
    '[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session, logger: session.send_line('yes', logger),
    '\(y\/n\)': lambda session, logger: session.send_line('y', logger),
    '[\[\(][Nn]o[\)\]]': lambda session, logger: session.send_line('y', logger),
    '[\[\(][Yy]es[\)\]]': lambda session, logger: session.send_line('y', logger),
    '[\[\(][Yy]/[Nn][\)\]]': lambda session, logger: session.send_line('y', logger),
    'overwrit+e': lambda session, logger: session.send_line('yes', logger)}), error_map={
    "[Ee]rror.*$|[Rr]ollback\s*[Dd]one|(?<=%).*(not.*|in)valid.*(?=\n)})":
        Exception("Configure_Replace",
                  "Configure replace completed with error")})

SNMP_SERVER_COMMUNITY = CommandTemplate("snmp-server community {snmp_community} ro")
NO_SNMP_SERVER_COMMUNITY = CommandTemplate("no snmp-server community {snmp_community}")