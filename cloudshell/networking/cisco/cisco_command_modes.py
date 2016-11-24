import re
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.shell.core.api_utils import decrypt_password_from_attribute
from cloudshell.shell.core.context_utils import get_attribute_by_name, get_resource_address


class DefaultCommandMode(CommandMode):
    PROMPT = r'>\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, context):
        """
        Initialize Default command mode, only for cases when session started not in enable mode

        :param context:
        """
        self._context = context
        CommandMode.__init__(self, DefaultCommandMode.PROMPT, DefaultCommandMode.ENTER_COMMAND,
                             DefaultCommandMode.EXIT_COMMAND)


class EnableCommandMode(CommandMode):
    PROMPT = r'(?:(?!\)).)#\s*$'
    ENTER_COMMAND = 'enable'
    EXIT_COMMAND = ''

    def __init__(self, context):
        """
        Initialize Enable command mode - default command mode for Cisco Shells

        :param context:
        """
        self._context = context

        CommandMode.__init__(self, EnableCommandMode.PROMPT, EnableCommandMode.ENTER_COMMAND,
                             EnableCommandMode.EXIT_COMMAND)


class ConfigCommandMode(CommandMode):
    PROMPT = r'\(config.*\)#\s*$'
    ENTER_COMMAND = 'configure terminal'
    EXIT_COMMAND = 'exit'

    def __init__(self, context):
        """
        Initialize Config command mode

        :param context:
        """
        exit_action_map = {
            self.PROMPT: lambda session, logger: session.send_line('exit', logger)}
        CommandMode.__init__(self, ConfigCommandMode.PROMPT,
                             ConfigCommandMode.ENTER_COMMAND,
                             ConfigCommandMode.EXIT_COMMAND,
                             exit_action_map=exit_action_map)


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        EnableCommandMode: {
            ConfigCommandMode: {}
        }
    }
}