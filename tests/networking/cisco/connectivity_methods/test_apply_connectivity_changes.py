from unittest import TestCase

from mock import MagicMock
from cloudshell.devices.standards.networking.configuration_attributes_structure import \
    create_networking_resource_from_context

from cloudshell.networking.cisco.runners.cisco_connectivity_runner import CiscoConnectivityRunner
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails


class TestCiscoConnectivityOperations(TestCase):
    def _get_handler(self):
        self.cli = MagicMock()
        self.snmp = MagicMock()
        self.api = MagicMock()
        self.logger = MagicMock()
        context = ResourceCommandContext()
        context.resource = ResourceContextDetails()
        context.resource.name = 'resource_name'
        context.reservation = ReservationContextDetails()
        context.reservation.reservation_id = 'c3b410cb-70bd-4437-ae32-15ea17c33a74'
        context.resource.attributes = dict()
        context.resource.attributes['CLI Connection Type'] = 'Telnet'
        context.resource.attributes['Sessions Concurrency Limit'] = '1'
        supported_os = ["CAT[ -]?OS", "IOS[ -]?X?[ER]?"]
        resource_config = create_networking_resource_from_context("", ["supported_os"], context)
        return CiscoConnectivityRunner(cli=self.cli, logger=self.logger, api=self.api,
                                       resource_config=resource_config)

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
        # handler.apply_connectivity_changes(request)
