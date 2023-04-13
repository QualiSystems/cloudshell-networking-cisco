class CiscoGeneralError(Exception):
    """Cisco General Error."""


class CiscoSNMPError(CiscoGeneralError):
    """Cisco SNMP Error."""


class CiscoCliError(CiscoGeneralError):
    """Cisco Cli Error."""


class CiscoInvalidCommandError(CiscoGeneralError):
    """Cisco Invalid Command Error."""


class CiscoConfigurationError(CiscoGeneralError):
    """Cisco Configuration Error."""


class CiscoConnectivityError(CiscoGeneralError):
    """Cisco Connectivity Error."""
