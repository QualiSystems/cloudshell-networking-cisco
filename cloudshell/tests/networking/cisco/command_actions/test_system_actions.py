from unittest import TestCase

from mock import MagicMock
from cloudshell.networking.cisco.command_actions.system_actions import SystemActions


class TestCiscoSystemActions(TestCase):
    TEST_RUNNING_CONFIG_SHORT_PATH = "running-config"
    TEST_RUNNING_CONFIG_FULL_PATH = "bootflash:/running-config"
    TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH = "tftp://localhost/running-config"
    TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH = "tftp://127.0.0.1/running-config"
    TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH = "ftp://user:pass@localhost/running-config"
    TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH = "ftp://user:pass@127.0.0.1/running-config"

    TEST_RESULT_TEXT_HOST = "(?!/)localhost(?!/)"
    TEST_RESULT_IP_HOST = "(?!/)127.0.0.1(?!/)"
    TEST_RESULT_PASSWORD = "[Pp]assword:"
    TEST_RESULT_SRC_FILE_NAME = "[\\[\\(].*running-config[\\)\\]]"
    TEST_RESULT_DST_FILE_NAME = "[\\[\\(]running-config[\\)\\]]"
    TEST_RESULT_FROM_REMOTE_DST_FILE_NAME = "(?!/)[\\[\\(]running-config[\\)\\]]"

    def setUp(self):
        self.system_action = SystemActions(cli_service=MagicMock(), logger=MagicMock())

    def test_prepare_action_map_tftp_text_path(self):
        short_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_SHORT_PATH,
                                                                      self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH)
        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_FULL_PATH,
                                                                     self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH)
        self.assertIsNotNone(full_path_action_map)

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH,
                                                                      self.TEST_RUNNING_CONFIG_SHORT_PATH)
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))

        full_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH,
                                                                     self.TEST_RUNNING_CONFIG_FULL_PATH)
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))

    def test_prepare_action_map_tftp_ip_path(self):
        short_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_SHORT_PATH,
                                                                      self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH)

        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_FULL_PATH,
                                                                     self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH)

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH,
                                                                      self.TEST_RUNNING_CONFIG_SHORT_PATH)
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))

        full_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH,
                                                                     self.TEST_RUNNING_CONFIG_FULL_PATH)
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))

    def test_prepare_action_map_ftp_text_path(self):
        short_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_SHORT_PATH,
                                                                      self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH)
        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_FULL_PATH,
                                                                     self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH)
        self.assertIsNotNone(full_path_action_map)

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH,
                                                                      self.TEST_RUNNING_CONFIG_SHORT_PATH)
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))

        full_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH,
                                                                     self.TEST_RUNNING_CONFIG_FULL_PATH)
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))

    def test_prepare_action_map_ftp_ip_path(self):
        short_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_SHORT_PATH,
                                                                      self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH)

        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_FULL_PATH,
                                                                     self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH)

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH,
                                                                      self.TEST_RUNNING_CONFIG_SHORT_PATH)
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))

        full_invert_path_map = self.system_action.prepare_action_map(self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH,
                                                                     self.TEST_RUNNING_CONFIG_FULL_PATH)
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME))
