from ynca.constants import Playback, PlaybackInfo, Repeat
from ynca.ipod import Ipod

SYS = "SYS"
SUBUNIT = "IPOD"

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

    ipod = Ipod(connection)
    ipod.register_update_callback(update_callback)

    ipod.initialize()

    assert update_callback.call_count == 1
    assert ipod.repeat is Repeat.SINGLE
    assert ipod.shuffle is True
    assert ipod.album == "Album"
    assert ipod.artist == "Artist"
    assert ipod.song == "Song"
    assert ipod.playbackinfo is PlaybackInfo.PAUSE

    ipod.repeat = Repeat.ALL
    connection.put.assert_called_with(SUBUNIT, "REPEAT", "All")
    ipod.shuffle = False
    connection.put.assert_called_with(SUBUNIT, "SHUFFLE", "Off")
    ipod.playback(Playback.PLAY)
    connection.put.assert_called_with(SUBUNIT, "PLAYBACK", "Play")
