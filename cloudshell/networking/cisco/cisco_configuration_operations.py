import time
from collections import OrderedDict
from posixpath import join

import re
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_command_modes import EnableCommandMode, ConfigCommandMode, get_session
from cloudshell.networking.operations.configuration_operations import ConfigurationOperations
from cloudshell.shell.core.context_utils import get_attribute_by_name
from cloudshell.shell.core.interfaces.save_restore import OrchestrationSavedArtifact


def _get_time_stamp():
    return time.strftime("%d%m%y-%H%M%S", time.localtime())


# def _is_valid_copy_filesystem(filesystem):
#     return not re.match('bootflash$|tftp$|ftp$|harddisk$|nvram$|pram$|flash$|localhost$', filesystem) is None


def _validate_restore_method(restore_method):
    restore_method = restore_method or "override"
    if not re.search('append|override', restore_method.lower()):
        raise Exception("Cisco OS",
                        "Restore method '{}' is wrong! Use 'Append' or 'Override'".format(restore_method))

    return restore_method.lower()


def _validate_configuration_type(configuration_type):
    configuration_type = configuration_type or "running"
    if not re.search("startup|running", configuration_type, re.IGNORECASE):
        raise Exception("Configuration type must be 'Running' or 'Startup'!")

    return configuration_type.lower()


def configure_replace(current_session, logger, source_filename, timeout=30, vrf=None):
    """Replace config on target device with specified one
    :param source_filename: full path to the file which will replace current running-config
    :param timeout: period of time code will wait for replace to finish
    """
    if not source_filename:
        raise Exception('Cisco IOS', "No source filename provided for config replace method!")
    command = 'configure replace ' + source_filename
    action_map = {
        '[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session, logger: session.send_line('yes', logger),
        '\(y\/n\)': lambda session, logger: session.send_line('y', logger),
        '[\[\(][Nn]o[\)\]]': lambda session, logger: session.send_line('y', logger),
        '[\[\(][Yy]es[\)\]]': lambda session, logger: session.send_line('y', logger),
        '[\[\(][Yy]/[Nn][\)\]]': lambda session, logger: session.send_line('y', logger),
        'overwrit+e': lambda session, logger: session.send_line('yes', logger)
    }
    output = current_session.send_command(command=command, action_map=action_map, timeout=timeout)
    match_error = re.search(r'[Ee]rror:', output)
    if match_error is not None:
        error_str = output[match_error.end() + 1:] + '\n'
        error_str += error_str[:error_str.find('\n')]
        logger.error('Configure replace completed with error: ' + error_str)
        raise Exception('Cisco IOS', 'Configure replace completed with error: ' + error_str)


