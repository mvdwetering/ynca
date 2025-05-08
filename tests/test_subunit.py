"""Test Zone subunit."""

from unittest import mock

import pytest  # type: ignore[import]

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Avail
from ynca.constants import Subunit
from ynca.errors import YncaInitializationFailedException
from ynca.function import IntFunctionMixin
from ynca.subunit import SubunitBase

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
def initialized_dummysubunit(connection: YncaConnectionMock) -> DummySubunit:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    sui = DummySubunit(connection)
    sui.initialize()
    return sui


def test_construct(
    connection: YncaConnectionMock,
    update_callback: mock.Mock,
) -> None:
    DummySubunit(connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_fail(
    connection: YncaConnectionMock,
    update_callback: mock.Mock,
) -> None:
    dsu = DummySubunit(connection)
    dsu.register_update_callback(update_callback)

    with pytest.raises(YncaInitializationFailedException):
        dsu.initialize()

    assert update_callback.call_count == 0


def test_initialize(
    connection: YncaConnectionMock,
    update_callback: mock.Mock,
) -> None:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    dsu = DummySubunit(connection)
    dsu.register_update_callback(update_callback)

    dsu.initialize()

    assert update_callback.call_count == 0
    assert dsu.avail == Avail.READY


def test_registration(
    connection: YncaConnectionMock, initialized_dummysubunit: SubunitBase
) -> None:
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


def test_close(
    connection: YncaConnectionMock, initialized_dummysubunit: SubunitBase
) -> None:
    initialized_dummysubunit.close()
    connection.unregister_message_callback.assert_called_once()

    # Should be safe to call multiple times
    initialized_dummysubunit.close()


def test_unknown_functions_ignored(
    connection: YncaConnectionMock,
    initialized_dummysubunit: SubunitBase,
    update_callback: mock.Mock,
) -> None:
    initialized_dummysubunit.register_update_callback(update_callback)
    connection.send_protocol_message(SUBUNIT, "UnknownFunction", "Value")
    assert update_callback.call_count == 0


def test_status_not_ok_ignored(
    connection: YncaConnectionMock,
    initialized_dummysubunit: SubunitBase,
    update_callback: mock.Mock,
) -> None:
    initialized_dummysubunit.register_update_callback(update_callback)
    connection.send_protocol_error("@UNDEFINED")
    assert update_callback.call_count == 0
    connection.send_protocol_error("@RESTRICTED")
    assert update_callback.call_count == 0


def test_write_function_calls_connection_put(
    connection: YncaConnectionMock,
    initialized_dummysubunit: DummySubunit,
) -> None:
    initialized_dummysubunit.dummy_function = 123
    connection.put.assert_called_with("UAW", "DUMMY_FUNCTION", "123")


def test_unreadable_attributes_ignored(connection: YncaConnectionMock) -> None:
    """Ensure handling of unreadable attributes as found with issue https://github.com/mvdwetering/yamaha_ynca/issues/315."""

    class Descriptor:
        def __get__(self, instance, owner):  # noqa: ANN001, ANN204
            msg = "unreadable attribute"
            raise AttributeError(msg)

    DummySubunit.__provides__ = Descriptor()  # type: ignore  # noqa: PGH003
    DummySubunit(connection)
