from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.core.logger import qs_logger
from cloudshell.cli.cli import CLI
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_command_modes import get_session, EnableCommandMode, ConfigCommandMode
from cloudshell.networking.cisco.cisco_configuration_operations import CiscoConfigurationOperations
from cloudshell.networking.cisco.cisco_state_operations import CiscoStateOperations
from cloudshell.networking.cisco.firmware_data.cisco_firmware_data import CiscoFirmwareData
from cloudshell.networking.networking_utils import UrlParser
from cloudshell.networking.operations.interfaces.firmware_operations_interface import FirmwareOperationsInterface
from cloudshell.shell.core.context import ResourceCommandContext


def _remove_old_boot_system_config(session):
    """Clear boot system parameters in current configuration
    """

    data = session.send_command('do show run | include boot')
    start_marker_str = 'boot-start-marker'
    index_begin = data.find(start_marker_str)
    index_end = data.find('boot-end-marker')

    if index_begin == -1 or index_end == -1:
        return

    data = data[index_begin + len(start_marker_str):index_end]
    data_list = data.split('\n')

    for line in data_list:
        if line.find('boot system') != -1:
            session.send_command(command='no ' + line, expected_str='(config)#')


class CiscoFirmwareOperations(FirmwareOperationsInterface):
    def __init__(self, cli, logger, api, context):
        """Handle firmware upgrade process

        :param CLI cli: Cli object
        :param qs_logger logger: logger
        :param CloudShellAPISession api: cloudshell api object
        :param ResourceCommandContext context: command context
        """

        self._cli = cli
        self._logger = logger
        self._api = api
        self._context = context
        self._enable_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self._config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)
        self._session_type = get_session(context=context, api=api)

    def load_firmware(self, path, vrf_management_name=None):
        """Update firmware version on device by loading provided image, performs following steps:

            1. Copy bin file from remote tftp server.
            2. Clear in run config boot system section.
            3. Set downloaded bin file as boot file and then reboot device.
            4. Check if firmware was successfully installed.

        :param path: full path to firmware file on ftp/tftp location
        :param vrf_management_name: VRF Name
        :return: status / exception
        """

        url = UrlParser.parse_url(path)
        required_keys = [UrlParser.FILENAME, UrlParser.HOSTNAME, UrlParser.SCHEME]

        if not url or not all(key in url for key in required_keys):
            raise Exception('CiscoFirmwareOperations', 'Path is wrong or empty')

        file_name = url[UrlParser.FILENAME]
        firmware_obj = CiscoFirmwareData(path)

        if firmware_obj.get_name() is None:
            raise Exception('CiscoFirmwareOperations', "Invalid firmware name!\n \
                                Firmware file must have: title, extension.\n \
                                Example: isr4400-universalk9.03.10.00.S.153-3.S-ext.SPA.bin\n\n \
                                Current path: {}".format(file_name))
        firmware_full_name = firmware_obj.get_name() + '.' + firmware_obj.get_extension()
        with self._cli.get_session(new_sessions=self._session_type, command_mode=self._enable_mode,
                                   logger=self._logger) as session:
            is_downloaded = CiscoConfigurationOperations.copy(current_session=session, logger=self._logger,
                                                              source_file=path,
                                                              destination_file='bootflash:/{}'.format(file_name),
                                                              timeout=600,
                                                              retries=2)

            if not is_downloaded[0]:
                raise Exception('CiscoFirmwareOperations',
                                "Failed to download firmware from {}!\n {}".format(path, is_downloaded[1]))

            with session.enter_mode(self._config_mode) as config_session:
                config_session.send_command(command='configure terminal', expected_str='(config)#')
                _remove_old_boot_system_config(config_session)

                is_boot_firmware = False

                retries = 5
                while (not is_boot_firmware) and (retries > 0):
                    config_session.send_command(command='boot system flash bootflash:' + firmware_full_name,
                                                expected_str='(config)#')
                    config_session.send_command(command='config-reg 0x2102', expected_str='(config)#')

                    output = config_session.send_command('do show run | include boot')

                    retries -= 1
                    is_boot_firmware = output.find(firmware_full_name) != -1

                if not is_boot_firmware:
                    raise Exception('CiscoFirmwareOperations',
                                    "Can't add firmware '" + firmware_full_name + "' for boot!")

            session.send_command(command='copy run start',
                                 expected_map={'\?': lambda session: session.send_line('')})

        self.reload()
        with self._cli.get_session(new_sessions=self._session_type, command_mode=self._enable_mode,
                                   logger=self._logger) as session:
            output_version = session.send_command(command='show version | include image file')

        is_firmware_installed = output_version.find(firmware_full_name)
        if is_firmware_installed != -1:
            return 'Update firmware completed successfully!'
        else:
            raise Exception('CiscoFirmwareOperations', 'Update firmware failed!')

    def reload(self, sleep_timeout=60, retries=15):
        """Reload device

        :param sleep_timeout: timeout between attempts to establish connection to the device
        :param retries: amount of retires will be taken
        :return: True or False
        """

        state_operations = CiscoStateOperations(cli=self._cli, api=self._api,
                                                context=self._context, logger=self._logger)
        return state_operations.reload(sleep_timeout=sleep_timeout, retries=retries)
