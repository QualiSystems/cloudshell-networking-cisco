import time
import inject
import jsonpickle
import traceback
from collections import OrderedDict

from cloudshell.core.action_result import ActionResult
from cloudshell.core.driver_response import DriverResponse
from cloudshell.core.driver_response_root import DriverResponseRoot
from cloudshell.networking.networking_utils import *
from cloudshell.networking.cisco.command_templates.ethernet import ETHERNET_COMMANDS_TEMPLATES
from cloudshell.networking.cisco.command_templates.vlan import VLAN_COMMANDS_TEMPLATES
from cloudshell.networking.cisco.command_templates.cisco_interface import ENTER_INTERFACE_CONF_MODE
from cloudshell.cli.command_template.command_template_service import add_templates, get_commands_list
from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload
from cloudshell.networking.cisco.firmware_data.cisco_firmware_data import CiscoFirmwareData
from cloudshell.shell.core.context_utils import get_resource_name
from cloudshell.networking.core.connectivity_request_helper import ConnectivityRequestDeserializer


class CiscoHandlerBase:
    APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST = ['type', 'actionId',
                                                                 ('connectionParams', 'mode'),
                                                                 ('actionTarget', 'fullAddress')]

    @inject.params(cli='cli_service', logger='logger', snmp='snmp_handler', api='api')
    def __init__(self, cli, logger, snmp, api, resource_name=None):
        """Create CiscoIOSHandlerBase

        :param cli: CliService object
        :param logger: QsLogger object
        :param snmp: QualiSnmp object
        :param api: CloudShell Api object
        :param resource_name: resource name
        :return:
        """

        self.supported_os = []
        self.cli = cli
        self.logger = logger
        self.api = api
        self.snmp_handler = snmp
        try:
            self.resource_name = resource_name or get_resource_name()
        except Exception:
            raise Exception('CiscoHandlerBase', 'ResourceName is empty or None')

    def send_command(self, command, expected_str=None, expected_map=None, timeout=30, retries=10,
                     is_need_default_prompt=True, session=None):
        """Send command

        :param command: cli command
        :param expected_str: optional, custom expected string, if you expect something different from default prompts
        :param expected_map: optional, custom expected map, if you expect some actions in progress of the command
        :param timeout: optional, custom timeout
        :param retries: optional, custom retry count, if you need more than 5 retries
        :param is_need_default_prompt: default
        :param session:
        :return output from cli
        :rtype: string
        """

        if session:
            response = self.cli.send_command(command=command, expected_str=expected_str, expected_map=expected_map,
                                             timeout=timeout, retries=retries,
                                             is_need_default_prompt=is_need_default_prompt, session=session)
        else:
            response = self.cli.send_command(command=command, expected_str=expected_str, expected_map=expected_map,
                                             timeout=timeout, retries=retries,
                                             is_need_default_prompt=is_need_default_prompt)
        return response

    def send_config_command(self, command, expected_str=None, expected_map=None, timeout=30, retries=10,
                            is_need_default_prompt=True):
        """Send list of config commands

        :param command_list: list of commands
        :return output from cli
        :rtype: string
        """

        return self.cli.send_config_command(command, expected_str, expected_map, timeout, retries,
                                            is_need_default_prompt)

    def send_config_command_list(self, command_list):
        """Send list of config commands

        :param command_list: list of commands
        :return output from cli
        :rtype: string
        """

        result = self.cli.send_command_list(command_list)
        self.cli.exit_configuration_mode()
        return result

    def _show_command(self, data):
        """Execute command: show plus provided part of command, i.e. 'show version'

        :param data:
        :return: response from send_command method
        :rtype: string
        """

        return self.send_command('show {0}'.format(data))

    def _check_download_from_tftp(self, output):
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

    def apply_connectivity_changes(self, request):
        """Handle apply connectivity changes request json, trigger add or remove vlan methods,
        get responce from them and create json response

        :param request: json with all required action to configure or remove vlans from certain port
        :return Serialized DriverResponseRoot to json
        :rtype json
        """

        if request is None or request == '':
            raise Exception('CiscoHandlerBase', 'request is None or empty')

        holder = ConnectivityRequestDeserializer(jsonpickle.decode(request))

        if not holder or not hasattr(holder, 'driverRequest'):
            raise Exception('CiscoHandlerBase', 'Deserialized request is None or empty')

        driver_response = DriverResponse()
        results = []
        driver_response_root = DriverResponseRoot()

        for action in holder.driverRequest.actions:
            self.logger.info('Action: ', action.__dict__)
            self._validate_request_action(action)
            action_result = ActionResult()
            action_result.type = action.type
            action_result.actionId = action.actionId
            action_result.errorMessage = None
            action_result.infoMessage = None
            action_result.updatedInterface = action.actionTarget.fullName
            if action.type == 'setVlan':
                qnq = False
                ctag = ''
                for attribute in action.connectionParams.vlanServiceAttributes:
                    if attribute.attributeName.lower() == 'qnq':
                        request_qnq = attribute.attributeValue
                        if request_qnq.lower() == 'true':
                            qnq = True
                    elif attribute.attributeName.lower() == 'ctag':
                        ctag = attribute.attributeValue
                try:
                    action_result.infoMessage = self.add_vlan(action.connectionParams.vlanId,
                                                              action.actionTarget.fullAddress,
                                                              action.connectionParams.mode.lower(),
                                                              qnq,
                                                              ctag)
                except Exception as e:
                    self.logger.error('Add vlan failed: {0}'.format(traceback.format_exc()))
                    action_result.errorMessage = ', '.join(e.args)
                    action_result.success = False
            elif action.type == 'removeVlan':
                try:
                    action_result.infoMessage = self.remove_vlan(action.connectionParams.vlanId,
                                                                 action.actionTarget.fullAddress,
                                                                 action.connectionParams.mode.lower())
                except Exception as e:
                    self.logger.error('Remove vlan failed: {0}'.format(traceback.format_exc()))
                    action_result.errorMessage = ', '.join(e.args)
                    action_result.success = False
            else:
                continue
            results.append(action_result)

        driver_response.actionResults = results
        driver_response_root.driverResponse = driver_response
        return self.set_command_result(driver_response_root).replace('[true]', 'true')

    def _validate_request_action(self, action):
        """Validate action from the request json, according to APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST

        """
        is_fail = False
        fail_attribute = ''
        for class_attribute in self.APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST:
            if type(class_attribute) is tuple:
                if not hasattr(action, class_attribute[0]):
                    is_fail = True
                    fail_attribute = class_attribute[0]
                if not hasattr(getattr(action, class_attribute[0]), class_attribute[1]):
                    is_fail = True
                    fail_attribute = class_attribute[1]
            else:
                if not hasattr(action, class_attribute):
                    is_fail = True
                    fail_attribute = class_attribute

        if is_fail:
            raise Exception('CiscoHandlerBase',
                            'Mandatory field {0} is missing in ApplyConnectivityChanges request json'.format(
                                fail_attribute))

    def set_command_result(self, result, unpicklable=False):
        """Serializes output as JSON and writes it to console output wrapped with special prefix and suffix

        :param result: Result to return
        :param unpicklable: If True adds JSON can be deserialized as real object.
                            When False will be deserialized as dictionary
        """

        json = jsonpickle.encode(result, unpicklable=unpicklable)
        result_for_output = str(json)
        print result_for_output
        return result_for_output

    def _is_valid_copy_filesystem(self, filesystem):
        return not re.match('bootflash$|tftp$|ftp$|harddisk$|nvram$|pram$|flash$|localhost$', filesystem) is None

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

        error_expected_string = 'ERROR|[Ee]rror\s*:.*\n|(FAILED|[Ff]ailed)\n'  # \%?[Ee]rror.*\n|
        expected_map = OrderedDict()
        if host:
            expected_map[host] = lambda session: session.send_line('')
        expected_map['{0}|\s+[Vv][Rr][Ff]\s+|\[confirm\]|\?'.format(filename)] = lambda session: session.send_line('')

        output = self.send_command(command=copy_command_str, expected_str=error_expected_string,
                                   expected_map=expected_map)

        match_data = re.search(error_expected_string, output)
        is_downloaded = self._check_download_from_tftp(output)

        if is_downloaded is False or match_data:
            if match_data:
                raise Exception('Cisco OS', match_data.group().replace('\n', '').replace('%', ''))
            else:
                raise Exception('Cisco OS', is_downloaded[1])

        if is_downloaded[1] == '':
            if re.search('(error|fail)', output.lower()):
                msg = 'Failed to copy configuration.'
                msg += '\n{}'.format(output)
                is_downloaded = (False, msg)
            else:
                msg = 'Successfully copied configuration'
                is_downloaded = (True, msg)
        return is_downloaded

    def configure_replace(self, source_filename, timeout=30, vrf=None):
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
        output = self.send_command(command=command, expected_map=expected_map, timeout=timeout)
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

        output = self.send_command(command='reload', expected_str='\[yes/no\]:|[confirm]')

        if re.search('\[yes/no\]:', output):
            self.send_command(command='yes', expected_str='[confirm]')
        elif re.search('\[y/n\]:', output):
            self.send_command(command='y', expected_str='[confirm]')

        output = self.send_command(command='', expected_str='.*', expected_map={})

        retry = 0
        is_reloaded = False
        while retry < retries:
            retry += 1

            time.sleep(sleep_timeout)
            try:
                output = self.send_command(command='', expected_str='(?<![#\n])[#>] *$', expected_map={}, timeout=5,
                                           is_need_default_prompt=False)
                if len(output) == 0:
                    continue

                is_reloaded = True
                break
            except Exception as e:
                self.logger.error('CiscoHandlerBase', 'Reload receives error: {0}'.format(e.message))
                pass

        return is_reloaded

    def _does_interface_support_qnq(self, interface_name):
        """Validate whether qnq is supported for certain port

        """

        result = False
        self.send_config_command('interface {0}'.format(interface_name))
        output = self.send_config_command('switchport mode ?')
        if 'dot1q-tunnel' in output.lower():
            result = True
        self.cli.exit_configuration_mode()
        return result

    def _get_resource_full_name(self, port_resource_address, resource_details_map):
        """Recursively search for port name on the resource

        :param port_resource_address: port resource address
        :param resource_details_map: full device resource structure
        :return: full port resource name (Cisco2950/Chassis 0/FastEthernet0-23)
        :rtype: string
        """

        result = None
        for port in resource_details_map.ChildResources:
            if port.FullAddress in port_resource_address and port.FullAddress == port_resource_address:
                return port.Name
            if port.FullAddress in port_resource_address and port.FullAddress != port_resource_address:
                result = self._get_resource_full_name(port_resource_address, port)
            if result is not None:
                return result
        return result

    def _load_vlan_command_templates(self):
        """Load all required Commandtemplates to configure valn on certain port

        """

        add_templates(ETHERNET_COMMANDS_TEMPLATES)
        add_templates(VLAN_COMMANDS_TEMPLATES)
        add_templates(ENTER_INTERFACE_CONF_MODE)

    def add_vlan(self, vlan_range, port_list, port_mode, qnq, ctag):
        """Configure specified vlan range in specified switchport mode on provided port

        :param vlan_range: range of vlans to be added, if empty, and switchport_type = trunk,
        trunk mode will be assigned
        :param port_list: List of interfaces Resource Full Address
        :param port_mode: type of adding vlan ('trunk' or 'access')
        :param qnq: QNQ parameter for switchport mode dot1nq
        :param ctag: CTag details
        :return: success message
        :rtype: string
        """

        self._load_vlan_command_templates()
        self.validate_vlan_methods_incoming_parameters(vlan_range, port_list, port_mode)
        for port in port_list.split('|'):
            port_name = self.get_port_name(port)
            self.logger.info('Start assigning Vlan {0} to interface {1}'.format(vlan_range, port_name))
            vlan_config_actions = OrderedDict()
            interface_config_actions = OrderedDict()
            vlan_config_actions['configure_vlan'] = vlan_range
            vlan_config_actions['state_active'] = []
            vlan_config_actions['no_shutdown'] = []

            self.configure_vlan(vlan_config_actions)
            self.cli.exit_configuration_mode()

            interface_config_actions['configure_interface'] = port_name
            interface_config_actions['no_shutdown'] = []
            if self.supported_os and 'NXOS' in self.supported_os:
                interface_config_actions['switchport'] = []
            if 'trunk' in port_mode and vlan_range == '':
                interface_config_actions['switchport_mode_trunk'] = []
            elif 'trunk' in port_mode and vlan_range != '':
                interface_config_actions['switchport_mode_trunk'] = []
                interface_config_actions['trunk_allow_vlan'] = [vlan_range]
            elif 'access' in port_mode and vlan_range != '':
                if not qnq or qnq is False:
                    self.logger.info('qnq is {0}'.format(qnq))
                    interface_config_actions['switchport_mode_access'] = []
                interface_config_actions['access_allow_vlan'] = [vlan_range]
            if qnq and qnq is True:
                if not self._does_interface_support_qnq(port_name):
                    raise Exception('interface does not support QnQ')
                if 'switchport_mode_trunk' in interface_config_actions:
                    raise Exception('interface cannot have trunk and dot1q-tunneling modes in the same time')
                interface_config_actions['qnq'] = []

            self.configure_vlan_on_interface(interface_config_actions)
            self.cli.exit_configuration_mode()
            self.logger.info('Vlan {0} was assigned to the interface {1}'.format(vlan_range, port_name))
        return 'Vlan Configuration Completed'

    def remove_vlan(self, vlan_range, port_list, port_mode):
        """
        Remove vlan from port
        :param vlan_range: range of vlans to be added, if empty, and switchport_type = trunk,
        trunk mode will be assigned
        :param port_list: List of interfaces Resource Full Address
        :param port_mode: type of adding vlan ('trunk' or 'access')
        :return: success message
        :rtype: string
        """

        self._load_vlan_command_templates()
        self.validate_vlan_methods_incoming_parameters(vlan_range, port_list, port_mode)
        for port in port_list.split('|'):
            port_name = self.get_port_name(port)
            self.logger.info('Vlan {0} will be removed from interface {1}'.format(vlan_range, port_name))
            interface_config_actions = OrderedDict()
            interface_config_actions['configure_interface'] = port_name
            self.configure_vlan_on_interface(interface_config_actions)
            self.logger.info(
                'All vlans and switchport configuration were removed from the interface {0}'.format(port_name))
        return 'Vlan Configuration Completed'

    def validate_vlan_methods_incoming_parameters(self, vlan_range, port_list, port_mode):
        """Validate add_vlan and remove_vlan incoming parameters

        :param vlan_range: vlan range (10,20,30-40)
        :param port_list: list of port resource addresses ([192.168.1.1/0/34, 192.168.1.1/0/42])
        :param port_mode: switchport mode (access or trunk)
        """

        self.logger.info('Vlan Configuration Started')
        if len(port_list) < 1:
            raise Exception('CiscoHandlerBase', 'Port list is empty')
        if vlan_range == '' and port_mode == 'access':
            raise Exception('CiscoHandlerBase', 'Switchport type is Access, but vlan id/range is empty')
        if (',' in vlan_range or '-' in vlan_range) and port_mode == 'access':
            raise Exception('CiscoHandlerBase', 'Only one vlan could be assigned to the interface in Access mode')

    def get_port_name(self, port):
        """Get port name from port resource full address

        :param port: port resource full address (192.168.1.1/0/34)
        :return: port name (FastEthernet0/23)
        :rtype: string
        """

        port_resource_map = self.api.GetResourceDetails(self.resource_name)
        temp_port_full_name = self._get_resource_full_name(port, port_resource_map)
        if not temp_port_full_name:
            self.logger.error('Interface was not found')
            raise Exception('Cisco OS', 'Interface name was not found')

        temp_port_name = temp_port_full_name.split('/')[-1]
        if 'port-channel' not in temp_port_full_name.lower():
            temp_port_name = temp_port_name.replace('-', '/')

        self.logger.info('Interface name validated: {0}'.format(temp_port_name))
        return temp_port_name

    def configure_vlan_on_interface(self, commands_dict):
        """
        Configures vlan on devices interface
        :param commands_dict: dictionary of parameters
        :return: success message
        :rtype: string
        """

        commands_list = get_commands_list(commands_dict)
        qnq = None
        if 'NXOS' in self.supported_os:
            for commands_list_item in commands_list:
                if 'dot1q-tunnel' in commands_list_item:
                    qnq = commands_list_item
                    break
            if qnq and qnq in commands_list:
                commands_list.remove(qnq)

        current_config = self._show_command('running-config interface {0}'.format(commands_dict['configure_interface']))

        for line in current_config.splitlines():
            if re.search('^\s*switchport\s+', line):
                line_to_remove = re.sub('\s+\d+[-\d+,]+', '', line)
                if not line_to_remove:
                    line_to_remove = line
                commands_list.insert(1, 'no {0}'.format(line_to_remove.strip(' ')))

        output = self.send_config_command_list(commands_list)
        if qnq:
            config_command = self.send_config_command(qnq, expected_str='\(y/n\).*\?\s*\[(y|n|[Yy]es|[Nn]o)\]')
            if 'continue(' in config_command:
                self.send_command('y')

        if re.search('[Cc]ommand rejected.*', output):
            error = 'Command rejected'
            if re.search('[Cc]ommand rejected.*', output):
                error = 'Command rejected'
                for line in output.splitlines():
                    if line.lower().startswith('command rejected'):
                        error = line.strip(' \t\n\r')
            raise Exception('Cisco OS', 'Failed to assign Vlan, {0}'.format(error))

        return 'Finished configuration of ethernet interface!'

    def configure_vlan(self, ordered_parameters_dict):
        """Configure vlan

        :param ordered_parameters_dict: dictionary of parameters
        :return: success message
        :rtype: string
        """

        commands_list = get_commands_list(ordered_parameters_dict)

        self.send_config_command_list(commands_list)
        return 'Finished configuration of ethernet interface!'

    def _is_valid_device_os(self):
        """Validate device OS using snmp
        :return: True or False
        """

        version = None

        system_description = self.snmp_handler.get(('SNMPv2-MIB', 'sysDescr'))['sysDescr']
        match_str = re.sub('[\n\r]+', ' ', system_description.upper())
        res = re.search('\s+(IOS[ -]XR|IOS-XE|CAT[ -]?OS|NX[ -]?OS|IOS)\s*', match_str)
        if res:
            version = res.group(0).strip(' \s\r\n')
        if version and version in self.supported_os:
            return True
        self.logger.info('System description from device: \'{0}\''.format(system_description))
        return False

    def discover_snmp(self):
        """Load device structure, and all required Attribute according to Networking Elements Standardization design
        :return: Attributes and Resources matrix,
        currently in string format (matrix separated by '$', lines by '|', columns by ',')
        """

        if not self._is_valid_device_os():
            error_message = 'Incompatible driver! Please use correct resource driver for {0} operation system(s)'. \
                format(str(tuple(self.supported_os)))
            self.logger.error(error_message)
            raise Exception(error_message)

        self.logger.info('************************************************************************')
        self.logger.info('Start SNMP discovery process .....')
        generic_autoload = CiscoGenericSNMPAutoload(self.snmp_handler, self.logger)
        result = generic_autoload.discover()
        self.logger.info('SNMP discovery Completed')
        return result

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

        is_downloaded = self.copy('tftp', 'bootflash', remote_host=remote_host,
                                  source_filename=file_path, timeout=600, retries=2)

        if not is_downloaded[0]:
            raise Exception('Cisco IOS', "Failed to download firmware from " + remote_host +
                            file_path + "!\n" + is_downloaded[1])

        self.send_command(command='configure terminal', expected_str='(config)#')
        self._remove_old_boot_system_config()
        output = self.send_command('do show run | include boot')

        is_boot_firmware = False
        firmware_full_name = firmware_obj.get_name() + \
                             '.' + firmware_obj.get_extension()

        retries = 5
        while (not is_boot_firmware) and (retries > 0):
            self.send_command(command='boot system flash bootflash:' + firmware_full_name, expected_str='(config)#')
            self.send_command(command='config-reg 0x2102', expected_str='(config)#')

            output = self.send_command('do show run | include boot')

            retries -= 1
            is_boot_firmware = output.find(firmware_full_name) != -1

        if not is_boot_firmware:
            raise Exception('Cisco IOS', "Can't add firmware '" + firmware_full_name + "' dor boot!")

        self.send_command(command='exit')
        output = self.send_command(command='copy run start', expected_map={'\?': lambda session: session.send_line('')})
        is_reloaded = self.reload()
        output_version = self.send_command(command='show version | include image file')

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

    def backup_configuration(self, destination_host, source_filename, vrf=None):
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
                                                    self._get_time_stamp())
        self.logger.info('destination filename is {0}'.format(destination_filename))

        if len(destination_host) <= 0:
            destination_host = self._get_resource_attribute(self.resource_name, 'Backup Location')
            if len(destination_host) <= 0:
                raise Exception('Folder path and Backup Location is empty')
        if destination_host.endswith('/'):
            destination_file = destination_host + destination_filename
        else:
            destination_file = destination_host + '/' + destination_filename

            # destination_file = destination_file.replace('127.0.0.1/', 'localhost/')
        is_uploaded = self.copy(destination_file=destination_file, source_file=source_filename, vrf=vrf)
        if is_uploaded[0] is True:
            self.logger.info('Save complete')
            return '{0},'.format(destination_filename)
        else:
            self.logger.info('Save failed with an error: {0}'.format(is_uploaded[1]))
            raise Exception(is_uploaded[1])

    def _get_time_stamp(self):
        return time.strftime("%d%m%y-%H%M%S", time.localtime())

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
            self.send_command(command='del ' + destination_filename,
                              expected_map={'\?|[confirm]': lambda session: session.send_line('')})

            is_uploaded = self.copy(source_file=source_file, destination_file=destination_filename, vrf=vrf)
        elif (restore_method.lower() == 'override') and (destination_filename == 'running-config'):

            if not self._check_replace_command():
                raise Exception('Override running-config is not supported for this device')
            self.configure_replace(source_filename=source_file, timeout=600, vrf=vrf)
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

        output = self.send_command('configure replace')
        if re.search('invalid (input|command)', output.lower()):
            return False
        return True

    def _remove_old_boot_system_config(self):
        """Clear boot system parameters in current configuration
        """

        data = self.send_command('do show run | include boot')
        start_marker_str = 'boot-start-marker'
        index_begin = data.find(start_marker_str)
        index_end = data.find('boot-end-marker')

        if index_begin == -1 or index_end == -1:
            return

        data = data[index_begin + len(start_marker_str):index_end]
        data_list = data.split('\n')

        for line in data_list:
            if line.find('boot system') != -1:
                self.send_command(command='no ' + line, expected_str='(config)#')

    def _get_free_memory_size(self, partition):
        """Get available memory size on provided partition
        :param partition: file system
        :return: size of free memory in bytes
        """

        cmd = 'dir {0}:'.format(partition)
        output = self.send_command(command=cmd, retries=100)

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
