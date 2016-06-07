import inject

from cloudshell.networking.operations.interfaces.send_command_interface import SendCommandInterface
from cloudshell.shell.core.context_utils import get_resource_name


class CiscoSendCommandOperations(SendCommandInterface):
    def __init__(self, resource_name=None, cli=None, logger=None, api=None):
        """Create CiscoIOSHandlerBase

        :param cli: CliService object
        :param logger: QsLogger object
        :param snmp: QualiSnmp object
        :param api: CloudShell Api object
        :param resource_name: resource name
        :return:
        """

        self.supported_os = []
        self._cli = cli
        self._logger = logger
        self._api = api
        try:
            self.resource_name = resource_name or get_resource_name()
        except Exception:
            raise Exception('CiscoHandlerBase', 'ResourceName is empty or None')

    @property
    def logger(self):
        if self._logger is None:
            try:
                self._logger = inject.instance('logger')
            except:
                raise Exception('Cisco OS', 'Logger is none or empty')
        return self._logger

    @property
    def snmp_handler(self):
        if self._snmp_handler is None:
            try:
                self._snmp_handler = inject.instance('snmp_handler')
            except:
                raise Exception('Cisco OS', 'Snmp handler is none or empty')
        return self._snmp_handler

    @property
    def api(self):
        if self._api is None:
            try:
                self._api = inject.instance('api')
            except:
                raise Exception('Cisco OS', 'Api handler is none or empty')
        return self._api

    @property
    def cli(self):
        if self._cli is None:
            try:
                self._cli = inject.instance('cli_service')
            except:
                raise Exception('Cisco OS', 'Cli Service is none or empty')
        return self._cli

    def send_command(self, command, expected_str=None, expected_map=None, timeout=30, retries=10,
                     is_need_default_prompt=True, session=None):
        """Send command

        :param command: cli command
        :param expected_str: optional, custom expected string, if you expect something different from default prompts
        :param expected_map: optional, custom expected map, if you expect some actions in progress of the command
        :param timeout: optional, custom timeout
        :param retries: optional, custom retry count, if you need more than 5 retries
        :param is_need_default_prompt: default
        :param session:
        :return output from cli
        :rtype: string
        """

        if session:
            response = self.cli.send_command(command=command, expected_str=expected_str, expected_map=expected_map,
                                             timeout=timeout, retries=retries,
                                             is_need_default_prompt=is_need_default_prompt, session=session)
        else:
            response = self.cli.send_command(command=command, expected_str=expected_str, expected_map=expected_map,
                                             timeout=timeout, retries=retries,
                                             is_need_default_prompt=is_need_default_prompt)
        return response

    def send_config_command(self, command, expected_str=None, expected_map=None, timeout=30, retries=10,
                            is_need_default_prompt=True):
        """Send list of config commands

        :param command: list of commands
        :return output from cli
        :rtype: string
        """

        return self.cli.send_config_command(command, expected_str, expected_map, timeout, retries,
                                            is_need_default_prompt)

    def send_config_command_list(self, command_list):
        """Send list of config commands

        :param command_list: list of commands
        :return output from cli
        :rtype: string
        """

        result = self.cli.send_command_list(command_list)
        self.cli.exit_configuration_mode()
        return result

    # def _show_command(self, data):
    #     """Execute command: show plus provided part of command, i.e. 'show version'
    #
    #     :param data:
    #     :return: response from send_command method
    #     :rtype: string
    #     """
    #
    #     return self.send_command('show {0}'.format(data))


