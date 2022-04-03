"""Test Zone subunit"""

import pytest

from ynca.constants import Avail
from ynca.subunit import SubunitBase
from ynca.errors import YncaInitializationFailedException


SYS = "SYS"
SUBUNIT = "SUBUNIT"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
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
    id = SUBUNIT


@pytest.fixture
def initialized_SubunitBase(connection) -> DummySubunit:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    sui = DummySubunit(connection)
    sui.initialize()
    return sui


def test_construct(connection, update_callback):

    sui = DummySubunit(connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_fail(connection, update_callback):

    sui = DummySubunit(connection)
    sui.register_update_callback(update_callback)

    with pytest.raises(YncaInitializationFailedException):
        sui.initialize()

    assert update_callback.call_count == 0


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    sui = DummySubunit(connection)
    sui.register_update_callback(update_callback)

    sui.initialize()

    assert update_callback.call_count == 1
    assert sui.avail == Avail.READY


def test_close(connection, initialized_SubunitBase):

    initialized_SubunitBase.close()
    connection.unregister_message_callback.assert_called_once()

    # Should be safe to call multiple times
    initialized_SubunitBase.close()
    connection.unregister_message_callback.assert_called_once()


def test_unknown_functions_ignored(
    connection, initialized_SubunitBase, update_callback
):
    initialized_SubunitBase.register_update_callback(update_callback)
    connection.send_protocol_message(SUBUNIT, "UnknownFunction", "Value")
    assert update_callback.call_count == 0


def test_status_not_ok_ignored(connection, initialized_SubunitBase, update_callback):
    initialized_SubunitBase.register_update_callback(update_callback)
    connection.send_protocol_error("@UNDEFINED")
    assert update_callback.call_count == 0
    connection.send_protocol_error("@RESTRICTED")
    assert update_callback.call_count == 0
