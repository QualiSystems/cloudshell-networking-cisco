from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload
from cloudshell.networking.devices.flows.configuration_flows import BaseFlow
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters


class CiscoAutoloadFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoAutoloadFlow, self).__init__(cli_handler, logger)
        self._command_actions = CiscoAutoloadFlow()
        self._snmp_command_actions = CiscoGenericSNMPAutoload()

    def execute_flow(self, enable_snmp, disable_snmp, snmp_parameters):
        result = None
        with self._cli_handler.get_session(self._cli_handler.config_mode) as session:
            try:
                if enable_snmp and isinstance(snmp_parameters, SNMPV2Parameters):
                    self._command_actions.enable_snmp(session)
                    existing_snmp_community = self._snmp_parameters.snmp_community.lower() in session.send_command(
                        'show running-config | include snmp-server community').lower().replace('snmp-server community', '')

                if not existing_snmp_community:
                    with session.enter_mode(self._config_mode) as config_session:
                        config_session.send_command('snmp-server community {0} ro'.format(
                            self._snmp_parameters.snmp_community))
                else:
                    self._logger.info('Enable SNMP skipped: Enable SNMP attribute set to False or SNMP Version = v3')
                result = self.run_autoload(snmp_parameters)
            finally:
                if disable_snmp:
                    self._command_actions.disable_snmp(session)
        return result

    def run_autoload(self, snmp_parameters):
        result = None
        snmp_handler = QualiSnmp(snmp_parameters, logger=self._logger)
        return result
