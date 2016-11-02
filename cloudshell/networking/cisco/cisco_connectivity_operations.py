from collections import OrderedDict
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cisco.cisco_command_modes import get_session, EnableCommandMode, ConfigCommandMode
from cloudshell.shell.core.context_utils import get_resource_name

from cloudshell.networking.networking_utils import *
from cloudshell.networking.operations.connectivity_operations import ConnectivityOperations
from cloudshell.networking.cisco.command_templates.ethernet import ETHERNET_COMMANDS_TEMPLATES
from cloudshell.networking.cisco.command_templates.vlan import VLAN_COMMANDS_TEMPLATES
from cloudshell.networking.cisco.command_templates.cisco_interface import ENTER_INTERFACE_CONF_MODE
from cloudshell.cli.command_template.command_template_service import add_templates, get_commands_list


def _does_interface_support_qnq(session, interface_name):
    """Validate whether qnq is supported for certain port

    """

    result = False
    session.send_config_command('interface {0}'.format(interface_name))
    output = session.send_config_command('switchport mode ?')
    if 'dot1q-tunnel' in output.lower():
        result = True
    session.exit_configuration_mode()
    return result


def send_config_command_list(session, command_list, expected_map=None):
    result = ''
    for command in command_list:
        result += session.send_command(command, expected_map=expected_map)

    return result


