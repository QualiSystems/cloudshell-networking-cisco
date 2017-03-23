import telnetlib
from collections import OrderedDict

from cloudshell.cli.session.session_exceptions import SessionException
from cloudshell.cli.session.telnet_session import TelnetSession


class TelnetSessionException(SessionException):
    pass


class ConsoleTelnetSession(TelnetSession):
    def __init__(self, host, username, password, port=None, on_session_start=None, start_with_new_line=None, *args, **kwargs):
        super(ConsoleTelnetSession, self).__init__(host, username, password, port, on_session_start,
                                                   loop_detector_max_action_loops=5, *args, **kwargs)
        self._start_with_new_line = start_with_new_line

    def connect(self, prompt, logger):
        """Open connection to device / create session

        :param prompt:
        :param logger:
        """
        if not self._handler:
            self._handler = telnetlib.Telnet()

        self._handler.open(self.host, int(self.port), self._timeout)
        if self._handler.get_socket() is None:
            raise TelnetSessionException(self.__class__.__name__, "Failed to open telnet connection.")

        self._handler.get_socket().send(telnetlib.IAC + telnetlib.WILL + telnetlib.ECHO)

        action_map = OrderedDict()
        action_map['[Ll]ogin:|[Uu]ser:|[Uu]sername:'] = lambda session, logger: session.send_line(session.username,
                                                                                                  logger)
        action_map['[Pp]assword:'] = lambda session, logger: session.send_line(session.password, logger)
        empty_key = r'.*'

        def empty_action(ses, log):
            ses.send_line('', log)
            if empty_key in action_map:
                del action_map[empty_key]

        action_map[empty_key] = empty_action
        cmd = None
        if self._start_with_new_line:
            cmd = ""
        try:
            out = self.hardware_expect(cmd, expected_string=prompt, timeout=self._timeout, logger=logger,
                                       action_map=action_map)
            if self.on_session_start and callable(self.on_session_start):
                self.on_session_start(self, logger)
        except Exception:
            self.disconnect()
            raise
        self._active = True
