from unittest import TestCase

from cloudshell.networking.cisco.flows.cisco_load_firmware_flow import (
    CiscoLoadFirmwareFlow,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoLoadFirmwareFlow(TestCase):
    def setUp(self):
        self.firmware_flow = CiscoLoadFirmwareFlow(MagicMock(), MagicMock())

    @patch("cloudshell.networking.cisco.flows.cisco_load_firmware_flow.SystemActions")
    def test_execute_flow(self, sys_actions_mock):
        sys_actions_mock.return_value.get_current_boot_config.side_effect = [
            "filename.bin",
            "filename.bin",
        ]
        self.firmware_flow.load_firmware("filename.bin", "")

        sys_actions_mock.return_value.get_flash_folders_list.assert_called_once()
        sys_actions_mock.return_value.get_current_boot_image.assert_called()
        sys_actions_mock.return_value.copy.assert_called_once()
        sys_actions_mock.return_value.get_current_boot_config.assert_called_once()

    @patch("cloudshell.networking.cisco.flows.cisco_load_firmware_flow.FirmwareActions")
    def test_apply_firmware(self, fw_actions_mock):
        old_firmware = "flash:/oldfirmware.bin"
        new_firmware = "flash:/filename.bin"
        self.firmware_flow._apply_firmware(
            enable_session=MagicMock(),
            current_boot=[old_firmware],
            firmware_dst_path=new_firmware,
        )

        fw_actions_mock.return_value.clean_boot_config.assert_called_once()
        fw_actions_mock.return_value.add_boot_config_file.assert_called_once_with(
            new_firmware
        )
        fw_actions_mock.return_value.add_boot_config.assert_called_once_with(
            old_firmware
        )