class CiscoConnectivityOperations(ConnectivityOperations):
    def __init__(self, cli, logger, api, context, supported_os):
        """
        Handle add/remove vlan flows

        :param cli:
        :param logger:
        :param api:
        :param context:
        :param supported_os:
        """
        ConnectivityOperations.__init__(self)
        self.cli = cli
        self._logger = logger
        self.api = api
        self.resource_name = get_resource_name(context)
        self.session_type = get_session(context=context, api=api)
        self._enable_mode = CommandModeHelper.create_command_mode(EnableCommandMode, context)
        self._config_mode = CommandModeHelper.create_command_mode(ConfigCommandMode, context)
        self.supported_os = supported_os

    @property
    def logger(self):
        return self._logger

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

        self._load_vlan_command_templates()
        self.validate_vlan_methods_incoming_parameters(vlan_range, port, port_mode)
        port_name = self.get_port_name(port)
        self.logger.info('Start vlan configuration: vlan {0}; interface {1}.'.format(vlan_range, port_name))

        with self.cli.get_session(new_sessions=self.session_type, command_mode=self._enable_mode,
                                  logger=self.logger) as session:

            with session.enter_mode(self._config_mode) as config_session:
                self.configure_vlan(config_session, self.prepare_vlan_config_commands(vlan_range))

            interface_config_actions = self.prepare_interface_config_commands(port_name=port_name, port_mode=port_mode,
                                                                              vlan_range=vlan_range, qnq=qnq)
            with session.enter_mode(self._config_mode) as config_session:
                if qnq:
                    if not _does_interface_support_qnq(config_session, port_name):
                        raise Exception('interface does not support QnQ')
                    interface_config_actions['qnq'] = []

                self.configure_vlan_on_interface(config_session, interface_config_actions)
            result = session.send_command('show running-config interface {0}'.format(port_name))
            self.logger.info('Vlan configuration completed: \n{0}'.format(result))

        return 'Vlan Configuration Completed.'

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

        with self.cli.get_session(new_sessions=self.session_type, command_mode=self._config_mode,
                                  logger=self.logger) as session:
            self._load_vlan_command_templates()
            self.validate_vlan_methods_incoming_parameters(vlan_range, port, port_mode)

            port_name = self.get_port_name(port)
            self.logger.info('Remove Vlan {0} from interface {1}'.format(vlan_range, port_name))
            interface_config_actions = OrderedDict()
            interface_config_actions['configure_interface'] = port_name
            self.configure_vlan_on_interface(session, interface_config_actions)
            result = session.send_command('do show running interface {}'.format(port_name))
            self.logger.info('Vlan configuration removed from the interface {0}'.format(port_name))

        return 'Remove Vlan Completed.'

    def validate_vlan_methods_incoming_parameters(self, vlan_range, port_range, port_mode):
        """Validate add_vlan and remove_vlan incoming parameters

        :param vlan_range: vlan range (10,20,30-40)
        :param port_range: list of port resource addresses ([192.168.1.1/0/34, 192.168.1.1/0/42])
        :param port_mode: switchport mode (access or trunk)
        """

        self.logger.info('Validate incoming parameters for vlan configuration:')
        if not port_range:
            raise Exception('CiscoHandlerBase: validate_vlan_methods_incoming_parameters ',
                            'Port list can\'t be empty.')

        if vlan_range == '' and port_mode == 'access':
            raise Exception('CiscoHandlerBase: validate_vlan_methods_incoming_parameters',
                            'Switchport type is Access, vlan id/range can\'t be empty.')

        if (',' in vlan_range or '-' in vlan_range) and port_mode == 'access':
            raise Exception('CiscoHandlerBase: validate_vlan_methods_incoming_parameters',
                            'Interface in Access mode, vlan range is not allowed, only one vlan can be assigned.')

    def get_port_name(self, port):
        """Get port name from port resource full address

        :param port: port resource full address (192.168.1.1/0/34)
        :return: port name (FastEthernet0/23)
        :rtype: string
        """

        if not port:
            err_msg = 'Failed to get port name.'
            self.logger.error(err_msg)
            raise Exception('Cisco OS: get_port_name', err_msg)

        temp_port_name = port.split('/')[-1]
        if 'port-channel' not in temp_port_name.lower():
            temp_port_name = temp_port_name.replace('-', '/')

        self.logger.info('Interface name validation OK, portname = {0}'.format(temp_port_name))
        return temp_port_name

    def configure_vlan_on_interface(self, session, commands_dict):
        """Configure vlan on specified interface/s

        :param commands_dict: dictionary of parameters
        :return: success message
        :rtype: string
        """

        commands_list = get_commands_list(commands_dict)

        current_config = session.send_command(
            'show running-config interface {0}'.format(commands_dict['configure_interface']))

        for line in current_config.splitlines():
            if re.search(r'^\s*switchport\s+', line):
                line_to_remove = re.sub(r'\s+\d+[-\d+,]+', '', line)
                if not line_to_remove:
                    line_to_remove = line
                commands_list.insert(1, 'no {0}'.format(line_to_remove.strip(' ')))

        expected_map = {'[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session: session.send_line('yes'),
                        '[\[\(][Yy]/[Nn][\)\]]': lambda session: session.send_line('y')}
        output = send_config_command_list(session, commands_list, expected_map=expected_map)

        if re.search(r'[Cc]ommand rejected.*', output):
            error = 'Command rejected'
            for line in output.splitlines():
                if line.lower().startswith('command rejected'):
                    error = line.strip(' \t\n\r')
            raise Exception('Cisco OS', 'Vlan configuration failed.\n{0}'.format(error))

        return 'Vlan configuration completed.'

    @staticmethod
    def configure_vlan(session, ordered_parameters_dict):
        """Configure vlan

        :param ordered_parameters_dict: dictionary of parameters
        :return: success message
        :rtype: string
        """

        commands_list = get_commands_list(ordered_parameters_dict)
        send_config_command_list(session, commands_list)

        return 'Vlan configuration completed.'

    @staticmethod
    def prepare_vlan_config_commands(vlan_range):
        vlan_config_actions = OrderedDict()
        vlan_config_actions['configure_vlan'] = vlan_range
        vlan_config_actions['state_active'] = []
        vlan_config_actions['no_shutdown'] = []
        return vlan_config_actions

    def prepare_interface_config_commands(self, port_name, port_mode, vlan_range, qnq):
        interface_config_actions = OrderedDict()
        interface_config_actions['configure_interface'] = port_name
        interface_config_actions['no_shutdown'] = []
        if self.supported_os and re.search(r"({0})".format("|".join(self.supported_os)), "NXOS"):
            interface_config_actions['switchport'] = []
        if 'trunk' in port_mode and vlan_range == '':
            interface_config_actions['switchport_mode_trunk'] = []
        elif 'trunk' in port_mode and vlan_range != '':
            interface_config_actions['switchport_mode_trunk'] = []
            interface_config_actions['trunk_allow_vlan'] = [vlan_range]
        elif 'access' in port_mode and vlan_range != '':
            if not qnq:
                self.logger.info('qnq is {0}'.format(qnq))
                interface_config_actions['switchport_mode_access'] = []
            interface_config_actions['access_allow_vlan'] = [vlan_range]

        return interface_config_actions
