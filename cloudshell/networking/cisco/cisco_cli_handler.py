import re

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_command_modes import EnableCommandMode, DefaultCommandMode, ConfigCommandMode
from cloudshell.networking.cli_handler_impl import CliHandlerImpl
from cloudshell.shell.core.api_utils import decrypt_password_from_attribute


class CiscoCliHandler(CliHandlerImpl):
    def __init__(self, cli, context, logger, api):
        super(CiscoCliHandler, self).__init__(cli, context, logger, api)
        modes = CommandModeHelper.create_command_mode(context)
        self.default_mode = modes[DefaultCommandMode]
        self.enable_mode = modes[EnableCommandMode]
        self.config_mode = modes[ConfigCommandMode]

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs
        :return:
        """

        self.enter_enable_mode(session=session, logger=logger)
        session.hardware_expect('terminal length 0', EnableCommandMode.PROMPT, logger)
        session.hardware_expect('terminal width 300', EnableCommandMode.PROMPT, logger)
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
        result = session.hardware_expect('', '{0}|{1}'.format(self.default_mode.PROMPT, self.enable_mode.PROMPT),
                                         logger)
        if not re.search(self.enable_mode.PROMPT, result):
            enable_password = decrypt_password_from_attribute(api=self._api,
                                                              password_attribute_name='Enable Password',
                                                              context=self._context)
            expect_map = {'[Pp]assword': lambda session, logger: session.send_line(enable_password, logger)}
            session.hardware_expect('enable', EnableCommandMode.PROMPT, action_map=expect_map, logger=logger)
            result = session.hardware_expect('', '{0}|{1}'.format(self.default_mode.PROMPT, EnableCommandMode.PROMPT),
                                             logger)
            if not re.search(EnableCommandMode.PROMPT, result):
                raise Exception('enter_enable_mode', 'Enable password is incorrect')