class CiscoConfigurationOperations(ConfigurationOperations):
    def __init__(self, cli, api, logger, context):
        super(CiscoConfigurationOperations, self).__init__(logger, api, context)
        self._cli = cli
        self._session_type = get_session(api=api, context=context)
        self._enable_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self._config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)

    def save_configuration(self, folder_path, configuration_type=None, vrf_management_name=None):
        response = self.save(folder_path, configuration_type, vrf_management_name)
        return response.identifier.split('/')[-1]

    def save(self, folder_path, configuration_type=None, vrf_management_name=None):
        """Backup 'startup-config' or 'running-config' from device to provided file_system [ftp|tftp]
        Also possible to backup config to localhost
        :param folder_path:  tftp/ftp server where file be saved
        :param configuration_type: type of configuration that will be saved (StartUp or Running)
        :param vrf_management_name: Virtual Routing and Forwarding management name
        :return: status message / exception
        """

        full_path = self.get_path(folder_path)
        if not vrf_management_name:
            vrf_management_name = get_attribute_by_name(context=self._context, attribute_name='VRF Management Name')

        configuration_type = _validate_configuration_type(configuration_type)

        source_filename = '{}-config'.format(configuration_type.lower())
        system_name = re.sub('\s+', '_', self._resource_name)
        system_name = system_name[:23]

        destination_filename = '{0}-{1}-{2}'.format(system_name, configuration_type.lower(), _get_time_stamp())
        self._logger.info('destination filename is {0}'.format(destination_filename))

        destination_file = join(full_path, destination_filename)
        with self._cli.get_session(new_sessions=self._session_type, command_mode=self._enable_mode,
                                   logger=self._logger) as session:
            is_uploaded = self.copy(current_session=session, logger=self._logger, source_file=source_filename,
                                    destination_file=destination_file, vrf=vrf_management_name)

        if is_uploaded[0] is True:
            self._logger.info('Save configuration completed.')
            identifier = destination_file
            artifact_type = full_path.split(':')[0]
            return OrchestrationSavedArtifact(identifier=identifier, artifact_type=artifact_type)
        else:
            self._logger.info('Save configuration failed with errors: {0}'.format(is_uploaded[1]))
            raise Exception(is_uploaded[1])

    def restore(self, path, configuration_type=None, restore_method=None, vrf_management_name=None):
        # def restore_configuration(self, source_file, config_type, restore_method='override', vrf=None):
        """Restore configuration on device from provided configuration file
        Restore configuration from local file system or ftp/tftp server into 'running-config' or 'startup-config'.
        :param path: relative path to the file on the remote host tftp://server/sourcefile
        :param configuration_type: the configuration type to restore (StartUp or Running)
        :param restore_method: override current config or not
        :param vrf_management_name: Virtual Routing and Forwarding management name
        :return:
        """

        is_uploaded = (False, "")
        configuration_type = _validate_configuration_type(configuration_type)
        restore_method = _validate_restore_method(restore_method)

        if not vrf_management_name:
            vrf_management_name = get_attribute_by_name('VRF Management Name')

        destination_filename = configuration_type

        if '-config' not in destination_filename:
            destination_filename = "{}-config".format(destination_filename)

        self._logger.info('Restore device configuration from {}'.format(path))

        if path == '':
            raise Exception('Cisco OS', "Source Path is empty.")
        with self._cli.get_session(new_sessions=self._session_type, command_mode=self._enable_mode,
                                   logger=self._logger) as session:
            if (restore_method == 'override') and (destination_filename == 'startup-config'):
                session.send_command(command='del nvram:' + destination_filename,
                                     action_map=OrderedDict(
                                         {'[Dd]elete [Ff]ilename '.format(destination_filename): lambda
                                             session, logger: session.send_line(destination_filename, logger),
                                          '[confirm]': lambda session, logger: session.send_line('', logger),
                                          '\?': lambda session, logger: session.send_line('', logger)}))
                is_uploaded = self.copy(current_session=session, logger=self._logger, source_file=path,
                                        destination_file=destination_filename, vrf=vrf_management_name)
            elif (restore_method == 'override') and (destination_filename == 'running-config'):

                if not self._check_replace_command(output=session.send_command('configure replace')):
                    raise Exception('Overriding running-config is not supported for this device.')

                configure_replace(current_session=session, logger=self._logger, source_filename=path, timeout=600,
                                  vrf=vrf_management_name)
                is_uploaded = (True, '')
            else:
                is_uploaded = self.copy(current_session=session, logger=self._logger, source_file=path,
                                        destination_file=destination_filename, vrf=vrf_management_name)

        if is_uploaded[0] is True:
            return 'Restore configuration completed.'
        else:
            raise Exception('Cisco OS', is_uploaded[1])

    @staticmethod
    def copy(current_session, logger, source_file='', destination_file='', vrf=None, timeout=600, retries=5):
        """Copy file from device to tftp or vice versa, as well as copying inside devices filesystem

        :param source_file: source file.
        :param destination_file: destination file.
        :return tuple(True or False, 'Success or Error message')
        """

        host = None
        action_map = OrderedDict()
        action_map[r'\[confirm\]'] = lambda session, logger: session.send_line('', logger)
        action_map[r'\(y/n\)'] = lambda session, logger: session.send_line('y', logger)
        action_map[r'[Oo]verwrit+e'] = lambda session, logger: session.send_line('y', logger)
        action_map[r'\([Yy]es/[Nn]o\)'] = lambda session, logger: session.send_line('yes', logger)
        # action_map[r'bytes'] = lambda session, logger: session.send_line('', logger)
        action_map[r'\s+[Vv][Rr][Ff]\s+'] = lambda session, logger: session.send_line('', logger)

        if '://' in source_file:
            source_file_data_list = re.sub('/+', '/', source_file).split('/')
            host = source_file_data_list[1]
            destination_file_name = destination_file.split(':')[-1].split('/')[-1]
            action_map[r'(?!/){}'.format(source_file_data_list[-1])] = lambda session, logger: session.send_line('', logger)
            action_map[r'[\[\(]{}[\)\]]'.format(destination_file_name)] = lambda session, logger: session.send_line('', logger)
        elif '://' in destination_file:
            destination_file_data_list = re.sub('/+', '/', destination_file).split('/')
            host = destination_file_data_list[1]
            source_file_name = source_file.split(':')[-1].split('/')[-1]
            action_map[r'[\[\(]{}[\)\]]'.format(destination_file_data_list[-1])] = lambda session, logger: session.send_line('', logger)
            action_map[r'(?!/){}'.format(source_file_name)] = lambda session, logger: session.send_line('', logger)
        else:
            destination_file_name = destination_file.split(':')[-1].split('/')[-1]
            source_file_name = source_file.split(':')[-1].split('/')[-1]
            action_map[r'[\[\(]{}[\)\]]'.format(destination_file_name)] = lambda session, logger: session.send_line('', logger)
            action_map[r'[\[\(]{}[\)\]]'.format(source_file_name)] = lambda session, logger: session.send_line('', logger)

        if host:
            if '@' in host:
                storage_data = re.search(r'^(?P<user>\S+):(?P<password>\S+)@(?P<host>\S+)', host)
                if storage_data:
                    host = storage_data.groupdict()['host']
                    password = storage_data.groupdict()['password']
                    action_map[r'[Pp]assword:'.format(source_file)] = lambda session, logger: session.send_line(
                        password, logger)
                else:
                    host = host.split('@')[-1]
            action_map[r"(?!/){}(?!/)".format(host)] = lambda session, logger: session.send_line('', logger)

        action_map[r'\?'] = lambda session, logger: session.send_line('', logger)

        copy_command_str = 'copy {0} {1}'.format(source_file, destination_file)
        if vrf:
            copy_command_str += ' vrf {}'.format(vrf)

        output = current_session.send_command(command=copy_command_str, action_map=action_map, timeout=60)

        return CiscoConfigurationOperations._check_download_from_tftp(logger=logger, output=output)

    @staticmethod
    def _check_download_from_tftp(logger, output):
        """Verify if file was successfully uploaded
        :param output: output from send_command_operations
        :return True or False, and success or error message
        :rtype tuple
        """
        is_success = True
        status_match = re.search(r'\d+ bytes copied|copied.*[\[\(].*[0-9]* bytes.*[\)\]]|[Cc]opy complete', output,
                                 re.IGNORECASE)
        message = ''
        if not status_match:
            is_success = False
            match_error = re.search('%.*|TFTP put operation failed.*|sysmgr.*not supported.*\n', output, re.IGNORECASE)
            message = 'Copy Command failed. '
            if match_error:
                logger.error(message)
                message += re.sub('^%|\\n', '', match_error.group())
            else:
                error_match = re.search(r"error.*\n|fail.*\n", output, re.IGNORECASE)
                if error_match:
                    logger.error(message)
                    message += error_match.group()

        return is_success, message

    @staticmethod
    def _check_replace_command(output):
        """Checks whether replace command exist on device or not
        :rtype : bool
        :param output:
        """

        if re.search(r'invalid (input|command)', output.lower()):
            return False
        return True
