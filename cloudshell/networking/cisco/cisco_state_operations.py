from collections import OrderedDict
import time

import inject
from cloudshell.configuration.cloudshell_cli_binding_keys import CLI_SERVICE, CONNECTION_MANAGER
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER, API
from cloudshell.networking.operations.state_operations import StateOperations
from cloudshell.shell.core.context_utils import get_resource_name


class CiscoStateOperations(StateOperations):
    def __init__(self, cli=None, logger=None, api=None, resource_name=None):
        StateOperations.__init__(self)
        self._cli = cli
        self._logger = logger
        self._api = api
        self._resource_name = resource_name

    @property
    def logger(self):
        if self._logger is None:
            try:
                self._logger = inject.instance(LOGGER)
            except:
                raise Exception(self.__class__.__name__, 'Failed to get logger.')
        return self._logger

    @property
    def cli(self):
        if self._cli is None:
            try:
                self._cli = inject.instance(CLI_SERVICE)
            except:
                raise Exception(self.__class__.__name__, 'Failed to get cli_service.')
        return self._cli

    @property
    def api(self):
        if self._api is None:
            try:
                self._api = inject.instance(API)
            except:
                raise Exception(self.__class__.__name__, 'Failed to get api handler.')
        return self._api

    @property
    def resource_name(self):
        if self._resource_name is None:
            try:
                self._resource_name = get_resource_name()
            except:
                raise Exception(self.__class__.__name__, 'Failed to get resource name.')
        return self._resource_name

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
            self.logger.info('Send \'reload\' to device...')
            self.cli.send_command(command='reload', expected_map=expected_map, timeout=3)

        except Exception:
            session_type = self.cli.get_session_type()

            if not session_type == 'CONSOLE':
                self.logger.info('Session type is \'{}\', closing session...'.format(session_type))
                self.cli.destroy_threaded_session()
                connection_manager = inject.instance(CONNECTION_MANAGER)
                connection_manager.decrement_sessions_count()

        self.logger.info('Wait 20 seconds for device to reload...')
        time.sleep(20)
        # output = self.send_command_operations.send_command(command='', expected_str='.*', expected_map={})

        retry = 0
        is_reloaded = False
        while retry < retries:
            retry += 1

            time.sleep(sleep_timeout)
            try:
                self.logger.debug('Trying to send command to device ... (retry {} of {}'.format(retry, retries))
                output = self.cli.send_command(command='', expected_str='(?<![#\n])[#>] *$', expected_map={}, timeout=5,
                                               is_need_default_prompt=False)
                if len(output) == 0:
                    continue

                is_reloaded = True
                break
            except Exception as e:
                self.logger.error('CiscoHandlerBase', e.message)
                self.logger.debug('Wait {} seconds and retry ...'.format(sleep_timeout / 2))
                time.sleep(sleep_timeout / 2)
                pass

        return is_reloaded
