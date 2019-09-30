from unittest import TestCase

from cloudshell.networking.cisco.command_actions.system_actions import SystemActions

from tests.networking.cisco.command_actions.system_actions import system_actions_output

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCiscoSystemActionsCopy(TestCase):
    def setUp(self):
        self.system_action = SystemActions(cli_service=MagicMock(), logger=MagicMock())

    def test_copy_success(self):
        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            cte_mock.return_value.execute_command.return_value = (
                system_actions_output.SUCCESS_OUTPUT_IOS
            )
            self.system_action.copy(MagicMock(), MagicMock())

        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            cte_mock.return_value.execute_command.return_value = (
                system_actions_output.SUCCESS_OUTPUT
            )
            self.system_action.copy(MagicMock(), MagicMock())

        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            cte_mock.return_value.execute_command.return_value = (
                system_actions_output.TEST_COPY_OUTPUT
            )
            self.system_action.copy(MagicMock(), MagicMock())

    def test_copy_error_opening_file(self):
        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            try:
                cte_mock.return_value.execute_command.return_value = (
                    system_actions_output.ERROR_OPENING_OUTPUT
                )
                self.system_action.copy(MagicMock(), MagicMock())
            except Exception as e:
                self.assertIn(
                    "Copy Command failed. "
                    "%Error opening tftp://10.10.10.10/ASR1004-2-running-100516-084841 "
                    "(Timed out)",
                    e.args,
                )

    def test_copy_error_access_violation(self):
        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            try:
                cte_mock.return_value.execute_command.return_value = (
                    system_actions_output.ERROR_ACCESS_VIOLATION
                )
                self.system_action.copy(MagicMock(), MagicMock())
            except Exception as e:
                self.assertIn(
                    "Copy Command failed. "
                    "TFTP put operation failed:Access violation",
                    e.args,
                )

    def test_copy_error(self):
        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            cte_mock.return_value.execute_command.return_value = (
                system_actions_output.SUCCESS_OUTPUT
            )
            self.system_action.copy(MagicMock(), MagicMock())
