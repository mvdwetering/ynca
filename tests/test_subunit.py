"""Test Zone subunit"""

from unittest import mock
import pytest

from ynca import Avail
from ynca.constants import Subunit
from ynca.subunit import SubunitBase
from ynca.function import IntFunctionMixin
from ynca.errors import YncaInitializationFailedException


SYS = "SYS"
SUBUNIT = "UAW"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
        ],
    ),
    (
        (SUBUNIT, "DUMMY_FUNCTION"),
        [
            (SUBUNIT, "DUMMY_FUNCTION", "1"),
        ],
    ),
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
]

# Need a class with an ID to test some of the handling
class DummySubunit(SubunitBase):
    id = Subunit.UAW

    dummy_function = IntFunctionMixin()


@pytest.fixture
def initialized_dummysubunit(connection) -> DummySubunit:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    sui = DummySubunit(connection)
    sui.initialize()
    return sui


def test_construct(connection, update_callback):

    dsu = DummySubunit(connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_fail(connection, update_callback):

    dsu = DummySubunit(connection)
    dsu.register_update_callback(update_callback)

    with pytest.raises(YncaInitializationFailedException):
        dsu.initialize()

    assert update_callback.call_count == 0


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    dsu = DummySubunit(connection)
    dsu.register_update_callback(update_callback)

    dsu.initialize()

    assert update_callback.call_count == 0
    assert dsu.avail == Avail.READY


def test_registration(connection, initialized_dummysubunit: SubunitBase):

    update_callback_1 = mock.MagicMock()
    update_callback_2 = mock.MagicMock()

    # Register multiple callbacks, both get called
    initialized_dummysubunit.register_update_callback(update_callback_1)
    initialized_dummysubunit.register_update_callback(update_callback_2)
    connection.send_protocol_message(SUBUNIT, "DUMMY_FUNCTION", "2")
    assert update_callback_1.call_count == 1
    update_callback_1.assert_called_with("DUMMY_FUNCTION", 2)
    assert update_callback_2.call_count == 1
    update_callback_2.assert_called_with("DUMMY_FUNCTION", 2)

    # Double registration (second gets ignored)
    initialized_dummysubunit.register_update_callback(update_callback_2)
    connection.send_protocol_message(SUBUNIT, "DUMMY_FUNCTION", "3")
    assert update_callback_1.call_count == 2
    update_callback_1.assert_called_with("DUMMY_FUNCTION", 3)
    assert update_callback_2.call_count == 2
    update_callback_2.assert_called_with("DUMMY_FUNCTION", 3)

    # Unregistration
    initialized_dummysubunit.unregister_update_callback(update_callback_2)
    connection.send_protocol_message(SUBUNIT, "DUMMY_FUNCTION", "4")
    assert update_callback_1.call_count == 3
    update_callback_1.assert_called_with("DUMMY_FUNCTION", 4)
    assert update_callback_2.call_count == 2


def test_close(connection, initialized_dummysubunit: SubunitBase):

    initialized_dummysubunit.close()
    connection.unregister_message_callback.assert_called_once()

    # Should be safe to call multiple times
    initialized_dummysubunit.close()
    connection.unregister_message_callback.assert_called_once()


def test_unknown_functions_ignored(
    connection, initialized_dummysubunit: SubunitBase, update_callback
):
    initialized_dummysubunit.register_update_callback(update_callback)
    connection.send_protocol_message(SUBUNIT, "UnknownFunction", "Value")
    assert update_callback.call_count == 0


def test_status_not_ok_ignored(
    connection, initialized_dummysubunit: SubunitBase, update_callback
):
    initialized_dummysubunit.register_update_callback(update_callback)
    connection.send_protocol_error("@UNDEFINED")
    assert update_callback.call_count == 0
    connection.send_protocol_error("@RESTRICTED")
    assert update_callback.call_count == 0


def test_write_function_calls_connection_put(
    connection, initialized_dummysubunit: SubunitBase, update_callback
):
    initialized_dummysubunit.dummy_function = 123
    connection.put.assert_called_with("UAW", "DUMMY_FUNCTION", "123")
