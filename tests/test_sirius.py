from collections.abc import Callable
from typing import Any

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import Sirius, SiriusSearchMode

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
        (SUBUNIT, "SEARCHMODE"),
        [
            (SUBUNIT, "SEARCHMODE", "Preset"),
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
    assert sirius.searchmode == SiriusSearchMode.PRESET


def test_searchmode(
    connection: YncaConnectionMock, update_callback: Callable[[str, Any], None]
) -> None:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    sirius = Sirius(connection)
    sirius.initialize()

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SEARCHMODE", "All Ch")
    assert sirius.searchmode == SiriusSearchMode.ALL_CH

    connection.send_protocol_message(SUBUNIT, "SEARCHMODE", "Category")
    assert sirius.searchmode == SiriusSearchMode.CATEGORY

    connection.send_protocol_message(SUBUNIT, "SEARCHMODE", "Preset")
    assert sirius.searchmode == SiriusSearchMode.PRESET

    # Set
    sirius.searchmode = SiriusSearchMode.ALL_CH
    connection.put.assert_called_with(SUBUNIT, "SEARCHMODE", "All Ch")

    sirius.searchmode = SiriusSearchMode.CATEGORY
    connection.put.assert_called_with(SUBUNIT, "SEARCHMODE", "Category")
