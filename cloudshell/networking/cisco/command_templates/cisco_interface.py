__author__ = 'g8y3e'

from abc import ABCMeta
from abc import abstractmethod

from cloudshell.networking.parameters_service.command_template import CommandTemplate
from cloudshell.networking.parameters_service.parameters_service import ParametersService
from cloudshell.networking.command_template_base import InterfaceBase


class CiscoInterface(InterfaceBase):
    __metaclass__ = ABCMeta

    COMMANDS_TEMPLATE = {
        'configure_interface': CommandTemplate('interface {0}', r'[\w-]+\s*[0-9/]+',
                                               'Interface name is incorrect!')
    }

    @abstractmethod
    def get_commands_list(self, **kwargs):
        prepared_commands = []

        if 'configure_interface' not in kwargs:
            raise Exception('Need to set configure_interface parameter!')

        command_template = CiscoInterface.COMMANDS_TEMPLATE['configure_interface']
        prepared_commands.append(ParametersService.get_validate_list(command_template, [kwargs['configure_interface']]))

        return prepared_commands