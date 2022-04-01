from ynca.constants import Playback, PlaybackInfo
from ynca.netradio import NetRadio

SYS = "SYS"
SUBUNIT = "NETRADIO"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
        ],
    ),
    (
        (SUBUNIT, "PLAYBACKINFO"),
        [
            (SUBUNIT, "PLAYBACKINFO", "Play"),
        ],
    ),
    (
        (SUBUNIT, "STATION"),
        [
            (SUBUNIT, "STATION", "Station"),
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

    netradio = NetRadio(connection)
    netradio.register_update_callback(update_callback)

    netradio.initialize()

    assert update_callback.call_count == 1
    assert netradio.station == "Station"
    assert netradio.playbackinfo is PlaybackInfo.PLAY

    netradio.playback(Playback.STOP)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Stop")
