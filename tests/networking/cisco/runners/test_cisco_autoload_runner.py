from unittest import TestCase

from mock import MagicMock, patch

from cloudshell.networking.cisco.runners.cisco_autoload_runner import (
    CiscoAutoloadRunner,
)


class TestCiscoAutoloadRunner(TestCase):
    def setUp(self):
        self._logger = MagicMock()
        self._snmp_handler = MagicMock()
        resource_config = MagicMock()
        self._handler = CiscoAutoloadRunner(
            logger=self._logger,
            snmp_handler=self._snmp_handler,
            resource_config=resource_config,
        )

    def test_discover(self):
        with patch(
            "cloudshell.networking.cisco.runners.cisco_autoload_runner"
            ".CiscoSnmpAutoloadFlow"
        ) as flow_mock:
            self._handler.discover()
            flow_mock.assert_called_once_with(self._snmp_handler, self._logger)
