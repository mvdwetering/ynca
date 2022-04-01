"""Test Usb subunit"""

from typing import Callable
from unittest import mock
import pytest
from ynca.constants import PlaybackInfo, Repeat

from ynca.usb import Usb

from .mock_yncaconnection import YncaConnectionMock

SYS = "SYS"
SUBUNIT = "USB"

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

def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    usb = Usb(connection)
    usb.register_update_callback(update_callback)

    usb.initialize()

    assert update_callback.call_count == 1
    assert usb.repeat is Repeat.SINGLE
    assert usb.shuffle is True
    assert usb.album == "Album"
    assert usb.artist == "Artist"
    assert usb.song == "Song"
    assert usb.playbackinfo is PlaybackInfo.PAUSE

    usb.repeat = Repeat.ALL
    connection.put.assert_called_with(SUBUNIT, "REPEAT", "All")
    usb.shuffle = False
    connection.put.assert_called_with(SUBUNIT, "SHUFFLE", "Off")