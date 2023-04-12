from unittest import TestCase

from cloudshell.shell.flows.utils.url import BasicLocalUrl, RemoteURL

from cloudshell.networking.cisco.command_actions.system_actions import SystemActions

try:
    from unittest.mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock


class TestCiscoSystemActions(TestCase):
    TEST_RUNNING_CONFIG_SHORT_PATH = BasicLocalUrl.from_str("running-config", "/")
    TEST_RUNNING_CONFIG_FULL_PATH = BasicLocalUrl.from_str("bootflash:/running-config")
    TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH = RemoteURL.from_str(
        "tftp://localhost/running-config"
    )
    TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH = RemoteURL.from_str(
        "tftp://127.0.0.1/running-config"
    )
    TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH = RemoteURL.from_str(
        "ftp://user:pass@localhost/running-config"
    )
    TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH = RemoteURL.from_str(
        "ftp://user:pass@127.0.0.1/running-config"
    )

    TEST_RESULT_TEXT_HOST = SystemActions.HOSTNAME_PATTERN.format(host="localhost")
    TEST_RESULT_IP_HOST = SystemActions.HOSTNAME_PATTERN.format(host="127.0.0.1")
    TEST_RESULT_PASSWORD = SystemActions.PASSWORD_PATTERN
    TEST_RESULT_SRC_FILE_NAME = SystemActions.SRC_FILE_NAME_PATTERN.format(
        src_file_name="running-config"
    )
    TEST_RESULT_DST_FILE_NAME = SystemActions.DST_FILE_NAME_PATTERN.format(
        dst_file_name="running-config"
    )
    TEST_RESULT_FROM_REMOTE_DST_FILE_NAME = SystemActions.DST_FILE_NAME_PATTERN.format(
        dst_file_name="running-config"
    )

    def setUp(self):
        self.system_action = SystemActions(cli_service=MagicMock(), logger=MagicMock())

    def test_prepare_action_map_tftp_text_path(self):
        short_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH,
        )
        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_FULL_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH,
        )
        self.assertIsNotNone(full_path_action_map)

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH,
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
        )
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(
            short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )

        full_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_TEXT_PATH,
            self.TEST_RUNNING_CONFIG_FULL_PATH,
        )
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(
            full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )

    def test_prepare_action_map_tftp_ip_path(self):
        short_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH,
        )

        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_FULL_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH,
        )

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH,
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
        )
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(
            short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )

        full_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_TFTP_IP_PATH,
            self.TEST_RUNNING_CONFIG_FULL_PATH,
        )
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(
            full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )

    def test_prepare_action_map_ftp_text_path(self):
        short_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH,
        )
        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_FULL_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH,
        )
        self.assertIsNotNone(full_path_action_map)

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH,
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
        )
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(
            short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )

        full_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_TEXT_PATH,
            self.TEST_RUNNING_CONFIG_FULL_PATH,
        )
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_TEXT_HOST))
        self.assertIsNotNone(
            full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )

    def test_prepare_action_map_ftp_ip_path(self):
        short_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH,
        )

        self.assertIsNotNone(short_path_action_map)
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(short_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        full_path_action_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_FULL_PATH,
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH,
        )

        self.assertIsNotNone(full_path_action_map)
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_PASSWORD))

        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_SRC_FILE_NAME))
        self.assertIsNotNone(full_path_action_map.get(self.TEST_RESULT_DST_FILE_NAME))

        short_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH,
            self.TEST_RUNNING_CONFIG_SHORT_PATH,
        )
        self.assertIsNotNone(short_invert_path_map)
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(short_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(
            short_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )

        full_invert_path_map = self.system_action.prepare_action_map(
            self.TEST_RUNNING_CONFIG_REMOTE_FTP_IP_PATH,
            self.TEST_RUNNING_CONFIG_FULL_PATH,
        )
        self.assertIsNotNone(full_invert_path_map)
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_IP_HOST))
        self.assertIsNotNone(full_invert_path_map.get(self.TEST_RESULT_PASSWORD))
        self.assertIsNotNone(
            full_invert_path_map.get(self.TEST_RESULT_FROM_REMOTE_DST_FILE_NAME)
        )
