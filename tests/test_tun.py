"""Test Usb subunit"""

from ynca.constants import Band
from ynca.tun import Tun


SYS = "SYS"
SUBUNIT = "TUN"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
        ],
    ),
    (
        (SUBUNIT, "BAND"),
        [
            (SUBUNIT, "BAND", "FM"),
        ],
    ),
    (
        (SUBUNIT, "AMFREQ"),
        [
            (SUBUNIT, "AMFREQ", "1080"),
        ],
    ),
    (
        (SUBUNIT, "FMFREQ"),
        [
            (SUBUNIT, "FMFREQ", "101.60"),
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

    tun = Tun(connection)
    tun.register_update_callback(update_callback)

    tun.initialize()

    assert update_callback.call_count == 1
    assert tun.band is Band.FM
    assert tun.amfreq == 1080
    assert tun.fmfreq == 101.60

    tun.band = Band.AM
    connection.put.assert_called_with(SUBUNIT, "BAND", "AM")
    tun.amfreq = 999
    connection.put.assert_called_with(SUBUNIT, "AMFREQ", "1000")
    tun.fmfreq = 100.05
    connection.put.assert_called_with(SUBUNIT, "FMFREQ", "100.00")
