from ynca.sirius import Sirius

SYS = "SYS"
SUBUNIT = "SIRIUS"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
        ],
    ),
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
        (SUBUNIT, "CHNAME"),
        [
            (SUBUNIT, "CHNAME", "ChName"),
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

    sirius = Sirius(connection)
    sirius.register_update_callback(update_callback)

    sirius.initialize()

    assert update_callback.call_count == 1
    assert sirius.album is None
    assert sirius.artist == "Artist"
    assert sirius.song == "Song"
    assert sirius.chname == "ChName"
