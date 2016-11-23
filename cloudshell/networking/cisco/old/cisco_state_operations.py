from collections import OrderedDict
import time

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.old.cisco_command_modes import EnableCommandMode, ConfigCommandMode, get_session
from cloudshell.networking.devices.operations import StateOperations


class CiscoStateOperations(StateOperations):
    def __init__(self, cli, logger, api, context):
        """

        :param cli:
        :param logger:
        :param api:
        :param context:
        """

        super(CiscoStateOperations, self).__init__(cli, logger, api, context)
        self._cli = cli
        self._logger = logger
        self._api = api
        self._session_type = get_session(self._context, self._api)
        self._default_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self._config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)

    def shutdown(self):
        pass

    @staticmethod
    def reboot(cli_session, logger, sleep_timeout=500):
        """Reload device

        :param cli_session:
        :param logger:
        :param sleep_timeout: period of time, to wait for device to get back online
        """

        expected_map = OrderedDict(
            {'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session, logger: session.send_line('yes', logger),
             '\(y/n\)|continue': lambda session, logger: session.send_line('y', logger),
             '[\[\(][Yy]/[Nn][\)\]]': lambda session, logger: session.send_line('y', logger)
             })
        try:
            logger.info('Send \'reload\' to device...')
            cli_session.send_command(command='reload', action_map=expected_map, timeout=3)
        except Exception:
            pass

        logger.info('Wait 20 seconds for device to reload...')
        time.sleep(20)

        cli_session.reconnect(sleep_timeout)

    def reload(self, cli_session, sleep_timeout=500):
        """Reload device

        :param sleep_timeout: period of time, to wait for device to get back online
        """

        return CiscoStateOperations.reboot(cli_session=cli_session, logger=self._logger, sleep_timeout=sleep_timeout)
