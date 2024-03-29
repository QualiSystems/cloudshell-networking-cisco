# !/usr/bin/python

from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

COPY = CommandTemplate(
    "copy {src} {dst} [vrf {vrf}]",
    action_map=OrderedDict(
        {
            r"\[confirm\]": lambda session, logger: session.send_line("", logger),
            r"\(y/n\)": lambda session, logger: session.send_line("y", logger),
            r"[Oo]verwrit+e": lambda session, logger: session.send_line("y", logger),
            r"\([Yy]es/[Nn]o\)": lambda session, logger: session.send_line(
                "yes", logger
            ),
            r"\s+[Vv][Rr][Ff]\s+": lambda session, logger: session.send_line(
                "", logger
            ),
        }
    ),
    error_map={
        r"permission\s*denied": "Failed to save configuration: Permission " "Denied",
        r"invalid\s*input": "Failed to save configuration: Invalid input",
        r"\S+isk\d+://scp://": "SCP is no longer supported by IOS-XR",
    },
)

DEL = CommandTemplate(
    "del {target}",
    action_map=OrderedDict(
        {
            r"\[confirm\]": lambda session, logger: session.send_line("", logger),
            r"\?": lambda session, logger: session.send_line("", logger),
        }
    ),
)

CONFIGURE_REPLACE = CommandTemplate(
    "configure replace {path} [{vrf}]",
    action_map=OrderedDict(
        {
            r"[\[\(][Yy]es/[Nn]o[\)\]]": lambda session, logger: session.send_line(
                "yes", logger
            ),
            r"\[confirm\]": lambda session, logger: session.send_line("", logger),
            r"\(y\/n\)": lambda session, logger: session.send_line("y", logger),
            r"[\[\(][Nn]o[\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"[\[\(][Yy]es[\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"[\[\(][Yy]/[Nn][\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"overwrit+e": lambda session, logger: session.send_line("yes", logger),
        }
    ),
    error_map=OrderedDict(
        {
            r"[Aa]borting\s*[Rr]ollback|"
            r"[Rr]ollback\s*[Aa]borted|"
            r"(?<=%).*(not.*|in)valid.*(?=\n)": Exception(
                "Configure replace completed with error"
            ),
            r"[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected": Exception(
                "Restore override mode is not supported"
            ),
        }
    ),
)

WRITE_ERASE = CommandTemplate(
    "write erase",
    action_map=OrderedDict(
        {
            r"[\[\(][Yy]es/[Nn]o[\)\]]": lambda session, logger: session.send_line(
                "yes", logger
            ),
            r"\[confirm\]": lambda session, logger: session.send_line("", logger),
            r"\(y\/n\)": lambda session, logger: session.send_line("y", logger),
            r"[\[\(][Nn]o[\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"[\[\(][Yy]es[\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"[\[\(][Yy]/[Nn][\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
        }
    ),
)

RELOAD = CommandTemplate(
    "reload",
    action_map=OrderedDict(
        {
            r"[\[\(][Yy]es/[Nn]o[\)\]]": lambda session, logger: session.send_line(
                "yes", logger
            ),
            r"\[confirm\]": lambda session, logger: session.send_line("", logger),
            r"\(y\/n\)|continue": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"reload": lambda session, logger: session.send_line("", logger),
            r"[\[\(][Yy]/[Nn][\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
        }
    ),
)

REDUNDANCY_PEER_SHELF = CommandTemplate(
    "redundancy reload shelf",
    action_map=OrderedDict(
        {
            r"[\[\(][Yy]es/[Nn]o[\)\]]": lambda session, logger: session.send_line(
                "yes", logger
            ),
            r"\[confirm\]": lambda session, logger: session.send_line("", logger),
            r"\(y\/n\)|continue": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"[\[\(][Yy]/[Nn][\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
        }
    ),
)

REDUNDANCY_SWITCHOVER = CommandTemplate(
    "redundancy force-switchover",
    action_map=OrderedDict(
        {
            r"[\[\(][Yy]es/[Nn]o[\)\]]": lambda session, logger: session.send_line(
                "yes", logger
            ),
            r"\[confirm\]": lambda session, logger: session.send_line("", logger),
            r"\(y\/n\)|continue": lambda session, logger: session.send_line(
                "y", logger
            ),
            r"[\[\(][Yy]/[Nn][\)\]]": lambda session, logger: session.send_line(
                "y", logger
            ),
        }
    ),
)

NO = CommandTemplate("no {command}")

SHOW_FILE_SYSTEMS = CommandTemplate("show file systems")

SHOW_VERSION_WITH_FILTERS = CommandTemplate(
    "[do{do}] show version [| include {filter}]"
)

CONSOLE_RELOAD = CommandTemplate("reload")
