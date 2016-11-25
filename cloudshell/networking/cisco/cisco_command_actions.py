from collections import OrderedDict
import re
from cloudshell.networking.cisco.command_templates.cisco_interface import CONFIGURE_INTERFACE, SHUTDOWN, \
    SWITCHPORT_MODE, \
    SWITCHPORT_ALLOW_VLAN, SHOW_RUNNING, NO, STATE_ACTIVE, CONFIGURE_VLAN, SHOW_VERSION, NO_SHUTDOWN
from cloudshell.networking.cisco.command_templates.configuration_templates import COPY, DEL, CONFIGURE_REPLACE, \
    SNMP_SERVER_COMMUNITY, NO_SNMP_SERVER_COMMUNITY


class CiscoCommandActions(object):
    def install_firmware(self, session, logger, path, vrf):
        pass

    def health_check(self, session, logger):
        pass

    def set_vlan_to_interface(self, config_session, logger, vlan_range, port_mode, port_name, qnq, c_tag,
                              action_map=None,
                              error_map=None):
        config_session.send_command(**CONFIGURE_INTERFACE.get_command(port_name=port_name))
        config_session.send_command(**NO_SHUTDOWN.get_command(action_map=action_map, error_map=error_map))
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

    def create_vlan(self, session, logger, vlan_range, action_map=None, error_map=None):
        session.send_command(**CONFIGURE_VLAN.get_command(vlan_id=vlan_range,
                                                          action_map=action_map,
                                                          error_map=error_map))
        session.send_command(**STATE_ACTIVE.get_command(action_map=action_map, error_map=error_map))
        session.send_command(**SHUTDOWN.get_command(no='', action_map=action_map, error_map=error_map))

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
        return session.send_command(
            **SHOW_RUNNING.get_command(port_name=port_name, action_map=action_map, error_map=error_map))

    def get_current_boot_config(self, session, action_map=None, error_map=None):
        return session.send_command(**SHOW_RUNNING.get_command(boot='', action_map=action_map, error_map=error_map))

    def get_current_os_version(self, session, action_map=None, error_map=None):
        return session.send_command(**SHOW_VERSION.get_command(action_map=action_map, error_map=error_map))

    def get_current_snmp_communities(self, session, action_map=None, error_map=None):
        return session.send_command(**SHOW_RUNNING.get_command(snmp='', action_map=action_map,
                                                               error_map=error_map))

    def clean_interface_switchport_config(self, config_session, logger, current_config, port_name, action_map=None,
                                          error_map=None):
        logger.debug("Start cleaning interface switchport configuration")
        config_session.send_command(**CONFIGURE_INTERFACE.get_command(port_name=port_name))
        for line in current_config.splitlines():
            if line.strip(" ").startswith('switchport '):
                config_session.send_command(
                    **NO.get_command(command=line.strip(' '), action_map=action_map, error_map=error_map))

        logger.debug("Completed cleaning interface switchport configuration")

    def remove_configuration_commands(self, session, config_to_remove, action_map=None, error_map=None):
        for line in config_to_remove.splitlines():
            if line.strip(" ").startswith('switchport '):
                session.send_command(
                    **NO.get_command(command=line.strip(' '), action_map=action_map, error_map=error_map))

    def delete_file(self, session, logger, path, action_map=None, error_map=None):
        session.send_command(**DEL.get_command(target=path, action_map=action_map, error_map=error_map))

    def verify_interface_configured(self, vlan_range, current_config):
        return str(vlan_range) in current_config

    def override_running(self, session, path, action_map=None, error_map=None):
        output = session.send_command(
            **CONFIGURE_REPLACE.get_command(path=path, action_map=action_map, error_map=error_map))
        match_error = re.search(r'[Ee]rror.*$', output)
        if match_error:
            error_str = match_error.group()
            raise Exception('CiscoConfigurationOperations', 'Configure replace completed with error: ' + error_str)

    def enable_snmp(self, session, snmp_community, action_map=None, error_map=None):
        session.send_command(**SNMP_SERVER_COMMUNITY.get_command(snmp_community=snmp_community,
                                                                 action_map=action_map, error_map=error_map))

    def disable_snmp(self, session, snmp_community, action_map=None, error_map=None):
        session.send_command(**NO_SNMP_SERVER_COMMUNITY.get_command(snmp_community=snmp_community,
                                                                    action_map=action_map, error_map=error_map))

    def get_port_name(self, logger, port):
        """Get port name from port resource full address
        :param port: port resource full address (192.168.1.1/0/34)
        :return: port name (FastEthernet0/23)
        :rtype: string
        """

        if not port:
            err_msg = 'Failed to get port name.'
            logger.error(err_msg)
            raise Exception('CiscoConnectivityOperations: get_port_name', err_msg)

        temp_port_name = port.split('/')[-1]
        if 'port-channel' not in temp_port_name.lower():
            temp_port_name = temp_port_name.replace('-', '/')

        logger.info('Interface name validation OK, portname = {0}'.format(temp_port_name))
        return temp_port_name
