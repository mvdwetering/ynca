from ynca.constants import Playback, PlaybackInfo, Repeat
from ynca.rhap import Rhap

SYS = "SYS"
SUBUNIT = "RHAP"

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


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    rhap = Rhap(connection)
    rhap.register_update_callback(update_callback)

    rhap.initialize()

    assert update_callback.call_count == 1
    assert rhap.repeat is Repeat.SINGLE
    assert rhap.shuffle is True
    assert rhap.album == "Album"
    assert rhap.artist == "Artist"
    assert rhap.song == "Song"
    assert rhap.playbackinfo is PlaybackInfo.PAUSE

    rhap.repeat = Repeat.ALL
    connection.put.assert_called_with(SUBUNIT, "REPEAT", "All")
    rhap.shuffle = False
    connection.put.assert_called_with(SUBUNIT, "SHUFFLE", "Off")
    rhap.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
