"""Test Pc subunit"""

from typing import Callable
from unittest import mock
import pytest
from ynca.constants import PlaybackInfo, Repeat

from ynca.pc import Pc

from .mock_yncaconnection import YncaConnectionMock

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


@pytest.fixture
def connection():
    c = YncaConnectionMock()
    c.setup_responses()
    return c


@pytest.fixture
def update_callback() -> Callable[[], None]:
    return mock.MagicMock()


def test_construct(connection, update_callback):

    pc = Pc(connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


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
