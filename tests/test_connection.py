import time
from contextlib import contextmanager
from unittest import mock

from ynca.connection import YncaConnection, YncaProtocolStatus

@contextmanager
def active_connection(serial_mock, delay_after_close:float=0.5):

    keep_alive = serial_mock.stub(
        receive_bytes=b'@SYS:MODELNAME=?\r\n',
        send_bytes=b'@SYS:MODELNAME=TESTMODEL\r\n'
    )

    try:
        connection = YncaConnection(serial_mock.port)
        connection.connect()
        yield connection
    finally:
        # Need to make sure messages actually got sent by the thread
        # on the other side of the queue.
        # Don't know how to check properly so just delay a bit :/
        # Note that delay depends on amount of commands sent because of the 100ms command spacing
        time.sleep(delay_after_close)
        connection.close()




def test_close_uninitialized():
    connection = YncaConnection("dummy")
    assert not connection.connected
    connection.close()
    assert not connection.connected


def test_connect(mock_serial):

    keep_alive = mock_serial.stub(
        receive_bytes=b'@SYS:MODELNAME=?\r\n',
        send_bytes=b'@SYS:MODELNAME=TESTMODEL\r\n'
    )

    connection = YncaConnection(mock_serial.port)
    connection.connect()
    assert connection.connected
    assert connection.num_commands_sent == 0

    # Need to make sure messages actually got sent by the thread :/
    time.sleep(0.5)

    connection.close()
    assert not connection.connected
    assert connection.num_commands_sent == 0

    # Double keep alive test intended because device can eat first one
    assert keep_alive.calls == 2



def test_send_raw(mock_serial):

    with active_connection(mock_serial) as connection:
        raw_data = mock_serial.stub(
            receive_bytes=b'RAW DATA',
            send_bytes=b''
        )

        connection.raw("RAW DATA")
        assert connection.num_commands_sent == 1

    assert raw_data.calls == 1

def test_send_put(mock_serial):

    with active_connection(mock_serial) as connection:
        raw_data = mock_serial.stub(
            receive_bytes=b'@Subunit:Function=Value\r\n',
            send_bytes=b''
        )

        connection.put("Subunit", "Function", "Value")
        assert connection.num_commands_sent == 1

    assert raw_data.calls == 1


def test_send_get(mock_serial):

    with active_connection(mock_serial) as connection:
        raw_data = mock_serial.stub(
            receive_bytes=b'@Subunit:Function=?\r\n',
            send_bytes=b''
        )

        connection.get("Subunit", "Function")
        assert connection.num_commands_sent == 1

    assert raw_data.calls == 1


def test_message_callbacks(mock_serial):

    with active_connection(mock_serial) as connection:
        data_1 = mock_serial.stub(
            receive_bytes=b'@RequestSubunit1:RequestFunction1=?\r\n',
            send_bytes=b'@ResponseSubunit1:ResponseFunction1=ResponseValue1\r\n',
        )
        data_2 = mock_serial.stub(
            receive_bytes=b'@RequestSubunit2:RequestFunction2=?\r\n',
            send_bytes=b'@ResponseSubunit2:ResponseFunction2=ResponseValue2\r\n',
        )

        # 2 message callbacks registered
        message_callback_1 = mock.MagicMock()
        message_callback_2 = mock.MagicMock()
        connection.register_message_callback(message_callback_1)
        connection.register_message_callback(message_callback_2)

        connection.get("RequestSubunit1", "RequestFunction1")

        time.sleep(0.5)
        assert message_callback_1.call_count == 1
        assert message_callback_2.call_count == 1
        call_args_1 = mock.call(YncaProtocolStatus.OK, "ResponseSubunit1", "ResponseFunction1", "ResponseValue1")
        assert message_callback_1.call_args == call_args_1
        assert message_callback_2.call_args == call_args_1


        # Unregister message callback 1, duplicate register message callback 2
        connection.unregister_message_callback(message_callback_1)
        connection.register_message_callback(message_callback_2)

        connection.get("RequestSubunit2", "RequestFunction2")

        time.sleep(0.5)
        assert message_callback_1.call_count == 1
        assert message_callback_2.call_count == 2
        assert message_callback_2.call_args == mock.call(YncaProtocolStatus.OK, "ResponseSubunit2", "ResponseFunction2", "ResponseValue2")

        # Unregister message callback too many times 
        connection.unregister_message_callback(message_callback_1)
