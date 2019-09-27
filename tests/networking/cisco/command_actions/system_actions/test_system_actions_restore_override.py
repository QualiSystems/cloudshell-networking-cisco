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

    def test_restore_override_success(self):
        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            cte_mock.return_value.execute_command.return_value = (
                system_actions_output.SUCCESS_OUTPUT_CONFIG_OVERRIDE
            )
            self.system_action.override_running(MagicMock(), MagicMock())

    def test_copy_error_opening_output(self):
        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            try:
                cte_mock.return_value.execute_command.return_value = (
                    system_actions_output.ERROR_OVERRIDE_RUNNING
                )
                self.system_action.override_running(MagicMock(), MagicMock())
            except Exception as e:
                self.assertIn("Copy Command failed.", e.args)

    def test_override_running_error_opening_output(self):
        with patch(
            "cloudshell.networking.cisco.command_actions.system_actions"
            ".CommandTemplateExecutor"
        ) as cte_mock:
            try:
                cte_mock.return_value.execute_command.return_value = (
                    system_actions_output.ERROR_ROLL_BACK
                )
                self.system_action.override_running(MagicMock(), MagicMock())
            except Exception as e:
                self.assertIn("Copy Command failed.", e.args)
