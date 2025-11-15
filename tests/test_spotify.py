from collections.abc import Callable
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Playback, PlaybackInfo, Repeat, Shuffle, Spotify

SYS = "SYS"
SUBUNIT = "SPOTIFY"

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

    spotify = Spotify(connection)
    spotify.register_update_callback(update_callback)

    spotify.initialize()

    assert spotify.album == "Album"
    assert spotify.artist == "Artist"
    assert spotify.track == "Track"
    assert spotify.playbackinfo is PlaybackInfo.PAUSE
    assert spotify.repeat == Repeat.SINGLE
    assert spotify.shuffle == Shuffle.ON

    spotify.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
