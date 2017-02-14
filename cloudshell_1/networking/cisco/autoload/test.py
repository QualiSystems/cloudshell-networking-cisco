#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging

from cloudshell.snmp.quali_snmp import QualiSnmp, QualiMibTable
from cloudshell.snmp.quali_snmp_cached import QualiSnmpCached
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters

from cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload


HOST = "172.29.168.7"
COMMUNITY = "public"
SUPPORTED_OS = ["CAT[ -]?OS", "IOS[ -]?X?[E]?"]


def snmp_handler():
    snmp_param = SNMPV2Parameters(ip=HOST, snmp_community=COMMUNITY)
    return QualiSnmpCached(snmp_parameters=snmp_param, logger=logging)


if __name__ == "__main__":
    # result1 = snmp_handler().walk(('ENTITY-MIB', 'entPhysicalTable'))
    # result = snmp_handler().walk(('ENTITY-MIB', 'entPhysicalTable'))

    # for index in snmp_handler().get_table('ENTITY-MIB', 'entPhysicalParentRelPos'):
    #     print index
    result_dict = QualiMibTable('entPhysicalTable')

    autoload = CiscoGenericSNMPAutoload(snmp_handler=snmp_handler(),
                                        shell_name="CiscoIOSShell",
                                        shell_type="CS_Switch",
                                        resource_name="CiscoTest",
                                        logger=logging).discover(supported_os=SUPPORTED_OS)

    print "OK"
