#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.networking.cisco.autoload.cisco_if_table import CiscoIfTable


class CiscoGenericSNMPAutoload(GenericSNMPAutoload):
    @property
    def if_table_service(self):
        if not self._if_table:
            self._if_table = CiscoIfTable(
                snmp_handler=self.snmp_handler, logger=self.logger
            )

        return self._if_table
