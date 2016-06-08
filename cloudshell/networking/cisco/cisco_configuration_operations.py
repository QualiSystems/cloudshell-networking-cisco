from collections import OrderedDict
import traceback
import inject
import re
import time

from cloudshell.networking.networking_utils import validateIP
from cloudshell.networking.cisco.firmware_data.cisco_firmware_data import CiscoFirmwareData
from cloudshell.networking.operations.interfaces.configuration_operations_interface import \
    ConfigurationOperationsInterface
from cloudshell.networking.operations.interfaces.firmware_operations_interface import FirmwareOperationsInterface
from cloudshell.shell.core.context_utils import get_resource_name


def _get_time_stamp():
    return time.strftime("%d%m%y-%H%M%S", time.localtime())


def _check_download_from_tftp(output):
    """Verify if file was successfully uploaded

    :param output: output from cli
    :return True or False, and success or error message
    :rtype tuple
    """

    status_match = re.search('\[OK - [0-9]* bytes\]', output)
    is_success = (status_match is not None)
    message = ''
    if not is_success:
        match_error = re.search('%', output, re.IGNORECASE)
        if match_error:
            message = output[match_error.end():]
            message = message.split('\n')[0]
        else:
            is_success = True

    return is_success, message


# def _is_valid_copy_filesystem(filesystem):
#     return not re.match('bootflash$|tftp$|ftp$|harddisk$|nvram$|pram$|flash$|localhost$', filesystem) is None


