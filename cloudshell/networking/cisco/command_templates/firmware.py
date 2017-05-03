#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template import CommandTemplate

BOOT_SYSTEM_FILE = CommandTemplate("boot system {firmware_file_name}")

CONFIG_REG = CommandTemplate("config-reg 0x2102")

SHOW_RUNNING = CommandTemplate("show running-config | include boot")

SHOW_VERSION = CommandTemplate("show version")
