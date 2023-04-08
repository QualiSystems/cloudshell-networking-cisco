import re
import time
from collections import OrderedDict

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.session.session_exceptions import (
    CommandExecutionException,
    ExpectedSessionException,
)

from cloudshell.networking.cisco.command_templates import configuration, firmware
from cloudshell.networking.cisco.errors.cisco_errors import CiscoConfigurationError


class SystemActions:
    USERNAME_PATTERN = r"(?!/)\b[Uu]ser(name)?\b"
    PASSWORD_PATTERN = r"((?:(?!:).)|^)\b[Pp]assword\b"
    HOSTNAME_PATTERN = r"(?!/){host}(?!/)\D*\s*$"
    DST_FILE_NAME_PATTERN = r"[\[\(].*{dst_file_name}[\)\]]"
    SRC_FILE_NAME_PATTERN = r"[\[\(]{src_file_name}[\)\]]"

    SUCCESS_COPY_PATTERN = (
        r"\d+ bytes copied|copied.*[\[\(].*[1-9][0-9]* bytes.*[\)\]]|"
        r"[Cc]opy complete|[\(\[]OK[\]\)]|updated\s*commit\s*database\s*\S*\s*\d+\s*sec"
    )

    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    @staticmethod
    def prepare_action_map(source_url_obj, destination_url_obj):
        dst_file_name = destination_url_obj.filename
        source_file_name = source_url_obj.filename
        action_map = OrderedDict()
        host = None

        action_map[
            SystemActions.DST_FILE_NAME_PATTERN.format(dst_file_name=dst_file_name)
        ] = lambda session, logger: session.send_line("", logger)

        action_map[
            SystemActions.SRC_FILE_NAME_PATTERN.format(src_file_name=source_file_name)
        ] = lambda session, logger: session.send_line("", logger)

        if hasattr(source_url_obj, "host"):
            host = source_url_obj.host
        elif hasattr(destination_url_obj, "host"):
            host = destination_url_obj.host
        password = source_url_obj.password or destination_url_obj.password
        username = source_url_obj.username or destination_url_obj.username

        if host:
            action_map[
                SystemActions.HOSTNAME_PATTERN.format(host=host)
            ] = lambda session, logger: session.send_line("", logger)
        if username:
            action_map[
                SystemActions.USERNAME_PATTERN
            ] = lambda session, logger: session.send_line(username, logger)

        if password:
            action_map[
                SystemActions.PASSWORD_PATTERN
            ] = lambda session, logger: session.send_line(password, logger)
        return action_map

    def copy(
        self,
        source,
        destination,
        vrf=None,
        action_map=None,
        error_map=None,
        timeout=180,
    ):
        """Copy file from device to tftp or vice versa.

        As well as copying inside devices filesystem.
        :param source: source file
        :param destination: destination file
        :param vrf: vrf management name
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :param timeout: session timeout
        :raise Exception:
        """
        if not vrf:
            vrf = None

        output = CommandTemplateExecutor(
            self._cli_service,
            configuration.COPY,
            action_map=action_map,
            error_map=error_map,
            timeout=timeout,
        ).execute_command(src=source, dst=destination, vrf=vrf)

        status_match = re.search(self.SUCCESS_COPY_PATTERN, output, re.IGNORECASE)

        if not status_match:
            match_error = re.search(
                r"%.*|TFTP put operation failed.*|sysmgr.*not supported.*\n",
                output,
                re.IGNORECASE,
            )
            message = "Copy Command failed. "
            if match_error:
                self._logger.error(message)
                message += re.sub(r"^%\s+|\\n|\s*at.*marker.*", "", match_error.group())
            else:
                error_match = re.search(r"error.*\n|fail.*\n", output, re.IGNORECASE)
                if error_match:
                    self._logger.error(message)
                    message += error_match.group()
            raise CiscoConfigurationError("Copy", message)

    def delete_file(self, path, action_map=None, error_map=None):
        """Delete file on the device.

        :param path: path to file
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        CommandTemplateExecutor(
            self._cli_service,
            configuration.DEL,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(target=path)

    def override_running(
        self,
        path,
        vrf=None,
        action_map=None,
        error_map=None,
        timeout=300,
        reconnect_timeout=1600,
    ):
        """Override running-config.

        :param path: relative path to the file on the remote host
            tftp://server/sourcefile
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
        i.e. handles Invalid Commands errors
        :raise Exception:
        """
        try:
            output = CommandTemplateExecutor(
                self._cli_service,
                configuration.CONFIGURE_REPLACE,
                action_map=action_map,
                error_map=error_map,
                timeout=timeout,
                check_action_loop_detector=False,
            ).execute_command(path=path, vrf=vrf)
            match_error = re.search(r"[Ee]rror.*", output, flags=re.DOTALL)
            if match_error:
                error_str = match_error.group()
                raise CommandExecutionException(
                    "Override_Running",
                    "Configure replace completed with error: " + error_str,
                )
        except ExpectedSessionException as e:
            self._logger.warning(e.args)
            if isinstance(e, CommandExecutionException):
                raise
            self._cli_service.reconnect(reconnect_timeout)

    def write_erase(self, action_map=None, error_map=None):
        """Erase startup configuration.

        :param action_map:
        :param error_map:
        """
        CommandTemplateExecutor(
            self._cli_service,
            configuration.WRITE_ERASE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def reload_device(self, timeout, action_map=None, error_map=None):
        """Reload device.

        :param timeout: session reconnect timeout
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        try:
            redundancy_reload = CommandTemplateExecutor(
                self._cli_service,
                configuration.REDUNDANCY_PEER_SHELF,
                action_map=action_map,
                error_map=error_map,
            ).execute_command()
            if re.search(
                r"[Ii]nvalid\s*([Ii]nput|[Cc]ommand)", redundancy_reload, re.IGNORECASE
            ):
                CommandTemplateExecutor(
                    self._cli_service,
                    configuration.RELOAD,
                    action_map=action_map,
                    error_map=error_map,
                ).execute_command()
            time.sleep(60)
        except Exception:
            self._logger.info("Device rebooted, starting reconnect")
        self._cli_service.reconnect(timeout)

    def get_flash_folders_list(self):
        output = CommandTemplateExecutor(
            self._cli_service, configuration.SHOW_FILE_SYSTEMS
        ).execute_command()

        match_dir = re.findall(
            r"(bootflash:|bootdisk:|flash-\d+\S+)", output, re.MULTILINE
        )
        if match_dir:
            return match_dir

    def reload_device_via_console(self, timeout=500, action_map=None, error_map=None):
        """Reload device.

        :param timeout: session reconnect timeout
        """
        CommandTemplateExecutor(
            self._cli_service,
            configuration.CONSOLE_RELOAD,
            action_map=action_map,
            error_map=error_map,
            timeout=timeout,
        ).execute_command()
        self._cli_service.session.on_session_start(
            self._cli_service.session, self._logger
        )

    def get_current_boot_config(self, action_map=None, error_map=None):
        """Retrieve current boot configuration.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return:
        """
        return CommandTemplateExecutor(
            self._cli_service,
            firmware.SHOW_RUNNING,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def get_current_os_version(self, action_map=None, error_map=None):
        """Retrieve os version.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return:
        """
        return CommandTemplateExecutor(
            self._cli_service,
            firmware.SHOW_VERSION,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def get_current_boot_image(self):
        current_firmware = []
        for line in self.get_current_boot_config().splitlines():
            if ".bin" in line:
                current_firmware.append(line.strip(" "))

        return current_firmware

    def shutdown(self):
        """Shutdown the system."""
        pass


class FirmwareActions:
    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def add_boot_config_file(self, firmware_file_name):
        """Set boot firmware file.

        :param firmware_file_name: firmware file nameSet boot firmware file.

        :param firmware_file_name: firmware file name
        """
        CommandTemplateExecutor(
            self._cli_service, firmware.BOOT_SYSTEM_FILE
        ).execute_command(firmware_file_name=firmware_file_name)
        current_reg_config = CommandTemplateExecutor(
            self._cli_service, configuration.SHOW_VERSION_WITH_FILTERS
        ).execute_command(do="", filter="0x")
        if "0x2102" not in current_reg_config:
            CommandTemplateExecutor(
                self._cli_service, firmware.CONFIG_REG
            ).execute_command()

    def add_boot_config(self, boot_config_line):
        """Set boot firmware file.

        :param boot_config_line: firmware file name
        """
        self._cli_service.send_command(boot_config_line)

    def clean_boot_config(self, config_line_to_remove, action_map=None, error_map=None):
        """Remove current boot from device.

        :param config_line_to_remove: current boot configuration
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        self._logger.debug("Start cleaning boot configuration")

        self._logger.info(f"Removing '{config_line_to_remove}' boot config line")
        CommandTemplateExecutor(
            self._cli_service,
            configuration.NO,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(command=config_line_to_remove.strip(" "))

        self._logger.debug("Completed cleaning boot configuration")
