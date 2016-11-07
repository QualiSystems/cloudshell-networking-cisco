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
    # PROMPT = r'#\s*$'
    ENTER_COMMAND = 'enable'
    EXIT_COMMAND = 'disable'

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


def get_session(context, api):
    """
    Creates session object from context.

    :param context:
    :param api:
    :return:
    """
    str_session = get_attribute_by_name(context=context, attribute_name='CLI Connection Type')
    host = get_resource_address(context)
    username = get_attribute_by_name(context=context, attribute_name='User')
    port = get_attribute_by_name(context=context, attribute_name='CLI TCP Port')
    password = decrypt_password_from_attribute(api=api, password_attribute_name='Password', context=context)
    default_actions = DefaultActions(context, api).send_actions
    telnet_session = TelnetSession(host=host, port=port, username=username, password=password,
                                   on_session_start=default_actions)
    ssh_session = SSHSession(host=host, port=port, username=username, password=password,
                             on_session_start=default_actions)
    session_types = {'auto': [telnet_session, ssh_session],
                     'ssh': ssh_session,
                     'telnet': telnet_session}
    return session_types.get(str_session.lower(), None)


class DefaultActions(object):
    def __init__(self, context, api):
        """

        :param context:
        :param api:
        """
        self._context = context
        self._api = api

    def send_actions(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        self.enter_enable_mode(session=session, logger=logger)
        session.hardware_expect('terminal length 0', EnableCommandMode.PROMPT, logger)
        session.hardware_expect('terminal width 200', EnableCommandMode.PROMPT, logger)
        session.hardware_expect('terminal no exec prompt timestamp', EnableCommandMode.PROMPT, logger)
        session.hardware_expect(ConfigCommandMode.ENTER_COMMAND, ConfigCommandMode.PROMPT, logger)
        session.hardware_expect('no logging console', ConfigCommandMode.PROMPT, logger)
        session.hardware_expect('exit', EnableCommandMode.PROMPT, logger)

    def enter_enable_mode(self, session, logger):
        """
        Enter enable mode

        :param session:
        :param logger:
        :raise Exception:
        """
        result = session.hardware_expect('', '{0}|{1}'.format(DefaultCommandMode.PROMPT, EnableCommandMode.PROMPT), logger)
        if not re.search(EnableCommandMode.PROMPT, result):
            enable_password = decrypt_password_from_attribute(api=self._api,
                                                              password_attribute_name='Enable Password',
                                                              context=self._context)
            expect_map = {'[Pp]assword': lambda session, logger: session.send_line(enable_password, logger)}
            session.hardware_expect('enable', EnableCommandMode.PROMPT, action_map=expect_map, logger=logger)
            result = session.hardware_expect('', '{0}|{1}'.format(DefaultCommandMode.PROMPT, EnableCommandMode.PROMPT),
                                             logger)
            if not re.search(EnableCommandMode.PROMPT, result):
                raise Exception('enter_enable_mode', 'Enable password is incorrect')


