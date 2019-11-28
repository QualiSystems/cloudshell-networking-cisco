#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.networking.cisco.command_actions.enable_disable_snmp_actions import (
    EnableDisableSnmpActions,
)


class CiscoEnableSnmpFlow(object):
    DEFAULT_SNMP_VIEW = "quali_snmp_view"
    DEFAULT_SNMP_GROUP = "quali_snmp_group"

    def __init__(self, cli_handler, logger):
        """Enable snmp flow.

        :param cli_handler:
        :param logger:
        :return:
        """
        self._logger = logger
        self._cli_handler = cli_handler

    def enable_flow(self, snmp_parameters):
        if "3" not in snmp_parameters.version and not snmp_parameters.snmp_community:
            message = "SNMP community cannot be empty"
            self._logger.error(message)
            raise Exception(message)

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if "3" in snmp_parameters.version:
                    current_snmp_user = snmp_actions.get_current_snmp_user()
                    if snmp_parameters.snmp_user not in current_snmp_user:
                        snmp_parameters.validate()
                        current_snmp_config = snmp_actions.get_current_snmp_config()
                        if (
                            "snmp-server view {}".format(self.DEFAULT_SNMP_VIEW)
                            not in current_snmp_config
                        ):
                            snmp_actions.enable_snmp_view(
                                snmp_view=self.DEFAULT_SNMP_VIEW
                            )
                        if (
                            "snmp-server group {}".format(self.DEFAULT_SNMP_GROUP)
                            not in current_snmp_config
                        ):
                            snmp_actions.enable_snmp_group(
                                snmp_group=self.DEFAULT_SNMP_GROUP,
                                snmp_view=self.DEFAULT_SNMP_VIEW,
                            )
                        snmp_actions.enable_snmp_v3(
                            snmp_user=snmp_parameters.snmp_user,
                            snmp_password=snmp_parameters.snmp_password,
                            auth_protocol=snmp_parameters.auth_protocol.lower(),
                            priv_protocol=snmp_parameters.private_key_protocol.lower(),
                            snmp_priv_key=snmp_parameters.snmp_private_key,
                            snmp_group=self.DEFAULT_SNMP_GROUP,
                        )

                else:
                    current_snmp_communities = snmp_actions.get_current_snmp_config()
                    snmp_community = snmp_parameters.snmp_community
                    if not re.search(
                        "snmp-server community {}".format(
                            re.escape(snmp_parameters.snmp_community)
                        ),
                        current_snmp_communities,
                    ):
                        snmp_actions.enable_snmp(
                            snmp_community, snmp_parameters.is_read_only
                        )
                    else:
                        self._logger.debug(
                            "SNMP Community '{}' already configured".format(
                                snmp_community
                            )
                        )
            self._logger.info("Start verification of SNMP config")
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                # Reentering config mode to perform commit for IOS-XR
                updated_snmp_actions = EnableDisableSnmpActions(
                    config_session, self._logger
                )
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    updated_snmp_user = updated_snmp_actions.get_current_snmp_user()
                    if snmp_parameters.snmp_user not in updated_snmp_user:
                        raise Exception(
                            self.__class__.__name__,
                            "Failed to create SNMP v3 Configuration."
                            + " Please check Logs for details",
                        )
                else:
                    updated_snmp_communities = (
                        updated_snmp_actions.get_current_snmp_config()
                    )
                    if not re.search(
                        "snmp-server community {}".format(
                            re.escape(snmp_parameters.snmp_community)
                        ),
                        updated_snmp_communities,
                    ):
                        raise Exception(
                            self.__class__.__name__,
                            "Failed to create SNMP community."
                            + " Please check Logs for details",
                        )
