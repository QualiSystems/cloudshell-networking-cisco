import inject
from collections import OrderedDict
import re

from cloudshell.networking.networking_utils import *
from cloudshell.networking.operations.connectivity_operations import ConnectivityOperations
from cloudshell.networking.cisco.command_templates.ethernet import ETHERNET_COMMANDS_TEMPLATES
from cloudshell.networking.cisco.command_templates.vlan import VLAN_COMMANDS_TEMPLATES
from cloudshell.networking.cisco.command_templates.cisco_interface import ENTER_INTERFACE_CONF_MODE
from cloudshell.cli.command_template.command_template_service import add_templates, get_commands_list
from cloudshell.shell.core.context_utils import get_resource_name


class CiscoConnectivityOperations(ConnectivityOperations):
    def __init__(self, cli=None, logger=None, api=None, resource_name=None):
        ConnectivityOperations.__init__(self)
        self._cli = cli
        self._logger = logger
        self._api = api
        try:
            self.resource_name = get_resource_name()
        except Exception:
            raise Exception('CiscoHandlerBase', 'ResourceName is empty or None')

    @property
    def logger(self):
        if self._logger is None:
            try:
                self._logger = inject.instance('logger')
            except:
                raise Exception('CiscoConnectivityOperations', 'Logger is none or empty')
        return self._logger

    @property
    def cli(self):
        if self._cli is None:
            try:
                self._cli = inject.instance('cli_service')
            except:
                raise Exception('CiscoConnectivityOperations', 'Cli Service is none or empty')
        return self._cli

    @property
    def api(self):
        if self._api is None:
            try:
                self._api = inject.instance('api')
            except:
                raise Exception('CiscoConnectivityOperations', 'Api handler is none or empty')
        return self._api

    def send_config_command_list(self, command_list, expected_map=None):
        """Send list of config commands

        :param command_list: list of commands
        :return output from cli
        :rtype: string
        """

        result = self.cli.send_command_list(command_list, expected_map=expected_map)
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

    def _does_interface_support_qnq(self, interface_name):
        """Validate whether qnq is supported for certain port

        """

        result = False
        self.cli.send_config_command('interface {0}'.format(interface_name))
        output = self.cli.send_config_command('switchport mode ?')
        if 'dot1q-tunnel' in output.lower():
            result = True
        self.cli.exit_configuration_mode()
        return result

    @staticmethod
    def _load_vlan_command_templates():
        """Load all required Commandtemplates to configure valn on certain port

        """

        add_templates(ETHERNET_COMMANDS_TEMPLATES)
        add_templates(VLAN_COMMANDS_TEMPLATES)
        add_templates(ENTER_INTERFACE_CONF_MODE)

    def add_vlan(self, vlan_range, port, port_mode, qnq, ctag):
        """Configure specified vlan range in specified switchport mode on provided port

        :param vlan_range: range of vlans to be added, if empty, and switchport_type = trunk,
        trunk mode will be assigned
        :param port: List of interfaces Resource Full Address
        :param port_mode: type of adding vlan ('trunk' or 'access')
        :param qnq: QNQ parameter for switchport mode dot1nq
        :param ctag: CTag details
        :return: success message
        :rtype: string
        """

        config = inject.instance('config')
        supported_os = config.SUPPORTED_OS
        self._load_vlan_command_templates()
        self.validate_vlan_methods_incoming_parameters(vlan_range, port, port_mode)
        port_name = self.get_port_name(port)
        self.logger.info('Start vlan configuration: vlan {0}; interface {1}.'.format(vlan_range, port_name))
        vlan_config_actions = OrderedDict()
        interface_config_actions = OrderedDict()
        vlan_config_actions['configure_vlan'] = vlan_range
        vlan_config_actions['state_active'] = []
        vlan_config_actions['no_shutdown'] = []

        self.configure_vlan(vlan_config_actions)
        self.cli.exit_configuration_mode()

        interface_config_actions['configure_interface'] = port_name
        interface_config_actions['no_shutdown'] = []
        if supported_os and 'NXOS' in supported_os:
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
            interface_config_actions['qnq'] = []

        self.configure_vlan_on_interface(interface_config_actions)
        result = self.cli.send_command('show running-config interface {0}'.format(port_name))
        self.logger.info('Vlan configuration completed: \n{0}'.format(result))

        return 'Vlan Configuration Completed'

    def remove_vlan(self, vlan_range, port, port_mode):
        """
        Remove vlan from port
        :param vlan_range: range of vlans to be added, if empty, and switchport_type = trunk,
        trunk mode will be assigned
        :param port: List of interfaces Resource Full Address
        :param port_mode: type of adding vlan ('trunk' or 'access')
        :return: success message
        :rtype: string
        """

        self._load_vlan_command_templates()
        self.validate_vlan_methods_incoming_parameters(vlan_range, port, port_mode)

        port_name = self.get_port_name(port)
        self.logger.info('Vlan {0} will be removed from interface {1}'.format(vlan_range, port_name))
        interface_config_actions = OrderedDict()
        interface_config_actions['configure_interface'] = port_name
        self.configure_vlan_on_interface(interface_config_actions)
        self.logger.info('Vlan configuration were removed from the interface {0}'.format(port_name))

        return 'Vlan Configuration Completed'

    def validate_vlan_methods_incoming_parameters(self, vlan_range, port, port_mode):
        """Validate add_vlan and remove_vlan incoming parameters

        :param vlan_range: vlan range (10,20,30-40)
        :param port_list: list of port resource addresses ([192.168.1.1/0/34, 192.168.1.1/0/42])
        :param port_mode: switchport mode (access or trunk)
        """

        self.logger.info('Vlan Configuration Started')
        if len(port) < 1:
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

        current_config = self.cli.send_command(
            'show running-config interface {0}'.format(commands_dict['configure_interface']))

        for line in current_config.splitlines():
            if re.search('^\s*switchport\s+', line):
                line_to_remove = re.sub('\s+\d+[-\d+,]+', '', line)
                if not line_to_remove:
                    line_to_remove = line
                commands_list.insert(1, 'no {0}'.format(line_to_remove.strip(' ')))

        expected_map = {'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session: session.send_line('yes'),
                        '[\[\(][Yy]/[Nn][\)\]]': lambda session: session.send_line('y')}
        output = self.send_config_command_list(commands_list, expected_map=expected_map)

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
