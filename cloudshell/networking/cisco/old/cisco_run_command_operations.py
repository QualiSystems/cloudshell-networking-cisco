from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.old.cisco_command_modes import get_session, EnableCommandMode, ConfigCommandMode
from cloudshell.shell.core.context_utils import get_resource_name
from cloudshell.networking.devices.operations.interfaces import RunCommandInterface


class CiscoRunCommandOperations(RunCommandInterface):
    def __init__(self, cli, context, logger, api):
        """Create CiscoIOSHandlerBase

        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        self.cli = cli
        self.logger = logger
        self.resource_name = get_resource_name(context)
        self.session_type = get_session(api=api, context=context)
        self._default_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self._config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)

    def run_custom_command(self, custom_command, mode=None, expected_str=None,
                           expected_map=None, timeout=None, retries=None, is_need_default_prompt=True):
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

        if not mode:
            mode = self._default_mode

        response = ''
        with self.cli.get_session(new_sessions=self.session_type, command_mode=mode,
                                  logger=self.logger) as default_session:
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

    def send_command(self, custom_command, expected_str=None,
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

        return self.run_custom_command(custom_command, expected_str=expected_str, expected_map=expected_map,
                                       timeout=timeout, retries=retries, is_need_default_prompt=is_need_default_prompt)

    def send_config_command(self, custom_command, expected_str=None,
                            expected_map=None,
                            timeout=None, retries=None,
                            is_need_default_prompt=True):
        """Send list of config commands to the session

        :param custom_command: list of commands to send

        :return session returned output
        :rtype: string
        """

        return self.run_custom_command(custom_command=custom_command, expected_str=expected_str,
                                       expected_map=expected_map,
                                       mode=self._config_mode,
                                       timeout=timeout, retries=retries,
                                       is_need_default_prompt=is_need_default_prompt)

    def run_custom_config_command(self, custom_command, expected_str=None,
                                  expected_map=None,
                                  timeout=None, retries=None,
                                  is_need_default_prompt=True):
        """Send list of config commands to the session

        :param custom_command: list of commands to send

        :return session returned output
        :rtype: string
        """

        return self.run_custom_command(custom_command=custom_command, expected_str=expected_str,
                                       expected_map=expected_map,
                                       mode=self._config_mode,
                                       timeout=timeout, retries=retries,
                                       is_need_default_prompt=is_need_default_prompt)
