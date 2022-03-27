"""Test Zone subunit"""

from typing import Callable
from unittest import mock
import pytest

from ynca.subunit import SubunitBase
from ynca.errors import YncaInitializationFailedException

from .mock_yncaconnection import YncaConnectionMock


class SubunitImpl(SubunitBase):
    def on_initialize(self):
        """
        Just a dummy to avoid NotImplementedError being raised
        """
        pass


SYS = "SYS"
SUBUNIT = "SUBUNIT"

INITIALIZE_FULL_RESPONSES = [
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
]


@pytest.fixture
def connection():
    c = YncaConnectionMock()
    c.setup_responses()
    return c


@pytest.fixture
def update_callback() -> Callable[[], None]:
    return mock.MagicMock()


@pytest.fixture
def initialized_subunitimpl(connection) -> SubunitImpl:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    sui = SubunitImpl(SUBUNIT, connection)
    sui.initialize()
    return sui


def test_construct(connection, update_callback):

    sui = SubunitImpl(SUBUNIT, connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_fail(connection, update_callback):

    sui = SubunitImpl(SUBUNIT, connection)
    sui.register_update_callback(update_callback)

    with pytest.raises(YncaInitializationFailedException):
        sui.initialize()

    assert update_callback.call_count == 0


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    sui = SubunitImpl(SUBUNIT, connection)
    sui.register_update_callback(update_callback)

    sui.initialize()

    assert update_callback.call_count == 1


def test_unknown_functions_ignored(
    connection, initialized_subunitimpl, update_callback
):
    initialized_subunitimpl.register_update_callback(update_callback)
    connection.send_protocol_message(SUBUNIT, "UnknownFunction", "Value")
    assert update_callback.call_count == 0


def test_status_not_ok_ignored(connection, initialized_subunitimpl, update_callback):
    initialized_subunitimpl.register_update_callback(update_callback)
    connection.send_protocol_error("@UNDEFINED")
    assert update_callback.call_count == 0
    connection.send_protocol_error("@RESTRICTED")
    assert update_callback.call_count == 0
