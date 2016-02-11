__author__ = 'g8y3e'

from cisco.common.interfaces.interface_base import *

class CiscoInterface(InterfaceBase):
    __metaclass__ = ABCMeta

    COMMANDS_TEMPLATE = {
        'configure_interface': CommandTemplate('interface {0}', r'\w+\s*[0-9/]+',
                                               'Interface name is incorrect!')
    }

    @abstractmethod
    def get_commands_list(self, **kwargs):
        prepared_commands = []

        if not 'configure_interface' in kwargs:
            raise Exception('Need to set configure_interface parameter!')

        command_template = InterfaceBase.COMMANDS_TEMPLATE['configure_interface']
        prepared_commands.append(ParametersService.getValidateList(command_template, [kwargs['configure_interface']]))

        return prepared_commands