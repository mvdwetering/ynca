from collections.abc import Generator
from contextlib import contextmanager
import threading
import time
from unittest import mock

from mock_serial import MockSerial  # type: ignore[import]
import pytest
import serial

from ynca.connection import YncaConnection, YncaProtocolStatus
from ynca.errors import YncaConnectionError, YncaConnectionFailed

SHORT_DELAY = 0.5


@contextmanager
def active_connection(
    serial_mock: MockSerial,
    delay_after_close: float = SHORT_DELAY,
    communication_log_size: int = 0,
) -> Generator[YncaConnection, None, None]:
    serial_mock.stub(
        receive_bytes=b"@SYS:MODELNAME=?\r\n",
        send_bytes=b"@SYS:MODELNAME=TESTMODEL\r\n",
    )  # Keep alive

    try:
        connection = YncaConnection.create_from_serial_url(serial_mock.port)
        connection.connect(communication_log_size=communication_log_size)
        yield connection
    finally:
        # Need to make sure messages actually got sent by the thread
        # on the other side of the queue.
        # Don't know how to check properly so just delay a bit :/
        # Note that delay depends on amount of commands sent because of the 100ms command spacing
        time.sleep(delay_after_close)
        connection.close()


def test_close_uninitialized() -> None:
    connection = YncaConnection("dummy")
    assert not connection.connected
    connection.close()
    assert not connection.connected


def test_connect(mock_serial: MockSerial) -> None:
    keep_alive = mock_serial.stub(
        receive_bytes=b"@SYS:MODELNAME=?\r\n",
        send_bytes=b"@SYS:MODELNAME=TESTMODEL\r\n",
    )

    connection = YncaConnection(mock_serial.port)
    connection.connect()
    assert connection.connected
    assert connection.num_commands_sent == 0

    # Need to make sure messages actually got sent by the thread :/
    time.sleep(SHORT_DELAY)

    connection.close()
    assert not connection.connected
    assert connection.num_commands_sent == 0

    # Double keep alive test intended because device can eat first one
    assert keep_alive.calls == 2


def test_connect_invalid_port() -> None:
    connection = YncaConnection("invalid")
    with pytest.raises(YncaConnectionError):
        connection.connect()


def test_connect_runtime_error(mock_serial: MockSerial) -> None:
    with mock.patch(
        "serial.serial_for_url",
        side_effect=RuntimeError("Runtime error"),
    ):
        connection = YncaConnection(mock_serial.port)
        with pytest.raises(YncaConnectionFailed):
            connection.connect()


def test_disconnect() -> None:
    disconnect_event = threading.Event()
    disconnect_callback = mock.MagicMock(side_effect=lambda: disconnect_event.set())

    read_should_fail = threading.Event()

    mock_ser = mock.MagicMock()
    mock_ser.is_open = True
    mock_ser.in_waiting = 0

    def controlled_read(_size: int) -> bytes:
        # Block until the test triggers a simulated disconnect, just like a real
        # serial port would block until data arrives or the connection drops.
        read_should_fail.wait(timeout=5.0)
        msg = "Simulated unexpected disconnect"
        raise serial.SerialException(msg)

    mock_ser.read.side_effect = controlled_read

    with mock.patch("serial.serial_for_url", return_value=mock_ser):
        connection = YncaConnection("dummy_port")
        connection.connect(disconnect_callback=disconnect_callback)

        # Trigger the simulated disconnect; controlled_read raises SerialException
        # which the ReaderThread detects and routes to connection_lost().
        read_should_fail.set()

        assert disconnect_event.wait(
            timeout=2.0
        ), "Disconnect callback not called within timeout"

    assert disconnect_callback.call_count == 1


def test_disconnect_oserror() -> None:
    """OSError from in_waiting (e.g. EIO on PTY/USB disconnect) must still fire the callback.

    pyserial's ReaderThread only catches serial.SerialException inside its read
    loop, so an OSError raised by in_waiting escapes without calling
    connection_lost().  _ReaderThread wraps this case.
    """
    disconnect_event = threading.Event()
    disconnect_callback = mock.MagicMock(side_effect=lambda: disconnect_event.set())

    in_waiting_should_fail = threading.Event()

    mock_ser = mock.MagicMock()
    mock_ser.is_open = True

    def controlled_in_waiting() -> int:
        in_waiting_should_fail.wait(timeout=5.0)
        raise OSError(5, "Input/output error")

    type(mock_ser).in_waiting = mock.PropertyMock(side_effect=controlled_in_waiting)

    with mock.patch("serial.serial_for_url", return_value=mock_ser):
        connection = YncaConnection("dummy_port")
        connection.connect(disconnect_callback=disconnect_callback)

        in_waiting_should_fail.set()

        assert disconnect_event.wait(
            timeout=2.0
        ), "Disconnect callback not called within timeout"

    assert disconnect_callback.call_count == 1


def test_send_raw(mock_serial: MockSerial) -> None:
    with active_connection(mock_serial) as connection:
        raw_data = mock_serial.stub(receive_bytes=b"RAW DATA", send_bytes=b"")

        connection.raw("RAW DATA")
        assert connection.num_commands_sent == 1

    assert raw_data.calls == 1


