#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.cisco.command_templates import enable_disable_snmp


class EnableDisableSnmpActions(object):
    READ_ONLY = "ro"
    READ_WRITE = "rw"

    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def get_current_snmp_communities(self, cli_service=None, action_map=None, error_map=None):
        """Retrieve current snmp communities

        :param cli_service:
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return:
        """

        if not cli_service:
            cli_service = self._cli_service
        return CommandTemplateExecutor(cli_service=cli_service,
                                       command_template=enable_disable_snmp.SHOW_SNMP_COMMUNITY,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()

    def enable_snmp(self, snmp_community, is_read_only_community=True, action_map=None, error_map=None):
        """Enable SNMP on the device

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        read_only = self.READ_WRITE
        if is_read_only_community:
            read_only = self.READ_ONLY
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=enable_disable_snmp.ENABLE_SNMP,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_community=snmp_community,
                                                                            read_only=read_only)

    def disable_snmp(self, snmp_community, action_map=None, error_map=None):
        """Disable SNMP on the device

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=enable_disable_snmp.DISABLE_SNMP,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_community=snmp_community)
