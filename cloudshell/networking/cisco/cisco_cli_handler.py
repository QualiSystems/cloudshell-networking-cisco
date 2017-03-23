import re
import time

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.networking.cisco.cisco_command_modes import EnableCommandMode, DefaultCommandMode, ConfigCommandMode
from cloudshell.networking.cisco.sessions.console_ssh_session import ConsoleSSHSession
from cloudshell.networking.cisco.sessions.console_telnet_session import ConsoleTelnetSession
from cloudshell.networking.cli_handler_impl import CliHandlerImpl
from cloudshell.shell.core.api_utils import decrypt_password_from_attribute
from cloudshell.shell.core.context_utils import get_attribute_by_name


class CiscoCliHandler(CliHandlerImpl):
    def __init__(self, cli, context, logger, api):
        super(CiscoCliHandler, self).__init__(cli, context, logger, api)
        modes = CommandModeHelper.create_command_mode(context)
        self.default_mode = modes[DefaultCommandMode]
        self.enable_mode = modes[EnableCommandMode]
        self.config_mode = modes[ConfigCommandMode]

    @property
    def console_server_address(self):
        """Resource console server IP address

        :return:
        """

        return get_attribute_by_name('Console Server IP Address', self._context)

    @property
    def console_server_port(self):
        """Connection console server port property, to open socket on

        :return:
        """
        return get_attribute_by_name('Console Port', self._context)

    @property
    def console_server_user(self):
        """Connection console username property

        :return:
        """
        return get_attribute_by_name('Console User', self._context)

    @property
    def console_server_password(self):
        """Connection console password property

        :return:
        """
        return get_attribute_by_name('Console Password', self._context)

    def _console_ssh_session(self):
        console_port = int(self.console_server_port)
        return ConsoleSSHSession(self.console_server_address, self.username, self.password, console_port,
                                 self.on_session_start)

    def _console_telnet_session(self):
        console_port = int(self.console_server_port)
        return [ConsoleTelnetSession(self.console_server_address, self.username, self.password, console_port,
                                     self.on_session_start),
                ConsoleTelnetSession(self.console_server_address, self.username, self.password, console_port,
                                     self.on_session_start, start_with_new_line=True)]

    def _console_sessions(self):
        console_address = self.console_server_address
        if not console_address:
            return []
        new_sessions = [self._console_ssh_session()]
        new_sessions.extend(self._console_telnet_session())
        return new_sessions

    def _new_sessions(self):
        if self.cli_type.lower() == SSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        elif self.cli_type.lower() == "console":
            new_sessions = self._console_sessions()
            if not new_sessions:
                raise Exception(self.__class__.__name__,
                                "Failed to create Console sessions, " +
                                "please check Console Server IP Address and Console Port Attributes")
        else:
            new_sessions = [self._ssh_session(), self._telnet_session(),
                            self._console_ssh_session()]
            new_sessions.extend(self._console_sessions())
        return new_sessions

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        self.enter_enable_mode(session=session, logger=logger)
        session.hardware_expect('terminal length 0', EnableCommandMode.PROMPT, logger)
        session.hardware_expect('terminal width 300', EnableCommandMode.PROMPT, logger)
        self._enter_config_mode(session, logger)
        session.hardware_expect('no logging console', ConfigCommandMode.PROMPT, logger)
        session.hardware_expect('exit', EnableCommandMode.PROMPT, logger)

    def _enter_config_mode(self, session, logger):
        max_retries = 5
        error_message = 'Failed to enter config mode, please check logs, for details'
        output = session.hardware_expect(ConfigCommandMode.ENTER_COMMAND,
                                         '{0}|{1}'.format(ConfigCommandMode.PROMPT, EnableCommandMode.PROMPT), logger)

        if not re.search(ConfigCommandMode.PROMPT, output):
            retries = 0
            while not re.search(r"[Cc]onfiguration [Ll]ocked", output, re.IGNORECASE) or retries == max_retries:
                time.sleep(5)
                output = session.hardware_expect(ConfigCommandMode.ENTER_COMMAND,
                                                 '{0}|{1}'.format(ConfigCommandMode.PROMPT, EnableCommandMode.PROMPT),
                                                 logger)
            if not re.search(ConfigCommandMode.PROMPT, output):
                raise Exception('_enter_config_mode', error_message)

    def enter_enable_mode(self, session, logger):
        """
        Enter enable mode

        :param session:
        :param logger:
        :raise Exception:
        """

        result = session.hardware_expect('', '{0}|{1}|{2}'.format(DefaultCommandMode.PROMPT, EnableCommandMode.PROMPT,
                                                                  ConfigCommandMode.PROMPT), logger)
        if not re.search(EnableCommandMode.PROMPT, result):
            if re.search(ConfigCommandMode.PROMPT, result):
                session.hardware_expect('end', EnableCommandMode.PROMPT, logger=logger)
                return

            enable_password = decrypt_password_from_attribute(api=self._api,
                                                              password_attribute_name='Enable Password',
                                                              context=self._context)
            expect_map = {'[Pp]assword': lambda session, logger: session.send_line(enable_password, logger)}
            session.hardware_expect('enable', EnableCommandMode.PROMPT, action_map=expect_map, logger=logger)
            result = session.hardware_expect('', '{0}|{1}'.format(DefaultCommandMode.PROMPT, EnableCommandMode.PROMPT),
                                             logger)
            if not re.search(EnableCommandMode.PROMPT, result):
                raise Exception('enter_enable_mode', 'Enable password is incorrect')
