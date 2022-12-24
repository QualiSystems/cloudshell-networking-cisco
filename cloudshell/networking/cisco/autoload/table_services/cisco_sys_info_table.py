import re

from cloudshell.snmp.autoload.services.system_info_table import SnmpSystemInfo


class CiscoSnmpSystemInfo(SnmpSystemInfo):
    def _get_device_model(self):
        """Get device model from the SNMPv2 mib.

        :return: device model
        :rtype: str
        """
        result = super()._get_device_model()
        sys_descr = str(self._snmp_v2_obj.get_system_description())
        match_name = re.search(r"\bvios(_l2)*\b", sys_descr, re.IGNORECASE)
        if match_name:
            result = match_name.group().upper().replace("_", "-")
        result = re.sub("cevchassis", "", result, flags=re.IGNORECASE)
        return result.capitalize()
