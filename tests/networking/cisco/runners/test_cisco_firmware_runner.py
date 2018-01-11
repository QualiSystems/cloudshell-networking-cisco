from unittest import TestCase

from mock import MagicMock, patch

from cloudshell.networking.cisco.runners.cisco_firmware_runner import CiscoFirmwareRunner


class TestCiscoConfigurationRunner(TestCase):

    def setUp(self):
        self._logger = MagicMock()
        self._cli_handler = MagicMock()
        self._handler = CiscoFirmwareRunner(logger=self._logger, cli_handler=self._cli_handler)

    def test_runs_firmware_flow(self):
        with patch("cloudshell.networking.cisco.runners.cisco_firmware_runner.CiscoLoadFirmwareFlow") as flow_mock:
            self._handler.load_firmware("tftp://10.10.10.10/qs_fw.bin")
            flow_mock.assert_called_once_with(self._cli_handler, self._logger)
