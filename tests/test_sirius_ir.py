from collections.abc import Callable
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Playback, PlaybackInfo, SiriusIr

SYS = "SYS"
SUBUNIT = "SIRIUSIR"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "METAINFO"),
        [
            (SUBUNIT, "CATNAME", "CatName"),
            (SUBUNIT, "CHNUM", "ChNum"),
            (SUBUNIT, "CHNAME", "ChName"),
            (SUBUNIT, "ARTIST", "Artist"),
            (SUBUNIT, "SONG", "Song"),
            (SUBUNIT, "COMPOSER", "Composer"),
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
            (SUBUNIT, "PLAYBACKINFO", "Stop"),
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

    siriusir = SiriusIr(connection)
    siriusir.register_update_callback(update_callback)

    siriusir.initialize()

    assert siriusir.artist == "Artist"
    assert siriusir.song == "Song"
    assert siriusir.chname == "ChName"
    assert siriusir.playbackinfo is PlaybackInfo.STOP

    siriusir.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
