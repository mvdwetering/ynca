from ynca.constants import Playback, PlaybackInfo
from ynca.pandora import Pandora

SYS = "SYS"
SUBUNIT = "PANDORA"

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
            (SUBUNIT, "PLAYBACKINFO", "Pause"),
        ],
    ),
    (
        (SUBUNIT, "METAINFO"),
        [
            (SUBUNIT, "ALBUM", "Album"),
            (SUBUNIT, "ARTIST", "Artist"),
            (SUBUNIT, "SONG", "Song"),
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

    pandora = Pandora(connection)
    pandora.register_update_callback(update_callback)

    pandora.initialize()

    assert update_callback.call_count == 1
    assert pandora.album == "Album"
    assert pandora.artist == "Artist"
    assert pandora.song == "Song"
    assert pandora.station == "Station"
    assert pandora.playbackinfo is PlaybackInfo.PAUSE

    pandora.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
