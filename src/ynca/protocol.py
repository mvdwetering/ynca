from __future__ import annotations

from enum import Enum
import logging
import queue
import re
import threading
import time
from typing import TYPE_CHECKING

import serial  # type: ignore[import-untyped]
import serial.threaded  # type: ignore[import-untyped]

from .helpers import RingBuffer

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class LogBuffer(RingBuffer[str]):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self._lock = threading.Lock()

    def add(self, item: str) -> None:
        with self._lock:
            super().add(item)

    def get_buffer(self) -> list[str]:
        with self._lock:
            return super().get_buffer()


class YncaProtocolStatus(Enum):
    OK = 0
    UNDEFINED = 1
    RESTRICTED = 2


class YncaProtocol(serial.threaded.LineReader):
    # YNCA spec specifies that there should be at least 100 milliseconds between commands
    COMMAND_SPACING = 0.1

    # YNCA spec says standby timeout is 40 seconds, so use a shorter period to be on the safe side
    KEEP_ALIVE_INTERVAL = 30

    def __init__(
        self,
        message_callback: (
            Callable[[YncaProtocolStatus, str | None, str | None, str | None], None]
            | None
        ) = None,
        disconnect_callback: Callable[[], None] | None = None,
        communication_log_size: int = 0,
    ) -> None:
        super().__init__()
        self._message_callback = message_callback
        self._disconnect_callback = disconnect_callback
        self._send_queue: queue.Queue
        self._send_thread: threading.Thread
        self._connected = False
        self._keep_alive_pending: threading.Event = threading.Event()
        self._communication_log_buffer: LogBuffer = LogBuffer(communication_log_size)
        self.num_commands_sent = 0

    @property
    def connected(self) -> bool:
        return self._connected

    def connection_made(self, transport) -> None:  # noqa: ANN001
        super().connection_made(transport)

        logger.debug("Connected")

        self._send_queue = queue.Queue()
        self._send_thread = threading.Thread(target=self._send_handler)
        self._send_thread.start()

        self._connected = True
        self._keep_alive_pending.clear()

        # When the device is in low power mode the first command is to wake up and gets lost
        # So send a dummy keep-alive on connect and a real one to make sure keep-alive administration is up-to-date
        self._send_keepalive()
        self._send_keepalive()

    def connection_lost(self, exc: Exception) -> None:
        self._connected = False

        logger.debug("Connection closed/lost %s", exc)

        if self._send_queue:
            # There seems to be no way to clear a queue so just read all and add the _EXIT command
            try:
                while self._send_queue.get(False):
                    pass
            except queue.Empty:
                pass
            finally:
                self._send_queue.put("_EXIT")
        if self._send_thread:
            self._send_thread.join(2)

        if self._disconnect_callback:
            self._disconnect_callback()

    def handle_line(self, line: str) -> None:
        ignore = False
        status = YncaProtocolStatus.OK
        subunit: str | None = None
        function: str | None = None
        value: str | None = None

        logger.debug("Recv - %s", line)
        self._communication_log_buffer.add(
            f"{time.perf_counter():.6f} Received: {line}"
        )

        if line == "@UNDEFINED":
            status = YncaProtocolStatus.UNDEFINED
        elif line == "@RESTRICTED":
            status = YncaProtocolStatus.RESTRICTED

        match = re.match(r"@(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.*)", line)
        if match is not None:
            subunit = match.group("subunit")
            function = match.group("function")
            value = match.group("value")

            if (
                self._keep_alive_pending.is_set()
                and subunit == "SYS"
                and function == "MODELNAME"
            ):
                ignore = True

        self._keep_alive_pending.clear()

        if not ignore and self._message_callback is not None:
            self._message_callback(status, subunit, function, value)

    def _send_keepalive(self) -> None:
        if self._send_queue:
            self._send_queue.put("_KEEP_ALIVE")

    def _send_handler(self) -> None:
        stop = False
        while not stop and self._send_queue:
            try:
                message = self._send_queue.get(True, self.KEEP_ALIVE_INTERVAL)

                if message == "_EXIT":
                    stop = True
                elif message == "_KEEP_ALIVE":
                    message = "@SYS:MODELNAME=?"  # Use MODELNAME as keep-alive, supported by all
                    self._keep_alive_pending.set()

                if not stop:
                    logger.debug("Send - %s", message)
                    self._communication_log_buffer.add(
                        f"{time.perf_counter():.6f} Send: {message}"
                    )

                    self.write_line(message)

                    # Maintain required command spacing
                    time.sleep(self.COMMAND_SPACING)
            except queue.Empty:
                # To avoid random message being eaten because device goes to sleep, keep it alive
                self._send_keepalive()
            except serial.SerialException:  # pragma: no cover
                logger.exception("Serial error while writing, stopping thread")
                stop = True

    def raw(self, raw_data: str) -> None:
        if self._send_queue:
            self._send_queue.put(raw_data)
            self.num_commands_sent += 1

    def put(self, subunit: str, funcname: str, parameter: str) -> None:
        if self._send_queue:
            self._send_queue.put(f"@{subunit}:{funcname}={parameter}")
            self.num_commands_sent += 1

    def get(self, subunit: str, funcname: str) -> None:
        self.put(subunit, funcname, "?")

    def get_communication_log_items(self) -> list[str]:
        """Get a list of logged communication items."""
        return self._communication_log_buffer.get_buffer()
