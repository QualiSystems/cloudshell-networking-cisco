from collections import OrderedDict
import time

import inject
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_command_modes import EnableCommandMode, ConfigCommandMode
from cloudshell.networking.operations.state_operations import StateOperations


class CiscoStateOperations(StateOperations):
    def __init__(self, cli, logger, api, context):
        super(CiscoStateOperations, self).__init__(cli, logger, api, context)
        self._cli = cli
        self._logger = logger
        self._api = api
        self._default_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self._config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)

    def shutdown(self):
        pass

    @staticmethod
    def reload(session, logger, sleep_timeout=60, retries=15):
        """Reload device

        :param sleep_timeout: period of time, to wait for device to get back online
        :param retries: amount of retires to get response from device after it will be rebooted
        """

        expected_map = OrderedDict({'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session: session.send_line('yes'),
                                    '\(y/n\)|continue': lambda session: session.send_line('y'),
                                    '[\[\(][Yy]/[Nn][\)\]]': lambda session: session.send_line('y')
                                    # 'reload': lambda session: session.send_line('')
                                    })
        try:
            logger.info('Send \'reload\' to device...')
            session.send_command(command='reload', expected_map=expected_map, timeout=3)

        except Exception:
            session_type = session.get_session_type()

            if not session_type == 'CONSOLE':
                logger.info('Session type is \'{}\', closing session...'.format(session_type))
                session.destroy_threaded_session()
                connection_manager = inject.instance(CONNECTION_MANAGER)
                connection_manager.decrement_sessions_count()

        logger.info('Wait 20 seconds for device to reload...')
        time.sleep(20)
        # output = self.send_command_operations.send_command(command='', expected_str='.*', expected_map={})

        retry = 0
        is_reloaded = False
        while retry < retries:
            retry += 1

            time.sleep(sleep_timeout)
            try:
                logger.debug('Trying to send command to device ... (retry {} of {}'.format(retry, retries))
                output = session.send_command(command='', expected_str='(?<![#\n])[#>] *$', expected_map={}, timeout=5,
                                              is_need_default_prompt=False)
                if len(output) == 0:
                    continue

                is_reloaded = True
                break
            except Exception as e:
                logger.error('CiscoHandlerBase', e.message)
                logger.debug('Wait {} seconds and retry ...'.format(sleep_timeout / 2))
                time.sleep(sleep_timeout / 2)
                pass

        return is_reloaded
