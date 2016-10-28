from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.driver_helper import get_cli_connection_attributes, get_api, \
    get_snmp_parameters_from_command_context
from cloudshell.shell.core.context_utils import get_resource_name, get_attribute_by_name
from cloudshell.networking.autoload.snmp_handler_helper import SNMPHandlerCreator
from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload
from cloudshell.networking.cisco.cisco_command_modes import EnableCommandMode, get_session_type, ConfigCommandMode
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters


class CiscoAutoloadOperations(object):
    def __init__(self, cli, logger, supported_os, context):
        """

        :param Cli cli:
        :param QualiSnmp snmp_handler:
        """

        self.cli = cli
        self.logger = logger
        self.supported_os = supported_os
        self.context = context

    def discover(self):
        with CiscoSNMPContextManager(logger=self.logger, cli=self.cli, context=self.context) as snmp_handler:
            cisco_autoload = CiscoGenericSNMPAutoload(snmp_handler=snmp_handler, logger=self.logger,
                                                      supported_os=self.supported_os)
            return cisco_autoload.discover()


class CiscoSNMPContextManager(SNMPHandlerCreator):
    DEFAULT_COMMUNITY_NAME = 'quali'

    def __init__(self, cli, logger, context):
        super(CiscoSNMPContextManager, self).__init__(logger=logger, context=context)
        self._cli = cli
        api = get_api(context)
        self._session_type = get_session_type(context)
        self._resource_name = get_resource_name(context)
        self._connection_attributes = get_cli_connection_attributes(api, context)
        self.enable_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self.config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)
        self._enable_snmp = get_attribute_by_name(context=context, attribute_name='Enable SNMP').lower() == 'true'
        self._disable_snmp = get_attribute_by_name(context=context, attribute_name='Disable SNMP').lower() == 'true'
        if not self._snmp_parameters.snmp_community:
            self._snmp_parameters.snmp_community = CiscoSNMPContextManager.DEFAULT_COMMUNITY_NAME
            api.SetAttributeValue(self._resource_name, 'SNMP Read Community',
                                        self._snmp_parameters.snmp_community)

    def enable_snmp(self):
        if not self._enable_snmp and not isinstance(self._connection_attributes, SNMPV2Parameters):
            self._logger.info('Enable SNMP skipped: Enable SNMP attribute set to False or SNMP Version = v3')
            return

        with self._cli.get_session(session_type=self._session_type, command_mode=self.enable_mode,
                                   connection_attrs=self._connection_attributes, logger=self._logger) as session:
            existing_snmp_community = self._snmp_parameters.snmp_community.lower() in session.send_command(
                'show snmp communities').lower()

            if not existing_snmp_community:
                with session.enter_mode(ConfigCommandMode) as config_session:
                    config_session.send_command('snmp-server community {0} ro'.format(
                        self._snmp_parameters.snmp_community))

    def disable_snmp(self):
        if not self._disable_snmp:
            self._logger.info('Disable SNMP skipped: Disable SNMP attribute set to False and/or SNMP Version = v3')
            return

        with self._cli.get_session(session_type=self._session_type, command_mode=self.config_mode,
                                   connection_attrs=self._connection_attributes, logger=self._logger) as session:
            session.send_command('no snmp-server community {0} ro'.format(
                self._snmp_parameters.snmp_community))

            self._logger.info('SNMP Community "{}" was successfully removed'.format(
                self._snmp_parameters.snmp_community))
