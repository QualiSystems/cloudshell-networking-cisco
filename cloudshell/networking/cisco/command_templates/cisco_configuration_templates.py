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

CONFIGURE_REPLACE = CommandTemplate('configure replace {path}',
                                    action_map=OrderedDict({
                                        '[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session,
                                                                                       logger: session.send_line('yes',
                                                                                                                 logger),
                                        '\(y\/n\)': lambda session, logger: session.send_line('y', logger),
                                        '[\[\(][Nn]o[\)\]]': lambda session, logger: session.send_line('y', logger),
                                        '[\[\(][Yy]es[\)\]]': lambda session, logger: session.send_line('y', logger),
                                        '[\[\(][Yy]/[Nn][\)\]]': lambda session, logger: session.send_line('y', logger),
                                        'overwrit+e': lambda session, logger: session.send_line('yes', logger)}),
                                    error_map=OrderedDict({
                                        "[Rr]ollback\s*[Dd]one|(?<=%).*(not.*|in)valid.*(?=\n)":
                                            Exception("Configure_Replace",
                                                      "Configure replace completed with error"),
                                        "[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected":
                                            Exception('Configure_Replace', 'Override mode is not supported')
                                    }))

SNMP_SERVER_COMMUNITY = CommandTemplate("snmp-server community {snmp_community} ro",
                                        action_map=OrderedDict({
                                            'commit.*[\[\(][Yy]es/[Nn]o.*[\)\]]': lambda session,
                                                                                         logger: session.send_line(
                                                'yes', logger)}))
NO_SNMP_SERVER_COMMUNITY = CommandTemplate("no snmp-server community {snmp_community}",
                                           action_map=OrderedDict({
                                               'commit.*[\[\(][Yy]es/[Nn]o.*[\)\]]': lambda session,
                                                                                            logger: session.send_line(
                                                   'yes', logger)}))

BOOT_SYSTEM_FILE = CommandTemplate("boot system flash bootflash:{firmware_file_name}")
CONFIG_REG = CommandTemplate("config-reg 0x2102")

WRITE_ERASE = CommandTemplate('write erase',
                              action_map=OrderedDict({
                                  '[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session,
                                                                                 logger: session.send_line('yes',
                                                                                                           logger),
                                  '\(y\/n\)': lambda session, logger: session.send_line('y', logger),
                                  '[\[\(][Nn]o[\)\]]': lambda session, logger: session.send_line('y', logger),
                                  '[\[\(][Yy]es[\)\]]': lambda session, logger: session.send_line('y', logger),
                                  '[\[\(][Yy]/[Nn][\)\]]': lambda session, logger: session.send_line('y', logger),
                              }))

RELOAD = CommandTemplate("reload", action_map=OrderedDict(
    {r"[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]": lambda session, logger: session.send_line('yes', logger),
     r"\(y\/n\)|continue": lambda session, logger: session.send_line('y', logger),
     r"[\[\(][Yy]/[Nn][\)\]]": lambda session, logger: session.send_line('y', logger)
     }))

CONSOLE_RELOAD = CommandTemplate("reload")
