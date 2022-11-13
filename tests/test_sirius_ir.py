from ynca import PlaybackInfo, Playback
from ynca.subunits.sirius import SiriusIr

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


def test_initialize(connection, update_callback):

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
