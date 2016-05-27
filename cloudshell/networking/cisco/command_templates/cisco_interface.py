from cloudshell.cli.command_template.command_template import CommandTemplate

ENTER_INTERFACE_CONF_MODE = {
    'configure_interface': CommandTemplate('interface {0}', r'[\w-]+\s*[0-9/]+',
                                           'Interface name is incorrect!')}
