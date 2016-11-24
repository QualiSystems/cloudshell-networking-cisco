from cloudshell.networking.devices.flows.action_flows import RunCommandFlow


class CiscoRunCustomCommandFlow(RunCommandFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoRunCustomCommand, self).__init__(cli_handler, logger)

    def execute_flow(self, custom_command='', is_config=False):
        responses = []
        if isinstance(custom_command, str):
            commands = [custom_command]
        elif isinstance(custom_command, tuple):
            commands = list(custom_command)
        else:
            commands = custom_command

        mode = self._cli_handler.enable_mode
        if is_config:
            mode = self._cli_handler.config_mode
        with self._cli_handler.get_session(mode) as session:
            if is_config:
                for cmd in commands:
                    responses.append(session.send_command(command=cmd))
        return '\n'.join(responses)
