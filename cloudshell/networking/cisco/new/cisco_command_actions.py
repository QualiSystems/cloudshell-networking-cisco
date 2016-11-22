import re
from cloudshell.networking.cisco.command_templates.configuration_templates import COPY
from cloudshell.networking.devices.command_actions_interface import CommandActions


class CiscoCommandActions(CommandActions):
    def install_firmware(self, session, logger, path, vrf):
        pass

    def health_check(self, session, logger):
        pass

    def set_vlan_to_interface(self, session, logger, vlan_range, port_mode, port_name, qnq, c_tag):
        pass

    def reload(self, session, logger, timeout):
        pass

    def create_vlan(self, session, logger, vlan_range, port_mode, qnq, c_tag, action_map=None, error_map=None):
        session.send_command(CONFIGURE_VLAN.get_command(vlan_id=vlan_range.replace(' ', ''),
                                                        action_map=action_map,
                                                        error_map=error_map))
        session.send_command(STATE_ACTIVE.get_command(action_map=action_map, error_map=error_map))
        session.send_command(NO_SHUTDOWN.get_command(action_map=action_map, error_map=error_map))

    def run_custom_command(self, session, logger, command):
        pass

    def verify_vlan_removed(self, session, logger, vlan_range, port_name):
        pass

    def copy(self, session, logger, source, destination, vrf=None, action_map=None, error_map=None):
        output = session.send_command(
            **COPY.get_command(src=source, dst=destination, vrf=vrf, action_map=action_map, error_map=error_map))

        status_match = re.search(r'\d+ bytes copied|copied.*[\[\(].*[0-9]* bytes.*[\)\]]|[Cc]opy complete', output,
                                 re.IGNORECASE)
        if not status_match:
            match_error = re.search('%.*|TFTP put operation failed.*|sysmgr.*not supported.*\n', output, re.IGNORECASE)
            message = 'Copy Command failed. '
            if match_error:
                logger.error(message)
                message += re.sub('^%|\\n', '', match_error.group())
            else:
                error_match = re.search(r"error.*\n|fail.*\n", output, re.IGNORECASE)
                if error_match:
                    logger.error(message)
                    message += error_match.group()
            raise Exception('copy', message)

    def verify_firmware(self, session, logger):
        pass

    def remove_vlan_from_interface(self, session, logger, vlan_range, port_mode, port_name, qnq, c_tag):
        pass

    def override_startup(self, session, path, restore_method, configuration, vrf):
        pass

    def verify_vlan_added(self, session, logger):
        pass

    def override_running(self, session, path, restore_method, configuration, vrf):
        pass

    def verify_config_applied(self, session, logger):
        pass
