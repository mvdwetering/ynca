from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, cast

import serial  # type: ignore[import-untyped]
import serial.threaded  # type: ignore[import-untyped]

from .errors import YncaConnectionError, YncaConnectionFailed
from .protocol import YncaProtocol, YncaProtocolStatus

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class YncaConnection:
    @classmethod
    def create_from_serial_url(cls, serial_url: str) -> YncaConnection:
        """Create a YncaConnection instance.

        serial_url:
            Can be a devicename (e.g. /dev/ttyUSB0 or COM3),
            but also any of supported url handlers by pyserial
            https://pyserial.readthedocs.io/en/latest/url_handlers.html
            This allows to setup IP connections with socket://ip:50000
            or select a specific usb-2-serial with hwgrep:// which is
            useful when the links to ttyUSB# change randomly.
        """
        return cls(serial_url)

    def __init__(self, serial_url: str) -> None:
        """Instantiate a YncaConnection.

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
        self._readerthread: serial.threaded.ReaderThread | None = None
        self._protocol: YncaProtocol | None = None

        self._is_closing = threading.Event()
        self._disconnect_callback: Callable[[], None] | None = None

        self._message_callbacks: set[
            Callable[[YncaProtocolStatus, str | None, str | None, str | None], None]
        ] = set()

    def register_message_callback(
        self,
        callback: Callable[
            [YncaProtocolStatus, str | None, str | None, str | None], None
        ],
    ) -> None:
        """Register a callback to be called when a message is received."""
        self._message_callbacks.add(callback)

    def unregister_message_callback(
        self,
        callback: Callable[
            [YncaProtocolStatus, str | None, str | None, str | None], None
        ],
    ) -> None:
        """Unregister a previously registered callback."""
        self._message_callbacks.discard(callback)

    def _call_registered_message_callbacks(
        self,
        status: YncaProtocolStatus,
        subunit: str | None,
        function_: str | None,
        value: str | None,
    ) -> None:
        for callback in self._message_callbacks:
            callback(status, subunit, function_, value)

    def _on_disconnect(self) -> None:
        # Disconnect callback is for unexpected disconnects
        # Don't need it to be called on planned `close()`
        if self._disconnect_callback and not self._is_closing.is_set():
            self._disconnect_callback()

    def connect(
        self,
        disconnect_callback: Callable[[], None] | None = None,
        communication_log_size: int = 0,
    ) -> None:
        """Connect to the receiver.

        disconnect_callback:
            Will be called when the connection is lost. It will _not_ be called when `close()` is called explicitly.

        communication_log_size:
            Amount of communication items to log. Useful for debugging.
            Get the logged items with the `get_communication_log_items` method
        """
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
            raise YncaConnectionError from e
        except RuntimeError as e:
            raise YncaConnectionFailed from e

    def close(self) -> None:
        """Close the connection."""
        self._is_closing.set()

        if self._readerthread:
            self._readerthread.close()

    def raw(self, raw_data: str) -> None:
        """Send raw data to the receiver."""
        if self._protocol:
            self._protocol.raw(raw_data)

    def put(self, subunit: str, funcname: str, parameter: str) -> None:
        """Send a PUT request to set a value of a function on a subunit of the receiver."""
        if self._protocol:
            self._protocol.put(subunit, funcname, parameter)

    def get(self, subunit: str, funcname: str) -> None:
        """Send a GET request to get a value of a function on a subunit of the receiver. Note that only a request is sent, no response is awaited."""
        if self._protocol:
            self._protocol.get(subunit, funcname)

    @property
    def connected(self) -> bool:
        """Indicates if connection is connected or not."""
        return self._protocol.connected if self._protocol else False

    @property
    def num_commands_sent(self) -> int:
        """Get the amount of commands sent."""
        return self._protocol.num_commands_sent if self._protocol else 0

    def get_communication_log_items(self) -> list[str]:
        """Get a list of logged communication items."""
        return self._protocol.get_communication_log_items() if self._protocol else []
