from collections.abc import Callable
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Bt, Playback

SYS = "SYS"
SUBUNIT = "BT"

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


def test_initialize(
    connection: YncaConnectionMock, update_callback: Callable[[str, Any], None]
) -> None:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    bt = Bt(connection)
    bt.register_update_callback(update_callback)

    bt.initialize()

    bt.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
