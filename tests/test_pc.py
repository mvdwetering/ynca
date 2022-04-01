from ynca.constants import Playback, PlaybackInfo, Repeat
from ynca.pc import Pc

SYS = "SYS"
SUBUNIT = "PC"

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

    pc = Pc(connection)
    pc.register_update_callback(update_callback)

    pc.initialize()

    assert update_callback.call_count == 1
    assert pc.repeat is Repeat.SINGLE
    assert pc.shuffle is True
    assert pc.album == "Album"
    assert pc.artist == "Artist"
    assert pc.song == "Song"
    assert pc.playbackinfo is PlaybackInfo.PAUSE

    pc.repeat = Repeat.ALL
    connection.put.assert_called_with(SUBUNIT, "REPEAT", "All")
    pc.shuffle = False
    connection.put.assert_called_with(SUBUNIT, "SHUFFLE", "Off")
    pc.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
