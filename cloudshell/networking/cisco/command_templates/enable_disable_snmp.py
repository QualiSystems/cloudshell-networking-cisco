#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template import CommandTemplate

SHOW_SNMP_COMMUNITY = CommandTemplate("do show running-config | include snmp-server community")
ENABLE_SNMP = CommandTemplate("snmp-server community {snmp_community} {read_only}")
DISABLE_SNMP = CommandTemplate("no snmp-server community {snmp_community}")