def test_send_put(mock_serial: MockSerial) -> None:
    with active_connection(mock_serial) as connection:
        put_data = mock_serial.stub(
            receive_bytes=b"@Subunit:Function=Value\r\n", send_bytes=b""
        )

        connection.put("Subunit", "Function", "Value")
        assert connection.num_commands_sent == 1

    assert put_data.calls == 1


def test_send_get(mock_serial: MockSerial) -> None:
    with active_connection(mock_serial) as connection:
        get_data = mock_serial.stub(
            receive_bytes=b"@Subunit:Function=?\r\n", send_bytes=b""
        )

        connection.get("Subunit", "Function")
        assert connection.num_commands_sent == 1

    assert get_data.calls == 1


def test_message_callbacks(mock_serial: MockSerial) -> None:
    with active_connection(mock_serial) as connection:
        mock_serial.stub(
            receive_bytes=b"@RequestSubunit1:RequestFunction1=?\r\n",
            send_bytes=b"@ResponseSubunit1:ResponseFunction1=ResponseValue1\r\n",
        )
        mock_serial.stub(
            receive_bytes=b"@RequestSubunit2:RequestFunction2=?\r\n",
            send_bytes=b"@ResponseSubunit2:ResponseFunction2=ResponseValue2\r\n",
        )

        # 2 message callbacks registered
        message_callback_1 = mock.MagicMock()
        message_callback_2 = mock.MagicMock()
        connection.register_message_callback(message_callback_1)
        connection.register_message_callback(message_callback_2)

        connection.get("RequestSubunit1", "RequestFunction1")

        time.sleep(SHORT_DELAY)
        assert message_callback_1.call_count == 1
        assert message_callback_2.call_count == 1
        call_args_1 = mock.call(
            YncaProtocolStatus.OK,
            "ResponseSubunit1",
            "ResponseFunction1",
            "ResponseValue1",
        )
        assert message_callback_1.call_args == call_args_1
        assert message_callback_2.call_args == call_args_1

        # Unregister message callback 1, duplicate register message callback 2
        connection.unregister_message_callback(message_callback_1)
        connection.register_message_callback(message_callback_2)

        connection.get("RequestSubunit2", "RequestFunction2")

        time.sleep(SHORT_DELAY)
        assert message_callback_1.call_count == 1
        assert message_callback_2.call_count == 2
        assert message_callback_2.call_args == mock.call(
            YncaProtocolStatus.OK,
            "ResponseSubunit2",
            "ResponseFunction2",
            "ResponseValue2",
        )

        # Unregister message callback too many times
        connection.unregister_message_callback(message_callback_1)


def test_protocol_status(mock_serial: MockSerial) -> None:
    with active_connection(mock_serial) as connection:
        # Undefined response
        mock_serial.stub(
            receive_bytes=b"@Subunit:Function=Undefined\r\n",
            send_bytes=b"@UNDEFINED\r\n",
        )

        # Restricted response
        mock_serial.stub(
            receive_bytes=b"@Subunit:Function=Restricted\r\n",
            send_bytes=b"@RESTRICTED\r\n",
        )

        message_callback = mock.MagicMock()
        connection.register_message_callback(message_callback)

        connection.put("Subunit", "Function", "Undefined")
        time.sleep(SHORT_DELAY)
        assert message_callback.call_args == mock.call(
            YncaProtocolStatus.UNDEFINED, mock.ANY, mock.ANY, mock.ANY
        )

        connection.put("Subunit", "Function", "Restricted")
        time.sleep(SHORT_DELAY)
        assert message_callback.call_args == mock.call(
            YncaProtocolStatus.RESTRICTED, mock.ANY, mock.ANY, mock.ANY
        )


def test_get_communication_log_items(mock_serial: MockSerial) -> None:
    with active_connection(mock_serial, communication_log_size=5) as connection:
        time.sleep(SHORT_DELAY)
        logitems = connection.get_communication_log_items()
        assert len(logitems) == 4  # Send en received keep-alive

        connection.get("Subunit", "Function")
        time.sleep(SHORT_DELAY)
        logitems = connection.get_communication_log_items()
        assert len(logitems) == 5  # 1 dropped out due to size limit


def test_keep_alive(mock_serial: MockSerial) -> None:
    # Tweak the internal keep-alive interval to keep test short
    from ynca.connection import YncaProtocol

    YncaProtocol.KEEP_ALIVE_INTERVAL = 2  # type: ignore[attr-defined]

    with active_connection(mock_serial, communication_log_size=100) as connection:
        message_callback = mock.MagicMock()
        connection.register_message_callback(message_callback)

        time.sleep(SHORT_DELAY)
        logitems = connection.get_communication_log_items()
        assert len(logitems) == 4  # Send en received keep-alive are logged

        time.sleep(2)
        logitems = connection.get_communication_log_items()
        assert len(logitems) == 6  # 1 additional keep alive pair

        # Keep alives do not generate message callbacks
        assert message_callback.call_count == 0

        # Manual sending of MODELNAME (which is internal keep alive)
        # must still work as expected
        connection.get("SYS", "MODELNAME")
        time.sleep(SHORT_DELAY)
        assert message_callback.call_args == mock.call(
            YncaProtocolStatus.OK, "SYS", "MODELNAME", "TESTMODEL"
        )
