from __future__ import annotations

import logging
from typing import Callable, List, Optional, Set, cast

import serial  # type: ignore
import serial.threaded # type: ignore


from .errors import YncaConnectionError, YncaConnectionFailed
from .protocol import YncaProtocol, YncaProtocolStatus

logger = logging.getLogger(__name__)

class YncaConnection:
    @classmethod
    def create_from_serial_url(cls, serial_url: str):
        return cls(serial_url)

    def __init__(self, serial_url: str):
        """Instantiate a YncaConnection

        serial_url:
            Can be a devicename (e.g. /dev/ttyUSB0 or COM3),
            but also any of supported url handlers by pyserial
            https://pyserial.readthedocs.io/en/latest/url_handlers.html
            This allows to setup IP connections with socket://ip:50000
            or select a specific usb-2-serial with hwgrep:// which is
            useful when the links to ttyUSB# change randomly.
        """
        self._port = serial_url
        self._serial = None
        self._readerthread: Optional[serial.threaded.ReaderThread] = None
        self._protocol: Optional[YncaProtocol] = None

        self._disconnect_callback: Callable[[], None] | None = None
        self._message_callbacks: Set[
            Callable[[YncaProtocolStatus, str | None, str | None, str | None], None]
        ] = set()

    def register_message_callback(
        self,
        callback: Callable[
            [YncaProtocolStatus, str | None, str | None, str | None], None
        ],
    ):
        self._message_callbacks.add(callback)

    def unregister_message_callback(
        self,
        callback: Callable[
            [YncaProtocolStatus, str | None, str | None, str | None], None
        ],
    ):
        self._message_callbacks.discard(callback)

    def _call_registered_message_callbacks(
        self,
        status: YncaProtocolStatus,
        subunit: str | None,
        function_: str | None,
        value: str | None,
    ):
        for callback in self._message_callbacks:
            callback(status, subunit, function_, value)

    def _on_disconnect(self):
        if self._disconnect_callback:
            self._disconnect_callback()


    def connect(
        self,
        disconnect_callback: Callable[[], None] | None = None,
        communication_log_size: int = 0,
    ):
        try:
            self._disconnect_callback = disconnect_callback
            self._serial = serial.serial_for_url(self._port)
            self._readerthread = serial.threaded.ReaderThread(
                self._serial,
                lambda: YncaProtocol(
                    self._call_registered_message_callbacks,
                    self._on_disconnect,
                    communication_log_size,
                ),
            )
            self._readerthread.start()
            _, protocol = self._readerthread.connect()
            self._protocol = cast(YncaProtocol, protocol)
        except serial.SerialException as e:
            raise YncaConnectionError(e)
        except RuntimeError as e:
            raise YncaConnectionFailed(e)

    def close(self):
        # Disconnect callback is for unexpected disconnects
        # Don't need it to be called on planned `close()`
        self._disconnect_callback = None

        if self._readerthread:
            self._readerthread.close()

    def raw(self, raw_data: str):
        if self._protocol:
            self._protocol.raw(raw_data)

    def put(self, subunit: str, funcname: str, parameter: str):
        if self._protocol:
            self._protocol.put(subunit, funcname, parameter)

    def get(self, subunit: str, funcname: str):
        if self._protocol:
            self._protocol.get(subunit, funcname)

    @property
    def connected(self):
        return self._protocol.connected if self._protocol else False

    @property
    def num_commands_sent(self):
        return self._protocol.num_commands_sent if self._protocol else 0

    def get_communication_log_items(self) -> List[str]:
        """Get a list of logged communication items."""
        return self._protocol.get_communication_log_items() if self._protocol else []
