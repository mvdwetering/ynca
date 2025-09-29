from collections.abc import Callable
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Playback, PlaybackInfo, Repeat, Shuffle
from ynca.subunits.tidal import Tidal

SYS = "SYS"
SUBUNIT = "TIDAL"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "METAINFO"),
        [
            (SUBUNIT, "ALBUM", "Album"),
            (SUBUNIT, "ARTIST", "Artist"),
            (SUBUNIT, "TRACK", "Track"),
        ],
    ),
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
        ],
    ),
    (
        (SUBUNIT, "PLAYBACKINFO"),
        [
            (SUBUNIT, "PLAYBACKINFO", "Pause"),
        ],
    ),
    (
        (SUBUNIT, "REPEAT"),
        [
            (SUBUNIT, "REPEAT", "Single"),
        ],
    ),
    (
        (SUBUNIT, "SHUFFLE"),
        [
            (SUBUNIT, "SHUFFLE", "On"),
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

    tidal = Tidal(connection)
    tidal.register_update_callback(update_callback)

    tidal.initialize()

    assert tidal.album == "Album"
    assert tidal.artist == "Artist"
    assert tidal.track == "Track"
    assert tidal.playbackinfo is PlaybackInfo.PAUSE
    assert tidal.repeat == Repeat.SINGLE
    assert tidal.shuffle == Shuffle.ON

    tidal.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
