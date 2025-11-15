from collections.abc import Callable
from datetime import timedelta
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Deezer, Playback, PlaybackInfo, Repeat, Shuffle

SYS = "SYS"
SUBUNIT = "DEEZER"

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
        (SUBUNIT, "ELAPSEDTIME"),
        [
            (SUBUNIT, "ELAPSEDTIME", ""),
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
        (SUBUNIT, "TOTALTIME"),
        [
            (SUBUNIT, "TOTALTIME", "1:23"),
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

    tidal = Deezer(connection)
    tidal.register_update_callback(update_callback)

    tidal.initialize()

    assert tidal.album == "Album"
    assert tidal.artist == "Artist"
    assert tidal.track == "Track"
    assert tidal.playbackinfo is PlaybackInfo.PAUSE
    assert tidal.repeat == Repeat.SINGLE
    assert tidal.shuffle == Shuffle.ON
    assert tidal.elapsedtime is None
    assert tidal.totaltime == timedelta(minutes=1, seconds=23)

    tidal.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
