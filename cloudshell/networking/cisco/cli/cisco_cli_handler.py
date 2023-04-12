#!/usr/bin/python
from __future__ import annotations

from typing import ClassVar

from attrs import define, field

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.factory.session_factory import (
    ConsoleSessionFactory,
    GenericSessionFactory,
    SessionFactory,
)
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.service.cli_service_impl import CliServiceImpl
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.service.session_pool_manager import SessionPoolManager
from cloudshell.cli.session.console_ssh import ConsoleSSHSession
from cloudshell.cli.session.console_telnet import ConsoleTelnetSession
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.types import T_COMMAND_MODE_RELATIONS

from cloudshell.networking.cisco.cisco_constants import DEFAULT_SESSION_POOL_TIMEOUT
from cloudshell.networking.cisco.cli.cisco_command_modes import (
    ConfigCommandMode,
    DefaultCommandMode,
    EnableCommandMode,
)


class CiscoCli:
    def __init__(self, resource_config, pool_timeout=DEFAULT_SESSION_POOL_TIMEOUT):
        session_pool_size = int(resource_config.sessions_concurrency_limit)
        session_pool = SessionPoolManager(
            max_pool_size=session_pool_size, pool_timeout=pool_timeout
        )
        self.cli = CLI(session_pool=session_pool)

    def get_cli_handler(self, resource_config, logger):
        return CiscoCliHandler.from_config(resource_config, logger, self.cli)


@define
class CiscoCliHandler(AbstractModeConfigurator):
    REGISTERED_SESSIONS: ClassVar[tuple[SessionFactory]] = (
        GenericSessionFactory(SSHSession),
        GenericSessionFactory(TelnetSession),
        ConsoleSessionFactory(ConsoleSSHSession),
        ConsoleSessionFactory(
            ConsoleTelnetSession, session_kwargs={"start_with_new_line": False}
        ),
        ConsoleSessionFactory(
            ConsoleTelnetSession, session_kwargs={"start_with_new_line": True}
        ),
    )
    modes: T_COMMAND_MODE_RELATIONS = field(init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.modes = CommandModeHelper.create_command_mode(self._auth.enable_password)

    @property
    def default_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def enable_mode(self):
        return self.modes[EnableCommandMode]

    @property
    def config_mode(self):
        return self.modes[ConfigCommandMode]

    def _on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs.

        :return:
        """
        cli_service = CliServiceImpl(
            session=session, requested_command_mode=self.enable_mode, logger=logger
        )
        cli_service.send_command("terminal length 0", EnableCommandMode.PROMPT)
        cli_service.send_command("terminal width 300", EnableCommandMode.PROMPT)
        cli_service.send_command(
            "terminal no exec prompt timestamp", EnableCommandMode.PROMPT
        )
        with cli_service.enter_mode(self.config_mode) as config_session:
            config_session.send_command("no logging console", ConfigCommandMode.PROMPT)
