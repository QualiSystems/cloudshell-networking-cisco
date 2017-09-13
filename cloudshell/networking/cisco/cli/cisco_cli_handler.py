#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import time

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.devices.cli_handler_impl import CliHandlerImpl
from cloudshell.networking.cisco.cli.cisco_command_modes import EnableCommandMode, DefaultCommandMode, ConfigCommandMode
from cloudshell.networking.cisco.sessions.console_ssh_session import ConsoleSSHSession
from cloudshell.networking.cisco.sessions.console_telnet_session import ConsoleTelnetSession


class CiscoCliHandler(CliHandlerImpl):
    def __init__(self, cli, resource_config, logger, api):
        super(CiscoCliHandler, self).__init__(cli, resource_config, logger, api)
        self.modes = CommandModeHelper.create_command_mode(resource_config, api)
        self._enable_password = None

    @property
    def default_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def enable_mode(self):
        return self.modes[EnableCommandMode]

    @property
    def config_mode(self):
        return self.modes[ConfigCommandMode]

    @property
    def enable_password(self):
        if not self._enable_password:
            password = self.resource_config.enable_password
            self._enable_password = self._api.DecryptPassword(password).Value
        return self._enable_password

    def _console_ssh_session(self):
        console_port = int(self.resource_config.console_port)
        session = ConsoleSSHSession(self.resource_config.console_server_ip_address,
                                    self.username,
                                    self.password,
                                    console_port,
                                    self.on_session_start)
        return session

    def _console_telnet_session(self):
        console_port = int(self.resource_config.console_port)
        return [ConsoleTelnetSession(self.resource_config.console_server_ip_address,
                                     self.username,
                                     self.password,
                                     console_port,
                                     self.on_session_start),
                ConsoleTelnetSession(self.resource_config.console_server_ip_address,
                                     self.username,
                                     self.password,
                                     console_port,
                                     self.on_session_start,
                                     start_with_new_line=True)
                ]

    def _new_sessions(self):
        if self.cli_type.lower() == SSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        elif self.cli_type.lower() == "console":
            new_sessions = list()
            new_sessions.append(self._console_ssh_session())
            new_sessions.extend(self._console_telnet_session())
        else:
            new_sessions = [self._ssh_session(), self._telnet_session(),
                            self._console_ssh_session()]
            new_sessions.extend(self._console_telnet_session())
        return new_sessions

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        self._enter_enable_mode(session=session, logger=logger)
        session.hardware_expect("terminal length 0", EnableCommandMode.PROMPT, logger)
        session.hardware_expect("terminal width 300", EnableCommandMode.PROMPT, logger)
        session.hardware_expect("terminal no exec prompt timestamp", EnableCommandMode.PROMPT, logger)
        self._enter_config_mode(session, logger)
        session.hardware_expect("no logging console", ConfigCommandMode.PROMPT, logger)
        session.hardware_expect("exit", EnableCommandMode.PROMPT, logger)

    def _enter_config_mode(self, session, logger):
        max_retries = 5
        error_message = "Failed to enter config mode, please check logs, for details"
        output = session.hardware_expect(ConfigCommandMode.ENTER_COMMAND,
                                         '{0}|{1}'.format(ConfigCommandMode.PROMPT, EnableCommandMode.PROMPT), logger)

        config_mode_match = re.search(ConfigCommandMode.PROMPT, output)
        retries = 0
        while (not config_mode_match) and retries <= max_retries:
            time.sleep(5)
            output = session.hardware_expect(ConfigCommandMode.ENTER_COMMAND,
                                             '{0}|{1}'.format(ConfigCommandMode.PROMPT, EnableCommandMode.PROMPT),
                                             logger)
            config_mode_match = re.search(ConfigCommandMode.PROMPT, output)
            retries += 1
        if not config_mode_match:
            raise Exception('_enter_config_mode', error_message)

    def _enter_enable_mode(self, session, logger):
        """
        Enter enable mode

        :param session:
        :param logger:
        :raise Exception:
        """
        result = session.hardware_expect("", "{default}|{enable}|{config}".format(default=DefaultCommandMode.PROMPT,
                                                                                  enable=EnableCommandMode.PROMPT,
                                                                                  config=ConfigCommandMode.PROMPT),
                                         logger)

        if re.search(DefaultCommandMode.PROMPT, result):
            expect_map = {'[Pp]assword': lambda session, logger: session.send_line(self.enable_password, logger)}
            session.hardware_expect('enable', EnableCommandMode.PROMPT, action_map=expect_map, logger=logger)
            result = session.hardware_expect('', '{0}|{1}'.format(DefaultCommandMode.PROMPT, EnableCommandMode.PROMPT),
                                             logger)
            if not re.search(EnableCommandMode.PROMPT, result):
                raise Exception('enter_enable_mode', 'Enable password is incorrect')
        elif re.search(ConfigCommandMode.PROMPT, result):
            session.hardware_expect("end", EnableCommandMode.PROMPT, logger=logger)
        else:
            logger.debug("Session already in Enable Mode")
