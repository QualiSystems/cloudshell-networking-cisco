from unittest import TestCase
from mock import MagicMock
import re
from cloudshell.networking.cisco.cisco_send_command_operations import CiscoHandlerBase


class TestCiscoHandlerBase(TestCase):
    def _get_handler(self):
        self.cli = MagicMock()
        self.snmp = MagicMock()
        self.api = MagicMock()
        self.logger = MagicMock()
        return CiscoHandlerBase(cli=self.cli, logger=self.logger, api=self.api, snmp=self.snmp,
                                resource_name='resource_name')

    def test_apply_connectivity_changes_validates_request_parameter(self):
        request = """{
        "driverRequest" : {
            "actions" : [{
                    "connectionId" : "0b0f37df-0f70-4a8a-bd7b-fd21e5fbc23d",
                    "connectionParams" : {
                        "vlanId" : "435",
                        "mode" : "Access",
                        "vlanServiceAttributes" : [{
                                "attributeName" : "QnQ",
                                "attributeValue" : "False",
                                "type" : "vlanServiceAttribute"
                            }, {
                                "attributeName" : "CTag",
                                "attributeValue" : "",
                                "type" : "vlanServiceAttribute"
                            }, {
                                "attributeName" : "Isolation Level",
                                "attributeValue" : "Shared",
                                "type" : "vlanServiceAttribute"
                            }, {
                                "attributeName" : "Access Mode",
                                "attributeValue" : "Access",
                                "type" : "vlanServiceAttribute"
                            }, {
                                "attributeName" : "VLAN ID",
                                "attributeValue" : "435",
                                "type" : "vlanServiceAttribute"
                            }, {
                                "attributeName" : "Pool Name",
                                "attributeValue" : "",
                                "type" : "vlanServiceAttribute"
                            }, {
                                "attributeName" : "Virtual Network",
                                "attributeValue" : "435",
                                "type" : "vlanServiceAttribute"
                            }
                        ],
                        "type" : "setVlanParameter"
                    },
                    "connectorAttributes" : [],
                    "actionId" : "0b0f37df-0f70-4a8a-bd7b-fd21e5fbc23d_5dded658-3389-466a-a479-4b97a3c17ebd",
                    "actionTarget" : {
                        "fullName" : "sw9003-vpp-10-3.cisco.com/port-channel2",
                        "fullAddress" : "10.89.143.226/PC2",
                        "type" : "actionTarget"
                    },
                    "customActionAttributes" : [],
                    "type" : "setVlan"
                }
            ]
        }
        }"""
        handler = self._get_handler()
        handler.get_port_name = MagicMock(return_value='port-channel2')
        handler.apply_connectivity_changes(request)
