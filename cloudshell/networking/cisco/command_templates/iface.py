#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template import CommandTemplate


CONFIGURE_INTERFACE = CommandTemplate("interface {port_name}")

NO = CommandTemplate("no {command}")

NO_SHUTDOWN = CommandTemplate("no shutdown")

SHOW_RUNNING = CommandTemplate("do show running-config [interface {port_name}]")

SHUTDOWN = CommandTemplate("shutdown")

STATE_ACTIVE = CommandTemplate("state active")
