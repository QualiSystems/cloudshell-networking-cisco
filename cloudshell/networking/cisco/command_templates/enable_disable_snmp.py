#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict(
    {
        (
            r"[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected"
        ): "Failed to initialize snmp. Please check Logs for details."
    }
)

SHOW_SNMP_COMMUNITY = CommandTemplate(
    "do show running-config | include snmp-server community", error_map=ERROR_MAP
)
SHOW_SNMP_CONFIG = CommandTemplate(
    "do show running-config | include snmp-server", error_map=ERROR_MAP
)
SHOW_SNMP_USER = CommandTemplate("do show snmp user", error_map=ERROR_MAP)
ENABLE_SNMP = CommandTemplate(
    "snmp-server community {snmp_community} {read_only}", error_map=ERROR_MAP
)
ENABLE_SNMP_VIEW = CommandTemplate(
    "snmp-server view {snmp_view} 1.3.6 included", error_map=ERROR_MAP
)
ENABLE_SNMP_GROUP = CommandTemplate(
    "snmp-server group {snmp_group} v3 priv read {snmp_view} write {snmp_view}",
    error_map=ERROR_MAP,
)
ENABLE_SNMP_V3_WITH_GROUP = CommandTemplate(
    "snmp-server user {snmp_user} {snmp_group} v3 auth {auth_protocol} "
    "{snmp_password} priv {priv_protocol} {snmp_priv_key}",
    error_map=ERROR_MAP,
)
ENABLE_SNMP_USER = CommandTemplate(
    "snmp-server user {snmp_user} auth {auth_protocol} "
    "{snmp_password} priv[ {priv_protocol}] {snmp_priv_key}",
    error_map=ERROR_MAP,
)
DISABLE_SNMP_COMMUNITY = CommandTemplate(
    "no snmp-server community {snmp_community}", error_map=ERROR_MAP
)
DISABLE_SNMP_VIEW = CommandTemplate(
    "no snmp-server view {snmp_view}", error_map=ERROR_MAP
)
DISABLE_SNMP_GROUP = CommandTemplate(
    "no snmp-server group {snmp_group} v3 priv", error_map=ERROR_MAP
)
DISABLE_SNMP_USER_WITH_GROUP = CommandTemplate(
    "no snmp-server user {snmp_user}[ {snmp_group} v3]", error_map=ERROR_MAP
)
DISABLE_SNMP_USER = CommandTemplate(
    "no snmp-server user {snmp_user}", error_map=ERROR_MAP
)
