from unittest import mock

from ynca.connection import YncaProtocolStatus


class YncaConnectionMock(mock.MagicMock):
    def __init__(self, *args, **kwargs) -> None:
        # Would like to have a MagicMock with `spec=YncaConnection`, but then
        # I can not add the response logic to the mock :/
        super().__init__(*args, **kwargs)
        self._num_commands_sent = 10

    @property
    def num_commands_sent(self):
        resp = self._num_commands_sent
        self._num_commands_sent += 10
        return resp

    def setup_responses(self):
        # Need to separate from __init__ otherwise it would run into infinite
        # recursion when executing `self.get.side_effect = xyz`
        self.get.side_effect = self._get_response
        self._get_response_list_offset = 0
        self._get_response_list = []

    def _get_response(self, subunit, function):
        print(f"get_response({subunit}, {function})")
        try:
            (match, responses) = self.get_response_list[self._get_response_list_offset]
            print(f"match={match}, responses={responses}")
            if match[0] == subunit and match[1] == function:
                self._get_response_list_offset += 1
                for response in responses:
                    if response[0].startswith("@"):
                        self.send_protocol_error(response[0])
                    else:
                        self.send_protocol_message(
                            response[0], response[1], response[2]
                        )
        except Exception as e:
            print(f"Skipping: {subunit}, {function} because of {e}")

    def send_protocol_message(self, subunit, function, value=None):
        self.register_message_callback.call_args.args[0](
            YncaProtocolStatus.OK, subunit, function, value
        )

    def send_protocol_error(self, error):
        self.register_message_callback.call_args.args[0](
            YncaProtocolStatus[error[1:]], None, None, None
        )
