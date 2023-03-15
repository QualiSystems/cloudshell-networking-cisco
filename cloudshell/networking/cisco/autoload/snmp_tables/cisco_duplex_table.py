from functools import lru_cache

from cloudshell.networking.cisco.autoload.constants.snmp_constants import (
    CISCO_STACK_DUPLEX,
    CISCO_STACK_DUPLEX_ID,
)


class CiscoSnmpStackTable:
    def __init__(self, snmp_handler, logger):
        self._snmp_handler = snmp_handler
        self._logger = logger
        self._data = None

    @property
    @lru_cache()
    def get_table(self):
        if self._data is None:
            data = self._snmp_handler.get_multiple_columns(
                [CISCO_STACK_DUPLEX_ID, CISCO_STACK_DUPLEX]
            )
            self._data = {
                str(data.get(CISCO_STACK_DUPLEX_ID.object_name, "")): str(
                    data.get(CISCO_STACK_DUPLEX.object_name, "")
                ).replace("'", "")
                for key, data in data.items()
            }
        return self._data

    def get(self, index):
        return self.get_table.get(index, "")
