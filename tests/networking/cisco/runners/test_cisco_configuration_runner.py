import time
from unittest import TestCase

from mock import MagicMock, patch

from cloudshell.networking.cisco.runners.cisco_configuration_runner import (
    CiscoConfigurationRunner,
)


class TestCiscoConfigurationRunner(TestCase):
    TEST_NAME = "resource_name"

    def setUp(self):
        self._logger = MagicMock()
        self._cli_handler = MagicMock()
        self._resource_config = MagicMock()
        self._resource_config.name = self.TEST_NAME
        self._handler = CiscoConfigurationRunner(
            logger=self._logger,
            cli_handler=self._cli_handler,
            resource_config=self._resource_config,
            api=MagicMock(),
        )

    def test_save(self):
        with patch(
            "cloudshell.networking.cisco.runners.cisco_configuration_runner.CiscoSaveFlow"
        ) as save_mock:
            config_type = "running"
            result = self._handler.save("tftp://10.10.10.10", "running", "")
            self.assertEqual(
                "{}-{}-{}".format(
                    self.TEST_NAME,
                    config_type,
                    time.strftime("%d%m%y-%H%M%S", time.localtime()),
                ),
                result,
            )
            save_mock.assert_called_once_with(
                cli_handler=self._cli_handler, logger=self._logger
            )

    def test_restore(self):
        with patch(
            "cloudshell.networking.cisco.runners.cisco_configuration_runner.CiscoRestoreFlow"
        ) as restore_mock:
            self._handler.restore("tftp://10.10.10.10", "running", "", "")
            restore_mock.assert_called_once_with(
                cli_handler=self._cli_handler, logger=self._logger
            )
