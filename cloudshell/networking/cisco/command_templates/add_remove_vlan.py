#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict({"[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]": lambda session: session.send_line("yes"),
                          "[\[\(][Yy]/[Nn][\)\]]": lambda session: session.send_line("y")})
ERROR_MAP = OrderedDict({"[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected":
                         Exception("SWITCHPORT_MODE", "Failed to switch port mode"),
                         })

CONFIGURE_VLAN = CommandTemplate("vlan {vlan_id}",
                                 error_map=OrderedDict({"%.*\.": Exception("CONFIGURE_VLAN", "Error")}))

SWITCHPORT_ALLOW_VLAN = CommandTemplate(
    "switchport [trunk allowed{port_mode_trunk}] [access{port_mode_access}] vlan {vlan_range}",
    action_map=ACTION_MAP,
    error_map=ERROR_MAP)

SWITCHPORT_MODE = CommandTemplate("switchport [mode {port_mode}]",
                                  action_map=ACTION_MAP,
                                  error_map=ERROR_MAP)
