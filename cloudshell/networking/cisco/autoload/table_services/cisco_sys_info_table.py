import re

from cloudshell.shell.flows.autoload.autoload_utils import get_device_name
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

    def fill_attributes(self, resource):
        """Get root element attributes.

        :type resource: cloudshell.shell_standards.autoload_generic_models.GenericResourceModel  # noqa: E501
        """
        self._logger.debug("Building Root started")

        resource.contact_name = self._snmp_v2_obj.get_system_contact()
        resource.system_name = self._snmp_v2_obj.get_system_name()
        resource.location = self._snmp_v2_obj.get_system_location()
        resource.os_version = self._get_device_os_version()
        vendor = self._get_vendor()
        resource.vendor = vendor

        raw_model = self._get_device_model()
        model = re.sub(rf"^{vendor}", "", raw_model, flags=re.IGNORECASE)
        resource.model = model.capitalize()
        resource.model_name = model.capitalize()
        resource.model_name = self._get_model_name(raw_model, vendor)

        self._logger.info("Building Root completed")

    def _get_model_name(self, model, vendor=None):
        result = model
        if self._device_model_map_path:
            result = (
                get_device_name(file_name=self._device_model_map_path, sys_obj_id=model)
                or model
            )
        if result == model and vendor and model.lower().startswith(vendor.lower()):
            result = f"{vendor.capitalize()} {model[len(vendor):].capitalize()}"
        return result
