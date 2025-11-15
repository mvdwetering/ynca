from collections.abc import Callable
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import McLink, PlaybackInfo

SYS = "SYS"
SUBUNIT = "MCLINK"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "METAINFO"),
        [
            (SUBUNIT, "ALBUM", "Album"),
            (SUBUNIT, "ARTIST", "Artist"),
            (SUBUNIT, "SONG", "Song"),
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

    mclink = McLink(connection)
    mclink.register_update_callback(update_callback)

    mclink.initialize()

    assert mclink.album == "Album"
    assert mclink.artist == "Artist"
    assert mclink.song == "Song"
    assert mclink.playbackinfo is PlaybackInfo.PAUSE
    assert mclink.elapsedtime is None
