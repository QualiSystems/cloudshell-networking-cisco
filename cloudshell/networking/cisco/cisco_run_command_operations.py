from cloudshell.cli.command_mode import CommandMode
from cloudshell.networking.operations.interfaces.run_command_interface import RunCommandInterface


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


class CiscoRunCommandOperations(RunCommandInterface):
    def __init__(self, resource_name, cli):
        """Create CiscoIOSHandlerBase

        :param cli: CliService object
        :param logger: QsLogger object
        :param resource_name: resource name
        :return:
        """

        self.cli = cli
        self.resource_name = resource_name

    def run_custom_command(self, custom_command, logger, session_type, connection_attributes,
                           mode=CommandModeContainer.ENABLE_MODE, expected_str=None, expected_map=None,
                           timeout=None, retries=None, is_need_default_prompt=True):
        """Send command using send_command_operations service

        :param custom_command: command to send
        :param expected_str: optional, custom expected string, if you expect something different from default prompts
        :param expected_map: optional, custom expected map, if you expect some actions in progress of the command
        :param timeout: optional, custom timeout
        :param retries: optional, custom retry count, if you need more than 5 retries
        :param is_need_default_prompt: default

        :return: session returned output
        :rtype: string
        """

        response = ''
        with self.cli.get_session(session_type, connection_attributes, CommandModeContainer.ENABLE_MODE,
                                  logger) as default_session:
            if isinstance(custom_command, str):
                commands = [custom_command]
            elif isinstance(custom_command, tuple):
                commands = list(custom_command)
            else:
                commands = custom_command

            for cmd in commands:
                response += default_session.send_command(command=cmd,
                                                         expected_str=expected_str,
                                                         expected_map=expected_map,
                                                         timeout=timeout,
                                                         retries=retries,
                                                         is_need_default_prompt=is_need_default_prompt)
        return response

    def send_command(self, custom_command, logger, session_type, connection_attributes, expected_str=None,
                     expected_map=None, timeout=None, retries=None, is_need_default_prompt=True):
        """Send command using send_command_operations service

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

        return self.run_custom_command(custom_command, session_type=session_type, expected_str=expected_str,
                                       expected_map=expected_map, timeout=timeout, retries=retries, logger=logger,
                                       connection_attributes=connection_attributes,
                                       is_need_default_prompt=is_need_default_prompt)

    def send_config_command(self, custom_command, logger, session_type, connection_attributes, expected_str=None,
                            expected_map=None,
                            timeout=None, retries=None,
                            is_need_default_prompt=True):
        """Send list of config commands to the session

        :param custom_command: list of commands to send

        :return session returned output
        :rtype: string
        """

        return self.run_custom_command(custom_command=custom_command, expected_str=expected_str,
                                       expected_map=expected_map, logger=logger,
                                       mode=CommandModeContainer.CONFIG_MODE,
                                       timeout=timeout, retries=retries, session_type=session_type,
                                       connection_attributes=connection_attributes,
                                       is_need_default_prompt=is_need_default_prompt)

    def run_custom_config_command(self, custom_command, logger, session_type, connection_attributes, expected_str=None,
                                  expected_map=None,
                                  timeout=None, retries=None,
                                  is_need_default_prompt=True):
        """Send list of config commands to the session

        :param custom_command: list of commands to send

        :return session returned output
        :rtype: string
        """

        return self.run_custom_command(custom_command=custom_command, expected_str=expected_str,
                                       expected_map=expected_map, logger=logger,
                                       mode=CommandModeContainer.CONFIG_MODE,
                                       timeout=timeout, retries=retries, session_type=session_type,
                                       connection_attributes=connection_attributes,
                                       is_need_default_prompt=is_need_default_prompt)

    def perform_default_actions(self, logger, session_type, connection_attributes):
        """Send default commands to configure/clear session outputs
        :return:
        """

        with self.cli.get_session(session_type, connection_attributes, CommandModeContainer.ENABLE_MODE,
                                  logger) as default_session:
            default_session.send_command('terminal length 0')
            default_session.send_command('terminal no exec prompt timestamp')
            with default_session.enter_mode(CommandModeContainer.CONFIG_MODE) as config_session:
                config_session.send_command('no logging console')
