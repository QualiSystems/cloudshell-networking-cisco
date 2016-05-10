from cloudshell.shell.core.context.driver_context import AutoLoadAttribute

class ResourceAttribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class GenericResourceAttribute:
    def __init__(self, relative_path, kwargs=None):
        self.relative_path = relative_path

    def get_autoload_resource_attributes(self):
        """

        :param relative_path:
        :param dict_data:
        :return:
        """

        result = []
        attributes_dict = self.__dict__.copy()
        attributes_dict.pop('relative_path')
        for attribute in attributes_dict.values():
            result.append(AutoLoadAttribute(relative_address=self.relative_path,
                                            attribute_name=attribute.name,
                                            attribute_value=attribute.value))
        return result


class NetworkingStandardRootAttributes(GenericResourceAttribute):
    def __init__(self, relative_path='', model='', vendor='Cisco', system_name='', location='',
                 contact='', version=''):
        GenericResourceAttribute.__init__(self, relative_path)
        self.vendor = ResourceAttribute('Vendor', vendor)
        self.system_name = ResourceAttribute('System Name', system_name)
        self.location = ResourceAttribute('Location', location)
        self.contact = ResourceAttribute('Contact Name', contact)
        self.version = ResourceAttribute('OS Version', version)
        self.model = ResourceAttribute('Model', model)

class NetworkingStandardChassisAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, serial_number='', chassis_model=''):
        GenericResourceAttribute.__init__(self, relative_path)
        self.serial_number = ResourceAttribute('Serial Number', serial_number)
        self.model = ResourceAttribute('Model', chassis_model)

class NetworkingStandardModuleAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, serial_number='', module_model='', version=''):
        GenericResourceAttribute.__init__(self, relative_path)
        self.serial_number = ResourceAttribute('Serial Number', serial_number)
        self.module_model = ResourceAttribute('Model', module_model)
        self.version = ResourceAttribute('Version', version)

class NetworkingStandardPortAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, protocol_type='Transparent', description='', l2_protocol_type='ethernet', mac='',
                 mtu=0, bandwidth=0, adjacent='', ipv4_address='', ipv6_address='', duplex='', auto_negotiation=''):
        GenericResourceAttribute.__init__(self, relative_path)
        self.protocol_type = ResourceAttribute('Protocol Type', protocol_type)
        self.port_description = ResourceAttribute('Port Description', description)
        self.l2_protocol_type = ResourceAttribute('L2 Protocol Type', l2_protocol_type)
        self.mac = ResourceAttribute('MAC Address', mac)
        self.mtu = ResourceAttribute('MTU', mtu)
        self.duplex = ResourceAttribute('Duplex', duplex)
        self.auto_negotiation = ResourceAttribute('Auto Negotiation', auto_negotiation)
        self.bandwidth = ResourceAttribute('Bandwidth', bandwidth)
        self.adjacent = ResourceAttribute('Adjacent', adjacent)
        self.ipv4_address = ResourceAttribute('IPv4 Address', ipv4_address)
        self.ipv6_address = ResourceAttribute('IPv6 Address', ipv6_address)

class NetworkingStandardPortChannelAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, protocol_type='Transparent', description='', associated_ports='',
                 ipv4_address='', ipv6_address=''):
        GenericResourceAttribute.__init__(self, relative_path)
        self.protocol_type = ResourceAttribute('Protocol Type', protocol_type)
        self.description = ResourceAttribute('Port Description', description)
        self.associated_ports = ResourceAttribute('Associated Ports', associated_ports)
        self.ipv4_address = ResourceAttribute('IPv4 Address', ipv4_address)
        self.ipv6_address = ResourceAttribute('IPv6 Address', ipv6_address)

class NetworkingStandardPowerPortAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, serial_number='', model='', version='', description=''):
        GenericResourceAttribute.__init__(self, relative_path)
        self.serial_number = ResourceAttribute('Serial Number', serial_number)
        self.model = ResourceAttribute('Model', model)
        self.version = ResourceAttribute('Version', version)
        self.description = ResourceAttribute('Port Description', description)



