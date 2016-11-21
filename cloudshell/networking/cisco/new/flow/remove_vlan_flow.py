from cloudshell.networking.devices.flows.base_flow import BaseFlow


class RemoveVlanFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(RemoveVlanFlow, self).__init__(cli_handler, logger)

    def execute_flow