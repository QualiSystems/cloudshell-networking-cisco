from cloudshell.shell.core.context.driver_context import AutoLoadResource
from cloudshell.networking.cisco.autoload.NetworkingAutoloadResourceAttributes import GenericResourceAttribute, \
    NetworkingStandardChassisAttributes, NetworkingStandardModuleAttributes, NetworkingStandardPortAttributes, \
    NetworkingStandardPortChannelAttributes, NetworkingStandardPowerPortAttributes


class GenericResource:
    def __init__(self, name='', model='', relative_path='', uniqe_id=None, **attributes_dict):
        self.name = name
        self.model = model
        self.relative_path = relative_path
        self.uniqe_id = uniqe_id
        if not hasattr(self, 'attributes_class'):
            self.attributes_class = GenericResourceAttribute
        self.attributes = self.attributes_class(self.relative_path, **attributes_dict)

    def get_autoload_resource_details(self):
        if self.model == '' or self.name == '' or self.relative_path == '':
            raise Exception('Cisco Generic SNMP Autoload', 'Resources details not found!')
        if self.uniqe_id:
            result = AutoLoadResource(self.model, self.name, self.relative_path, self.uniqe_id)
        else:
            result = AutoLoadResource(self.model, self.name, self.relative_path)
        return result

    def get_autoload_resource_attributes(self):
        return self.attributes.get_autoload_resource_attributes()




class Chassis(GenericResource):
    def __init__(self, name='', model='Generic Chassis', relative_path='', **attributes_dict):
        if name == '':
            name = 'Chassis {0}'.format(relative_path)
        self.attributes_class = NetworkingStandardChassisAttributes
        GenericResource.__init__(self, name, model, relative_path, **attributes_dict)


class PowerPort(GenericResource):
    def __init__(self, name='', model='Generic Power Port', relative_path='', **attributes_dict):
        self.attributes_class = NetworkingStandardPowerPortAttributes
        GenericResource.__init__(self, name, model, relative_path, **attributes_dict)


class Port(GenericResource):
    def __init__(self, name='', model='Generic Port', relative_path='', **attributes_dict):
        port_name = name.replace('/', '-').replace('\s+', '')
        self.attributes_class = NetworkingStandardPortAttributes
        GenericResource.__init__(self, port_name, model, relative_path, **attributes_dict)


class Module(GenericResource):
    def __init__(self, name='', model='Generic Module', relative_path='', **attributes_dict):
        self.attributes_class = NetworkingStandardModuleAttributes
        GenericResource.__init__(self, name, model, relative_path, **attributes_dict)


class PortChannel(GenericResource):
    def __init__(self, name='', model='Generic Port Channel', relative_path='', **attributes_dict):
        self.attributes_class = NetworkingStandardPortChannelAttributes
        GenericResource.__init__(self, name, model, relative_path, **attributes_dict)