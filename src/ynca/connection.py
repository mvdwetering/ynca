from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

import serialx

from .errors import YncaConnectionError, YncaConnectionFailed
from .protocol import YncaProtocol, YncaProtocolStatus

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class _ReaderThread(threading.Thread):
    def __init__(self, serial_port: serialx.BaseSerial, protocol: YncaProtocol) -> None:
        super().__init__(daemon=True)
        self._serial_port = serial_port
        self._protocol = protocol
        self._stop_event = threading.Event()

    def run(self) -> None:
        receive_buffer = bytearray(4096)
        line_buffer = bytearray()
        error: Exception | None = None

        try:
            while not self._stop_event.is_set():
                bytes_read = self._serial_port.readinto(receive_buffer, timeout=1)
                if not bytes_read:
                    continue

                line_buffer.extend(receive_buffer[:bytes_read])
                while (line_end := line_buffer.find(b"\n")) >= 0:
                    line = line_buffer[:line_end].rstrip(b"\r")
                    del line_buffer[: line_end + 1]
                    self._protocol.handle_line(line.decode("utf-8", errors="replace"))
        except (serialx.SerialException, OSError) as exc:
            error = exc
            if not self._stop_event.is_set():
                logger.exception("Serial error while reading")
        finally:
            self._protocol.connection_lost(error)

    def close(self) -> None:
        self._stop_event.set()
        if self.ident is not None and threading.current_thread() is not self:
            self.join(2)
        self._serial_port.close()


class YncaConnection:
    @classmethod
    def create_from_serial_url(cls, serial_url: str) -> YncaConnection:
        """Create a YncaConnection instance.

        serial_url:
            Can be a devicename (e.g. /dev/ttyUSB0 or COM3),
            or a URL supported by serialx, such as socket://ip:50000.
        """
        return cls(serial_url)

    def __init__(self, serial_url: str) -> None:
        """Instantiate a YncaConnection.

        serial_url:
            Can be a devicename (e.g. /dev/ttyUSB0 or COM3),
            or a URL supported by serialx, such as socket://ip:50000.
        """
        self._port = serial_url
        self._serial: serialx.BaseSerial | None = None
        self._readerthread: _ReaderThread | None = None
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

            serial_port = serialx.serial_for_url(
                self._port, read_timeout=1, write_timeout=1
            )
            serial_port.open()
            self._serial = serial_port
            self._protocol = YncaProtocol(
                self._call_registered_message_callbacks,
                self._on_disconnect,
                communication_log_size,
            )
            self._protocol.connection_made(serial_port)
            self._readerthread = _ReaderThread(serial_port, self._protocol)
            self._readerthread.start()
        except (serialx.SerialException, OSError) as e:
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
