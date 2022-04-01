from ynca.constants import Playback
from ynca.bt import Bt

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


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    bt = Bt(connection)
    bt.register_update_callback(update_callback)

    bt.initialize()

    assert update_callback.call_count == 1

    bt.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
