from collections.abc import Callable
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Sirius

SYS = "SYS"
SUBUNIT = "SIRIUS"

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

    sirius = Sirius(connection)
    sirius.register_update_callback(update_callback)

    sirius.initialize()

    assert sirius.artist == "Artist"
    assert sirius.song == "Song"
    assert sirius.chname == "ChName"
