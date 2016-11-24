from cloudshell.networking.cisco.cisco_cli_handler import CiscoCliHandler
from cloudshell.networking.devices.autoload.snmp_handler_helper import SNMPHandlerCreator
from cloudshell.networking.devices.driver_helper import get_api
from cloudshell.shell.core.context_utils import get_resource_name, get_attribute_by_name
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters


class CiscoAutoloadOperations(object):
    def __init__(self, cli, logger, supported_os, context):
        """
        Facilitate SNMP autoload,

        :param cli:
        :param logger:
        :param supported_os:
        :param context:
        :param Cli cli:
        :param QualiSnmp snmp_handler:
        """

        self.cli = cli
        self.logger = logger
        self.supported_os = supported_os
        self.context = context
        self._autoload_class = None
        self.resource_name = get_resource_name(context)

    def discover(self):
        """Enable and Disable SNMP communityon the device, Read it's structure and attributes: chassis, modules,
        submodules, ports, port-channels and power supplies

        :return: AutoLoadDetails object
        """
        with CiscoSNMPContextManager(logger=self.logger, cli=self.cli, context=self.context) as snmp_handler:
            cisco_autoload = self._autoload_class(snmp_handler=snmp_handler, logger=self.logger,
                                                  supported_os=self.supported_os, resource_name=self.resource_name)
            return cisco_autoload.discover()


class CiscoSNMPContextManager(SNMPHandlerCreator):
    DEFAULT_COMMUNITY_NAME = 'quali'

    def __init__(self, cli, logger, context, api):
        """
        SNMP Context Manager, handle enabling/disabling SNMP

        :param cli:
        :param logger:
        :param context:
        """
        super(CiscoSNMPContextManager, self).__init__(logger=logger, context=context)
        self._cli_handler = CiscoCliHandler(cli, context, logger, api)
        self._logger = logger
        self._enable_snmp_flow(self._cli_handler, self._logger)
        self._enable_snmp = get_attribute_by_name(context=context, attribute_name='Enable SNMP').lower() == 'true'
        self._disable_snmp = get_attribute_by_name(context=context, attribute_name='Disable SNMP').lower() == 'true'
        if not self._snmp_parameters.snmp_community:
            raise Exception(self.__class__.__name__, 'SNMP Read Community is empty')

    def enable_snmp(self):
        """
        Enable SNMP on the device

        :return:
        """
        if not self._enable_snmp or not isinstance(self._snmp_parameters, SNMPV2Parameters):
            self._logger.info('Enable SNMP skipped: Enable SNMP attribute set to False or SNMP Version = v3')
            return

        with self._cli.get_session(new_sessions=self._session_type, command_mode=self._enable_mode,
                                   logger=self._logger) as session:
            existing_snmp_community = self._snmp_parameters.snmp_community.lower() in session.send_command(
                'show running-config | include snmp-server community').lower().replace('snmp-server community', '')

            if not existing_snmp_community:
                with session.enter_mode(self._config_mode) as config_session:
                    config_session.send_command('snmp-server community {0} ro'.format(
                        self._snmp_parameters.snmp_community))

    def disable_snmp(self):
        """
        Disable SNMP on the device

        :return:
        """
        if not self._disable_snmp or not isinstance(self._snmp_parameters, SNMPV2Parameters):
            self._logger.info('Disable SNMP skipped: Disable SNMP attribute set to False and/or SNMP Version = v3')
            return

        with self._cli.get_session(new_sessions=self._session_type, command_mode=self._config_mode,
                                   logger=self._logger) as session:
            session.send_command('no snmp-server community {0} ro'.format(
                self._snmp_parameters.snmp_community))

            self._logger.info('SNMP Community "{}" was successfully removed'.format(
                self._snmp_parameters.snmp_community))
