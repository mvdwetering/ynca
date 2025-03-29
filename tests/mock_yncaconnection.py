from unittest import mock

from ynca.connection import YncaProtocolStatus


class YncaConnectionMock(mock.MagicMock):
    def __init__(self, *args, **kwargs) -> None:
        # Would like to have a MagicMock with `spec=YncaConnection`, but then
        # I can not add the response logic to the mock :/
        super().__init__(*args, **kwargs)
        self._num_commands_sent = 10
        self.get_response_list = []

    @property
    def num_commands_sent(self):
        return self._num_commands_sent

    def setup_responses(self):
        # Need to separate from __init__ otherwise it would run into infinite
        # recursion when executing `self.get.side_effect = xyz`
        self.get.side_effect = self._get_response
        self._get_response_list_offset = 0

    def _get_response(self, subunit: str, function: str):
        self._num_commands_sent += 1

        print(f"mock: get_response({subunit}, {function})")
        try:
            (next_request, responses) = self.get_response_list[
                self._get_response_list_offset
            ]
            print(f"mock:   next_request={next_request}, responses={responses}")
            if not (next_request[0] == subunit and next_request[1] == function):
                print(f"mock:   no match return @UNDEFINED")
                self.send_protocol_error("@UNDEFINED")
                return

            self._get_response_list_offset += 1
            for response in responses:
                if response[0].startswith("@"):
                    self.send_protocol_error(response[0])
                else:
                    self.send_protocol_message(response[0], response[1], response[2])

        except Exception as e:
            print(f"Skipping: {subunit}, {function} because of {e}")

    def send_protocol_message(self, subunit, function, value=None):
        for callback in self.register_message_callback.call_args.args:
            callback(YncaProtocolStatus.OK, subunit, function, value)

    def send_protocol_error(self, error):
        for callback in self.register_message_callback.call_args.args:
            callback(YncaProtocolStatus[error[1:]], None, None, None)
