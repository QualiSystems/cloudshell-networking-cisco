from cloudshell.cli.cli import Cli
from cloudshell.cli.cli_session_type import SSH
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.configuration.cloudshell_cli_binding_keys import CLI_SERVICE
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER, API
import inject

from cloudshell.networking.operations.interfaces.run_command_interface import RunCommandInterface
from cloudshell.shell.core.context_utils import get_resource_name


def _translate_session_type(str_session_type):
    session_types = [TelnetSession, SSHSession]
    for session in session_types:
        if str_session_type.lower() in session.__name__.lower():
            return session


class CiscoRunCommandOperations(RunCommandInterface):
    def __init__(self, resource_name, cli, session_type, connection_attributes):
        """Create CiscoIOSHandlerBase

        :param cli: CliService object
        :param logger: QsLogger object
        :param resource_name: resource name
        :return:
        """

        self.cli = cli
        self.resource_name = resource_name
        self.attrs = connection_attributes
        self.session_type_object = _translate_session_type(session_type)

    def run_custom_config_command(self, custom_command, logger, expected_str=None, expected_map=None, timeout=None,
                                  retries=None, is_need_default_prompt=True):
        """Send list of config commands to the session

        :param custom_command: list of commands to send

        :return session returned output
        :rtype: string
        """

        response = ''
        with self.cli.get_session(self.session_type_object, self.attrs, CommandModeContainer.ENABLE_MODE,
                                  logger) as default_session:
            with default_session.enter_mode(CommandModeContainer.CONFIG_MODE) as config_session:
                if isinstance(custom_command, str):
                    commands = [custom_command]
                elif isinstance(custom_command, tuple):
                    commands = list(custom_command)
                else:
                    commands = custom_command

                for cmd in commands:
                    response += config_session.send_command(cmd)
        return response

    def run_custom_command(self, custom_command, logger, expected_str=None, expected_map=None, timeout=None,
                           retries=None, is_need_default_prompt=True, session=None):
        """Send command using cli service

        :param custom_command: command to send
        :param expected_str: optional, custom expected string, if you expect something different from default prompts
        :param expected_map: optional, custom expected map, if you expect some actions in progress of the command
        :param timeout: optional, custom timeout
        :param retries: optional, custom retry count, if you need more than 5 retries
        :param is_need_default_prompt: default
        :param session:

        :return: session returned output
        :rtype: string
        """

        response = ''
        with self.cli.get_session(self.session_type_object, self.attrs, CommandModeContainer.ENABLE_MODE,
                                  logger) as default_session:
            if isinstance(custom_command, str):
                commands = [custom_command]
            elif isinstance(custom_command, tuple):
                commands = list(custom_command)
            else:
                commands = custom_command

            for cmd in commands:
                response += default_session.send_command(cmd)
        return response

    def send_command(self, custom_command, logger, expected_str=None, expected_map=None, timeout=None, retries=None,
                     is_need_default_prompt=True, session=None):
        """Send command using cli service

        :param custom_command: command to send
        :param expected_str: optional, custom expected string, if you expect something different from default prompts
        :param expected_map: optional, custom expected map, if you expect some actions in progress of the command
        :param timeout: optional, custom timeout
        :param retries: optional, custom retry count, if you need more than 5 retries
        :param is_need_default_prompt: default
        :param session:

        :return: session returned output
        :rtype: string
        """

        return self.run_custom_command(custom_command, expected_str=expected_str, expected_map=expected_map,
                                       timeout=timeout, retries=retries, logger=logger,
                                       is_need_default_prompt=is_need_default_prompt, session=session)

    def send_config_command(self, custom_command, logger, expected_str=None, expected_map=None, timeout=None, retries=None,
                            is_need_default_prompt=True):
        """Send list of config commands to the session

        :param custom_command: list of commands to send

        :return session returned output
        :rtype: string
        """

        return self.run_custom_config_command(custom_command=custom_command, expected_str=expected_str,
                                              expected_map=expected_map, logger=logger,
                                              timeout=timeout, retries=retries,
                                              is_need_default_prompt=is_need_default_prompt)

    def perform_default_actions(self, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        with self.cli.get_session(self.session_type_object, self.attrs, CommandModeContainer.ENABLE_MODE,
                                  logger) as default_session:
            default_session.send_command('terminal length 0')
            default_session.send_command('terminal no exec prompt timestamp')
            with default_session.enter_mode(CommandModeContainer.CONFIG_MODE) as config_session:
                config_session.send_command('no logging console')


class CommandModeContainer(object):
    """
    Defined command modes
    """

    DEFAULT_MODE = CommandMode(r'>\s*$', '', '')
    ENABLE_MODE = CommandMode(r'#\s*$', 'enable', 'exit', parent_mode=DEFAULT_MODE,
                              action_map={'[Pp]assword',
                                          lambda s: s.send_command(CommandModeContainer.ENABLE_PASSWORD)})
    CONFIG_MODE = CommandMode(r'\(config.*\)#\s*$', 'configure terminal', 'exit', parent_mode=ENABLE_MODE)
    ENABLE_PASSWORD = ''
