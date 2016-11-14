from collections import OrderedDict
import time

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_command_modes import EnableCommandMode, ConfigCommandMode, get_session
from cloudshell.networking.operations.state_operations import StateOperations


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

    def reload(self, sleep_timeout=500):
        """Reload device

        :param sleep_timeout: period of time, to wait for device to get back online
        """

        expected_map = OrderedDict(
            {'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session, logger: session.send_line('yes', logger),
             '\(y/n\)|continue': lambda session, logger: session.send_line('y', logger),
             '[\[\(][Yy]/[Nn][\)\]]': lambda session, logger: session.send_line('y', logger)
             # 'reload': lambda session: session.send_line('')
             })
        try:
            self._logger.info('Send \'reload\' to device...')
            with self._cli.get_session(new_sessions=self._session_type, command_mode=self._default_mode,
                                       logger=self._logger) as session:
                session.send_command(command='reload', expected_map=expected_map, timeout=3)

        except Exception:
            pass

        self._logger.info('Wait 20 seconds for device to reload...')
        time.sleep(20)

        return self._wait_device_up(sleep_timeout)
