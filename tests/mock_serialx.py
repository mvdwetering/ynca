from __future__ import annotations

import socket
import threading
import time


class MockSerialStub:
    def __init__(
        self,
        receive_bytes: bytes,
        send_bytes: bytes,
        split_at: int | None,
    ) -> None:
        self.receive_bytes = receive_bytes.rstrip(b"\r\n")
        self.send_bytes = send_bytes
        self.split_at = split_at
        self.calls = 0


class MockSerial:
    def __init__(self) -> None:
        self._server = socket.socket()
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(("127.0.0.1", 0))
        self._server.listen()
        self._server.settimeout(0.1)
        self.port = f"socket://127.0.0.1:{self._server.getsockname()[1]}"

        self._stubs: list[MockSerialStub] = []
        self._stubs_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stub(
        self,
        receive_bytes: bytes,
        send_bytes: bytes,
        *,
        split_at: int | None = None,
    ) -> MockSerialStub:
        stub = MockSerialStub(receive_bytes, send_bytes, split_at)
        with self._stubs_lock:
            self._stubs.append(stub)
        return stub

    def close(self) -> None:
        self._stop_event.set()
        self._server.close()
        self._thread.join(2)

    def _serve(self) -> None:
        client = self._accept()
        if client is None:
            return

        with client:
            client.settimeout(0.1)
            self._serve_client(client)

    def _accept(self) -> socket.socket | None:
        while not self._stop_event.is_set():
            try:
                client, _ = self._server.accept()
            except TimeoutError:
                continue
            except OSError:
                if not self._stop_event.is_set():
                    raise
                return None
            else:
                return client

        return None

    def _serve_client(self, client: socket.socket) -> None:
        receive_buffer = bytearray()
        while not self._stop_event.is_set():
            try:
                data = client.recv(4096)
            except TimeoutError:
                continue
            except OSError:
                if not self._stop_event.is_set():
                    raise
                return

            if not data:
                return

            receive_buffer.extend(data)
            while (line_end := receive_buffer.find(b"\n")) >= 0:
                request = receive_buffer[:line_end].rstrip(b"\r")
                del receive_buffer[: line_end + 1]
                self._respond(client, request)

    def _respond(self, client: socket.socket, request: bytes) -> None:
        with self._stubs_lock:
            stub = next(
                (stub for stub in self._stubs if stub.receive_bytes == request),
                None,
            )
            if stub is not None:
                stub.calls += 1

        if stub is not None and stub.send_bytes:
            if stub.split_at is not None:
                client.sendall(stub.send_bytes[: stub.split_at])
                time.sleep(0.01)
                client.sendall(stub.send_bytes[stub.split_at :])
            else:
                client.sendall(stub.send_bytes)
