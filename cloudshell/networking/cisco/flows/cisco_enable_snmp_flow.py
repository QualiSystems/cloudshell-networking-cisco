#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.networking.cisco.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters


class CiscoEnableSnmpFlow(EnableSnmpFlow):
    DEFAULT_SNMP_VIEW = "quali_snmp_view"
    DEFAULT_SNMP_GROUP = "quali_snmp_group"
    SNMP_AUTH_MAP = {v: k for k, v in SNMPV3Parameters.AUTH_PROTOCOL_MAP.iteritems()}
    SNMP_PRIV_MAP = {v: k for k, v in SNMPV3Parameters.PRIV_PROTOCOL_MAP.iteritems()}

    def __init__(self, cli_handler, logger, create_group=True):
        """
        Enable snmp flow
        :param cli_handler:
        :param logger:
        :return:
        """
        super(CiscoEnableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler
        self._create_group = create_group

    def execute_flow(self, snmp_parameters):
        if hasattr(snmp_parameters, "snmp_community") and not snmp_parameters.snmp_community:
            message = 'SNMP community cannot be empty'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

        read_only_community = True

        if isinstance(snmp_parameters, SNMPV2WriteParameters):
            read_only_community = False

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    current_snmp_user = snmp_actions.get_current_snmp_user()
                    if snmp_parameters.snmp_user not in current_snmp_user:
                        self._validate_snmp_v3_params(snmp_parameters)
                        if self._create_group:
                            current_snmp_config = snmp_actions.get_current_snmp_config()
                            if "snmp-server view {}".format(self.DEFAULT_SNMP_VIEW) not in current_snmp_config:
                                snmp_actions.enable_snmp_view(snmp_view=self.DEFAULT_SNMP_VIEW)
                            if "snmp-server group {}".format(self.DEFAULT_SNMP_GROUP) not in current_snmp_config:
                                snmp_actions.enable_snmp_group(snmp_group=self.DEFAULT_SNMP_GROUP,
                                                               snmp_view=self.DEFAULT_SNMP_VIEW)
                            snmp_actions.enable_snmp_v3(snmp_user=snmp_parameters.snmp_user,
                                                        snmp_password=snmp_parameters.snmp_password,
                                                        auth_protocol=self.SNMP_AUTH_MAP[
                                                            snmp_parameters.auth_protocol].lower(),
                                                        priv_protocol=self.SNMP_PRIV_MAP[
                                                            snmp_parameters.private_key_protocol].lower(),
                                                        snmp_priv_key=snmp_parameters.snmp_private_key,
                                                        snmp_group=self.DEFAULT_SNMP_GROUP)
                        else:
                            priv_protocol = self.SNMP_PRIV_MAP[snmp_parameters.private_key_protocol].lower()
                            if priv_protocol == "des":
                                priv_protocol = ""
                            snmp_actions.enable_snmp_v3(snmp_user=snmp_parameters.snmp_user,
                                                        snmp_password=snmp_parameters.snmp_password,
                                                        auth_protocol=self.SNMP_AUTH_MAP[
                                                            snmp_parameters.auth_protocol].lower(),
                                                        priv_protocol=priv_protocol,
                                                        snmp_priv_key=snmp_parameters.snmp_private_key,
                                                        snmp_group=None)

                else:
                    current_snmp_communities = snmp_actions.get_current_snmp_communities()
                    snmp_community = snmp_parameters.snmp_community
                    if snmp_community not in current_snmp_communities:
                        snmp_actions.enable_snmp(snmp_community, read_only_community)
                    else:
                        self._logger.debug("SNMP Community '{}' already configured".format(snmp_community))
            self._logger.info("Start verification of SNMP config")
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                # Reentering config mode to perform commit for IOS-XR
                updated_snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    updated_snmp_user = updated_snmp_actions.get_current_snmp_user()
                    if snmp_parameters.snmp_user not in updated_snmp_user:
                        raise Exception(self.__class__.__name__, "Failed to create SNMP v3 Configuration." +
                                        " Please check Logs for details")
                else:
                    updated_snmp_communities = updated_snmp_actions.get_current_snmp_communities()
                    if snmp_parameters.snmp_community not in updated_snmp_communities:
                        raise Exception(self.__class__.__name__, "Failed to create SNMP community." +
                                        " Please check Logs for details")

    def _validate_snmp_v3_params(self, snmp_v3_params):
        message = "Failed to enable SNMP v3, '{}' attribute cannot be empty"
        is_failed = False
        if not snmp_v3_params.private_key_protocol or self.SNMP_PRIV_MAP[
            snmp_v3_params.private_key_protocol] == 'No Privacy Protocol':
            # SNMP V3 Privacy Protocol
            is_failed = True
            message = message.format("SNMP V3 Privacy Protocol") + " or set to 'No Privacy Protocol'"

        if not snmp_v3_params.auth_protocol or self.SNMP_AUTH_MAP[
            snmp_v3_params.auth_protocol] == 'No Authentication Protocol':
            # SNMP V3 Authentication Protocol
            is_failed = True
            message = message.format("SNMP V3 Authentication Protocol") + " or set to 'No Authentication Protocol'"

        if not snmp_v3_params.snmp_user:
            is_failed = True
            message = message.format("SNMP V3 User")

        if not snmp_v3_params.snmp_private_key:
            is_failed = True
            message = message.format("SNMP V3 Private Key")

        if not snmp_v3_params.snmp_password:
            is_failed = True
            message = message.format("SNMP V3 Password")

        if is_failed:
            self._logger.error(message)
            raise AttributeError(self.__class__.__name__, message)
