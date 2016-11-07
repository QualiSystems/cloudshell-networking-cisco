from collections import OrderedDict
import time

import inject
from cloudshell.cli.cli import CLI
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
        self._session_obj = get_session(context=context, api=api)
        self._default_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self._config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)

    def shutdown(self):
        pass

    def reload(self, sleep_timeout=60, retries=15):
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
            self._logger.info('Send \'reload\' to device...')
            with self._cli.get_session(new_sessions=self._session_obj, command_mode=self._default_mode,
                                       logger=self._logger) as session:
                session.send_command(command='reload', expected_map=expected_map, timeout=3)

        except Exception:
            pass

        self._logger.info('Wait 20 seconds for device to reload...')
        time.sleep(20)
        # output = self.send_command_operations.send_command(command='', expected_str='.*', expected_map={})

        retry = 0
        is_reloaded = False
        while retry < retries:
            retry += 1

            time.sleep(sleep_timeout)
            try:
                self._logger.debug('Trying to send command to device ... (retry {} of {}'.format(retry, retries))
                with self._cli.get_session(new_sessions=self._session_obj, command_mode=self._default_mode,
                                           logger=self._logger) as session:
                    output = session.send_command(command='', expected_str='(?<![#\n])[#>] *$', expected_map={}, timeout=5,
                                                  is_need_default_prompt=False)
                    if len(output) == 0:
                        continue

                    is_reloaded = True
                    break
            except Exception as e:
                self._logger.error('CiscoStateOperations', e.message)
                self._logger.debug('Wait {} seconds and retry ...'.format(sleep_timeout / 2))
                time.sleep(sleep_timeout / 2)
                pass

        return is_reloaded
