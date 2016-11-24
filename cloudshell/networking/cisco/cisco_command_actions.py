from collections import OrderedDict
import re
from cloudshell.networking.cisco.command_templates.cisco_interface import CONFIGURE_INTERFACE, SHUTDOWN, \
    SWITCHPORT_MODE, \
    SWITCHPORT_ALLOW_VLAN, SHOW_RUNNING, NO, STATE_ACTIVE, CONFIGURE_VLAN, DO_SHOW_RUNNING
from cloudshell.networking.cisco.command_templates.configuration_templates import COPY, DEL, CONFIGURE_REPLACE


class CiscoCommandActions():
    def install_firmware(self, session, logger, path, vrf):
        pass

    def health_check(self, session, logger):
        pass

    def set_vlan_to_interface(self, config_session, logger, vlan_range, port_mode, port_name, qnq, c_tag,
                              action_map=None,
                              error_map=None):
        # interface_config_actions = OrderedDict()
        # interface_config_actions['configure_interface'] = port_name
        # interface_config_actions['no_shutdown'] = []
        # if self.supported_os and re.search(r"({0})".format("|".join(self.supported_os)), "NXOS"):
        #     interface_config_actions['switchport'] = []
        # if 'trunk' in port_mode and vlan_range == '':
        #     interface_config_actions['switchport_mode_trunk'] = []
        # elif 'trunk' in port_mode and vlan_range != '':
        #     interface_config_actions['switchport_mode_trunk'] = []
        #     interface_config_actions['trunk_allow_vlan'] = [vlan_range]
        # elif 'access' in port_mode and vlan_range != '':
        #     if not qnq:
        #         self.logger.info('qnq is {0}'.format(qnq))
        #         interface_config_actions['switchport_mode_access'] = []
        #     interface_config_actions['access_allow_vlan'] = [vlan_range]
        # self.logger.info('Finished preparing interface configuration commands')
        config_session.send_command(**CONFIGURE_INTERFACE.get_command(port_name=port_name))
        config_session.send_command(**SHUTDOWN.get_command(no='', action_map=action_map, error_map=error_map))
        if qnq:
            port_mode = 'dot1q-tunnel'
        config_session.send_command(**SWITCHPORT_MODE.get_command(port_mode=port_mode, action_map=action_map,
                                                                  error_map=error_map))
        if 'trunk' not in port_mode:
            config_session.send_command(**SWITCHPORT_ALLOW_VLAN.get_command(port_mode_access='',
                                                                            vlan_range=vlan_range,
                                                                            action_map=action_map,
                                                                            error_map=error_map))
        else:
            config_session.send_command(**SWITCHPORT_ALLOW_VLAN.get_command(port_mode_trunk='',
                                                                            vlan_range=vlan_range,
                                                                            action_map=action_map,
                                                                            error_map=error_map))

    def reload(self, session, logger, timeout):
        pass

    def create_vlan(self, session, logger, vlan_range, port_mode, qnq, c_tag, action_map=None, error_map=None):
        session.send_command(CONFIGURE_VLAN.get_command(vlan_id=vlan_range.replace(' ', ''),
                                                        action_map=action_map,
                                                        error_map=error_map))
        session.send_command(STATE_ACTIVE.get_command(action_map=action_map, error_map=error_map))
        session.send_command(SHUTDOWN.get_command(no='', action_map=action_map, error_map=error_map))

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
            raise Exception(self.__class__.__name__, message)

    def get_current_interface_config(self, session, logger, port_name, action_map=None, error_map=None):
        return session.send_command(**SHOW_RUNNING(port_name=port_name, action_map=action_map,
                                                   error_map=error_map))

    def clean_interface_switchport_config(self, config_session, logger, current_config, port_name, action_map=None,
                                          error_map=None):
        logger.debug("Start cleaning interface switchport configuration")
        config_session.send_command(**CONFIGURE_INTERFACE.get_command(port_name=port_name))
        for line in current_config.splitlines():
            if line.strip(" ").startswith('switchport '):
                config_session.send_command(**NO(command=line.strip(' '), action_map=action_map, error_map=error_map))

        logger.debug("Completed cleaning interface switchport configuration")

    def delete_file(self, session, logger, path, action_map=None, error_map=None):
        session.send_command(**DEL.get_command(tarfget=path, action_map=action_map, error_map=error_map))

    def verify_interface_configured(self, vlan_range, current_config):
        return vlan_range not in current_config

    def override_running(self, session, path, vrf, action_map=None, error_map=None):
        session.send_command(**CONFIGURE_REPLACE(path=path, action_map=action_map, error_map))
