#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict(
    {
        r"[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]": lambda session: session.send_line(
            "yes"
        ),
        r"[\[\(][Yy]/[Nn][\)\]]": lambda session: session.send_line("y"),
    }
)
ERROR_MAP = OrderedDict(
    {
        r"[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected": Exception(
            "Interface Commands", "Failed to send command"
        )
    }
)

CONFIGURE_INTERFACE = CommandTemplate(
    "interface {port_name} [l2transport{l2transport}]",
    action_map=ACTION_MAP,
    error_map=ERROR_MAP,
)

REMOVE_INTERFACE = CommandTemplate("no interface {port_name}")

NO_SHUTDOWN = CommandTemplate("no shutdown")

SHOW_RUNNING = CommandTemplate("do show running-config [interface {port_name}]")

SHUTDOWN = CommandTemplate("shutdown")

STATE_ACTIVE = CommandTemplate("state active")