class CiscoConfigurationOperations(ConfigurationOperationsInterface, FirmwareOperationsInterface):
    def __init__(self, cli=None, logger=None, api=None, resource_name=None):
        self._cli = cli
        self._logger = logger
        self._api = api
        try:
            self.resource_name = resource_name or get_resource_name()
        except Exception:
            raise Exception('CiscoHandlerBase', 'ResourceName is empty or None')

    @property
    def logger(self):
        if self._logger is None:
            try:
                self._logger = inject.instance('logger')
            except:
                raise Exception('Cisco OS', 'Logger is none or empty')
        return self._logger

    @property
    def api(self):
        if self._api is None:
            try:
                self._api = inject.instance('api')
            except:
                raise Exception('Cisco OS', 'Api handler is none or empty')
        return self._api

    @property
    def cli(self):
        if self._cli is None:
            try:
                self._cli = inject.instance('cli_service')
            except:
                raise Exception('Cisco OS', 'Cli Service is none or empty')
        return self._cli

    def copy(self, source_file='', destination_file='', vrf=None, timeout=600, retries=5):
        host = None

        if '://' in source_file:
            source_file_data_list = re.sub('/+', '/', source_file).split('/')
            host = source_file_data_list[1]
            filename = source_file_data_list[-1]
        elif '://' in destination_file:
            destination_file_data_list = re.sub('/+', '/', destination_file).split('/')
            host = destination_file_data_list[1]
            filename = destination_file_data_list[-1]
        else:
            filename = destination_file

        if host and not validateIP(host):
            raise Exception('Cisco OS', 'Copy method: remote host ip is not valid!')

        copy_command_str = 'copy {0} {1}'.format(source_file, destination_file)
        if vrf:
            copy_command_str += ' vrf {0}'.format(vrf)

        expected_map = OrderedDict()
        if host:
            expected_map[host] = lambda session: session.send_line('')
        expected_map['{0}|\s+[Vv][Rr][Ff]\s+|\[confirm\]|\?'.format(filename)] = lambda session: session.send_line('')

        output = self.cli.send_command(command=copy_command_str, expected_map=expected_map)

        match_data = re.search('(ERROR|[Ee]rror).*', output, re.DOTALL)
        is_downloaded = _check_download_from_tftp(output)

        if is_downloaded is False or match_data:
            if match_data:
                self.logger.error(match_data.group())
                raise Exception('Cisco OS', 'Failed to copy {0} to {1}, Please see logs for additional info'.format(
                    source_file, destination_file))
            else:
                self.logger.error(is_downloaded[1])
                raise Exception('Cisco OS', is_downloaded[1])

        if is_downloaded[1] == '':
            if re.search('(error|fail)', output.lower()):
                msg = 'Failed to copy configuration, \n{0}'.format(output)
                is_downloaded = (False, msg)
            else:
                msg = 'Successfully copied configuration'
                is_downloaded = (True, msg)
        return is_downloaded

    def configure_replace(self, source_filename, timeout=30):
        """Replace config on target device with specified one

        :param source_filename: full path to the file which will replace current running-config
        :param timeout: period of time code will wait for replace to finish
        """

        if not source_filename:
            raise Exception('Cisco IOS', "Config replace method doesn't have source filename!")
        command = 'configure replace ' + source_filename
        expected_map = {
            '\[[Nn]o\]|\[[Yy]es\]:': lambda session: session.send_line('yes')
        }
        output = self.cli.send_command(command=command, expected_map=expected_map, timeout=timeout)
        match_error = re.search('[Ee]rror:', output)
        if match_error is not None:
            error_str = output[match_error.end() + 1:]
            error_str = error_str[:error_str.find('\n')]
            raise Exception('Cisco IOS', 'Configure replace error: ' + error_str)

    def reload(self, sleep_timeout=60, retries=5):
        """Reload device

        :param sleep_timeout: period of time, to wait for device to get back online
        :param retries: amount of retires to get response from device after it will be rebooted
        """

        expected_map = {'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session: session.send_line('yes'),
                        '[\[\(][Yy]/[Nn][\)\]]': lambda session: session.send_line('y')}
        try:
            self.cli.send_command(command='reload', expected_map=expected_map)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            output = self.cli.send_command('sh ver')
        # output = self.cli.send_command(command='', expected_map={})

        retry = 0
        is_reloaded = False
        while retry < retries:
            retry += 1

            time.sleep(sleep_timeout)
            try:
                output = self.cli.send_command(command='', expected_str='(?<![#\n])[#>] *$', expected_map={}, timeout=5,
                                               is_need_default_prompt=False)
                if len(output) == 0:
                    continue

                is_reloaded = True
                break
            except Exception as e:
                self.logger.error('CiscoHandlerBase', 'Reload receives error: {0}'.format(e.message))
                pass

        return is_reloaded

    def update_firmware(self, remote_host, file_path, size_of_firmware=200000000):
        """Update firmware version on device by loading provided image, performs following steps:

            1. Copy bin file from remote tftp server.
            2. Clear in run config boot system section.
            3. Set downloaded bin file as boot file and then reboot device.
            4. Check if firmware was successfully installed.

        :param remote_host: host with firmware
        :param file_path: relative path on remote host
        :param size_of_firmware: size in bytes
        :return: status / exception
        """

        firmware_obj = CiscoFirmwareData(file_path)
        if firmware_obj.get_name() is None:
            raise Exception('Cisco IOS', "Invalid firmware name!\n \
                                Firmware file must have: title, extension.\n \
                                Example: isr4400-universalk9.03.10.00.S.153-3.S-ext.SPA.bin\n\n \
                                Current path: " + file_path)

            # if not validateIP(remote_host):
            #     raise Exception('Cisco IOS', "Not valid remote host IP address!")
        free_memory_size = self._get_free_memory_size('bootflash')

        # if size_of_firmware > free_memory_size:
        #    raise Exception('Cisco ISR 4K', "Not enough memory for firmware!")

        is_downloaded = self.copy(source_file=remote_host,
                                  destination_file='bootflash:/' + file_path, timeout=600, retries=2)

        if not is_downloaded[0]:
            raise Exception('Cisco IOS', "Failed to download firmware from " + remote_host +
                            file_path + "!\n" + is_downloaded[1])

        self.cli.send_command(command='configure terminal', expected_str='(config)#')
        self._remove_old_boot_system_config()
        output = self.cli.send_command('do show run | include boot')

        is_boot_firmware = False
        firmware_full_name = firmware_obj.get_name() + \
                             '.' + firmware_obj.get_extension()

        retries = 5
        while (not is_boot_firmware) and (retries > 0):
            self.cli.send_command(command='boot system flash bootflash:' + firmware_full_name, expected_str='(config)#')
            self.cli.send_command(command='config-reg 0x2102', expected_str='(config)#')

            output = self.cli.send_command('do show run | include boot')

            retries -= 1
            is_boot_firmware = output.find(firmware_full_name) != -1

        if not is_boot_firmware:
            raise Exception('Cisco IOS', "Can't add firmware '" + firmware_full_name + "' dor boot!")

        self.cli.send_command(command='exit')
        output = self.cli.send_command(command='copy run start',
                                       expected_map={'\?': lambda session: session.send_line('')})
        is_reloaded = self.reload()
        output_version = self.cli.send_command(command='show version | include image file')

        is_firmware_installed = output_version.find(firmware_full_name)
        if is_firmware_installed != -1:
            return 'Finished updating firmware!'
        else:
            raise Exception('Cisco IOS', 'Firmware update was unsuccessful!')

    def _get_resource_attribute(self, resource_full_path, attribute_name):
        """Get resource attribute by provided attribute_name

        :param resource_full_path: resource name or full name
        :param attribute_name: name of the attribute
        :return: attribute value
        :rtype: string
        """

        try:
            result = self.api.GetAttributeValue(resource_full_path, attribute_name).Value
        except Exception as e:
            raise Exception(e.message)
        return result

    def save_configuration(self, destination_host, source_filename, vrf=None):
        """Backup 'startup-config' or 'running-config' from device to provided file_system [ftp|tftp]
        Also possible to backup config to localhost
        :param destination_host:  tftp/ftp server where file be saved
        :param source_filename: what file to backup
        :return: status message / exception
        """

        if source_filename == '':
            source_filename = 'running-config'
        if '-config' not in source_filename:
            source_filename = source_filename.lower() + '-config'
        if ('startup' not in source_filename) and ('running' not in source_filename):
            raise Exception('Cisco OS', "Source filename must be 'startup' or 'running'!")
        if destination_host == '':
            raise Exception('Cisco OS', "Destination host is empty")

        system_name = re.sub('\s+', '_', self.resource_name)
        if len(system_name) > 23:
            system_name = system_name[:23]

        destination_filename = '{0}-{1}-{2}'.format(system_name, source_filename.replace('-config', ''),
                                                    _get_time_stamp())
        self.logger.info('destination filename is {0}'.format(destination_filename))

        if len(destination_host) <= 0:
            destination_host = self._get_resource_attribute(self.resource_name, 'Backup Location')
            if len(destination_host) <= 0:
                raise Exception('Folder path and Backup Location is empty')
        if destination_host.endswith('/'):
            destination_file = destination_host + destination_filename
        else:
            destination_file = destination_host + '/' + destination_filename

        is_uploaded = self.copy(destination_file=destination_file, source_file=source_filename, vrf=vrf)
        if is_uploaded[0] is True:
            self.logger.info('Save complete')
            return '{0},'.format(destination_filename)
        else:
            self.logger.info('Save failed with an error: {0}'.format(is_uploaded[1]))
            raise Exception(is_uploaded[1])

    def restore_configuration(self, source_file, config_type, restore_method='override', vrf=None):
        """Restore configuration on device from provided configuration file
        Restore configuration from local file system or ftp/tftp server into 'running-config' or 'startup-config'.
        :param source_file: relative path to the file on the remote host tftp://server/sourcefile
        :param restore_method: override current config or not
        :return:
        """

        if not re.search('append|override', restore_method.lower()):
            raise Exception('Cisco OS', "Restore method is wrong! Should be Append or Override")

        if '-config' not in config_type:
            config_type = config_type.lower() + '-config'

        self.logger.info('Start restoring device configuration from {}'.format(source_file))

        match_data = re.search('startup-config|running-config', config_type)
        if not match_data:
            raise Exception('Cisco OS', "Configuration type is empty or wrong")

        destination_filename = match_data.group()

        if source_file == '':
            raise Exception('Cisco OS', "Path is empty")

        # source_file = source_file.replace('127.0.0.1/', 'localhost/')

        if (restore_method.lower() == 'override') and (destination_filename == 'startup-config'):
            self.cli.send_command(command='del ' + destination_filename,
                                  expected_map={'\?|[confirm]': lambda session: session.send_line('')})

            is_uploaded = self.copy(source_file=source_file, destination_file=destination_filename, vrf=vrf)
        elif (restore_method.lower() == 'override') and (destination_filename == 'running-config'):

            if not self._check_replace_command():
                raise Exception('Override running-config is not supported for this device')
            self.configure_replace(source_filename=source_file, timeout=600)
            is_uploaded = (True, '')
        else:
            is_uploaded = self.copy(source_file=source_file, destination_file=destination_filename, vrf=vrf)

        if is_uploaded[0] is False:
            raise Exception('Cisco OS', is_uploaded[1])

        is_downloaded = (True, '')

        if is_downloaded[0] is True:
            return 'Finished restore configuration!'
        else:
            raise Exception('Cisco OS', is_downloaded[1])

    def _check_replace_command(self):
        """Checks whether replace command exist on device or not
        """

        output = self.cli.send_command('configure replace')
        if re.search('invalid (input|command)', output.lower()):
            return False
        return True

    def _remove_old_boot_system_config(self):
        """Clear boot system parameters in current configuration
        """

        data = self.cli.send_command('do show run | include boot')
        start_marker_str = 'boot-start-marker'
        index_begin = data.find(start_marker_str)
        index_end = data.find('boot-end-marker')

        if index_begin == -1 or index_end == -1:
            return

        data = data[index_begin + len(start_marker_str):index_end]
        data_list = data.split('\n')

        for line in data_list:
            if line.find('boot system') != -1:
                self.cli.send_command(command='no ' + line, expected_str='(config)#')

    def _get_free_memory_size(self, partition):
        """Get available memory size on provided partition
        :param partition: file system
        :return: size of free memory in bytes
        """

        cmd = 'dir {0}:'.format(partition)
        output = self.cli.send_command(command=cmd, retries=100)

        find_str = 'bytes total ('
        position = output.find(find_str)
        if position != -1:
            size_str = output[(position + len(find_str)):]

            size_match = re.match('[0-9]*', size_str)
            if size_match:
                return int(size_match.group())
            else:
                return -1
        else:
            return -1
