__author__ = 'g8y3e'

class Resource:
    RESOURCE_TEMPLATE= '{0}^{1}^{2}^{3}|'
    RESOURCE_ATTRIBUTE_TEMPLATE = '{0}^{1}^{2}|'

    RESOURCES_MATRIX_HEADERS = ['Model', 'Name', 'Relative Address', 'Unique Identifier']
    ATTRIBUTES_MATRIX_HEADERS = ['Relative Address', 'Attribute Name', 'Attribute Value']

    ATTRIBUTE_NAMES = {'l2_protocol_type': 'L2 Protocol Type', 'type': 'Type', 'mac': 'MAC Address', 'mtu': 'MTU',
                       'bandwidth': 'Bandwidth', 'dly': 'DLY', 'encapsulation': 'Encapsulation',
                       'port_ip_v4': 'IPv4 Address', 'port_ip_v6': 'IPv6 Address', 'port_state': 'State',
                       'port_method': 'Method', 'port_status': 'Status', 'os_version': 'OS Version',
                       'release_version': 'Release Version', 'firmware_version': 'Firmware Version',
                       'serial_number': 'Serial Number', 'version': 'Version', 'protocol': 'Protocol',
                       'protocol_type': 'Protocol Type', 'mask': 'Subnet Mask', 'model': 'Model',
                       'contact': 'Contact Name', 'system_name': 'System Name', 'location': 'Location',
                       'vendor': 'Vendor', 'auto_negotiation': 'Auto Negotiation', 'duplex': 'Duplex',
                       'adjacent': 'Adjacent', 'hardware_rev': 'Hardware Revision', 'description': 'Port Description',
                       'associated_ports': 'Associated Ports'
                       }
    #'name': 'Port Name', 'module': 'Module Model', 'entPhysicalName': 'Port Name',

    def __init__(self):
        self._childs = {}
        self._info_data = None

    def toString(self, resource_template=RESOURCE_TEMPLATE, attribute_template=RESOURCE_ATTRIBUTE_TEMPLATE,
                 matrix_separator='$'):
        result_str = resource_template.format(*Resource.RESOURCES_MATRIX_HEADERS)

        for key, value in self._childs.iteritems():
            result_str += value.toResourceString(resource_template)

        result_str += matrix_separator
        #result_str += attribute_template.format(*Resource.ATTRIBUTES_MATRIX_HEADERS)

        for key, value in self._childs.iteritems():
            result_str += value.toAttributesString(attribute_template)

        return result_str

    def toResourceString(self, resource_template):
        result_str = ''

        if not self._info_data is None:
            if 'model' in self._info_data :
                result_str += resource_template.format(self._info_data['model'], self._info_data['name'],
                                                   self._info_data['relative_path'], '')

        for key, value in self._childs.iteritems():
            result_str += value.toResourceString(resource_template)

        return result_str

    def toAttributesString(self, attribute_template):
        result_str = ''
        if (self._info_data is not None) and 'attributes' in self._info_data:
            for key, value in self._info_data['attributes'].iteritems():
                key_name = key
                if key in Resource.ATTRIBUTE_NAMES:
                    key_name = Resource.ATTRIBUTE_NAMES[key]
                    if value is not None:
                        result_str += attribute_template.format(self._info_data['relative_path'], key_name,
                                                            value)

        for key, value in self._childs.iteritems():
            result_str += value.toAttributesString(attribute_template)

        return result_str

    def setInfo(self, info_data):
        self._info_data = info_data

    def addChild(self, child_path, path_separator, info):
        index = child_path.find(path_separator)

        key = child_path
        if index != -1:
            key = child_path[:index]

        resource = None
        if key in self._childs:
            resource = self._childs[key]
        else:
            resource = Resource()
            self._childs[key] = resource

        if index != -1:
            resource.addChild(child_path[index + 1:], path_separator, info)
        else:
            resource.setInfo(info)
