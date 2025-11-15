from collections.abc import Callable
from typing import Any

import pytest  # type: ignore[import]

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import BandTun, Tun

SYS = "SYS"
SUBUNIT = "TUN"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AMFREQ"),
        [
            (SUBUNIT, "AMFREQ", "1080"),
        ],
    ),
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
        (SUBUNIT, "FMFREQ"),
        [
            (SUBUNIT, "FMFREQ", "101.60"),
        ],
    ),
    (
        (SUBUNIT, "PRESET"),
        [
            (SUBUNIT, "PRESET", "12"),
        ],
    ),
    (
        (SUBUNIT, "RDSINFO"),
        [
            (SUBUNIT, "RDSPRGTYPE", "RDS PRG TYPE"),
            (SUBUNIT, "RDSPRGSERVICE", "RDS PRG SERVICE"),
            (SUBUNIT, "RDSTXTA", "RDS RADIO TEXT A"),
            (SUBUNIT, "RDSTXTB", "RDS RADIO TEXT B"),
            (SUBUNIT, "RDSCLOCK", "RDS CLOCK"),
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
def initialized_tun(connection: YncaConnectionMock) -> Tun:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    tun = Tun(connection)
    tun.initialize()
    return tun


def test_initialize(
    connection: YncaConnectionMock, update_callback: Callable[[str, Any], None]
) -> None:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    tun = Tun(connection)
    tun.register_update_callback(update_callback)

    tun.initialize()

    assert tun.band is BandTun.FM
    assert tun.amfreq == 1080
    assert tun.fmfreq == 101.60
    assert tun.preset == 12


def test_am(connection: YncaConnectionMock, initialized_tun: Tun) -> None:
    initialized_tun.band = BandTun.AM
    connection.put.assert_called_with(SUBUNIT, "BAND", "AM")

    # Set value and test stepsize handling (which is why it becomes 1000)
    initialized_tun.amfreq = 999
    connection.put.assert_called_with(SUBUNIT, "AMFREQ", "1000")


def test_fm(connection: YncaConnectionMock, initialized_tun: Tun) -> None:
    initialized_tun.band = BandTun.FM
    connection.put.assert_called_with(SUBUNIT, "BAND", "FM")

    # Set value and test stepsize handling (which is why it becomes 100.00)
    initialized_tun.fmfreq = 100.05
    connection.put.assert_called_with(SUBUNIT, "FMFREQ", "100.00")


def test_rds(connection: YncaConnectionMock, initialized_tun: Tun) -> None:
    # Updates from device
    connection.send_protocol_message(SUBUNIT, "RDSPRGSERVICE", "rds prg service")
    assert initialized_tun.rdsprgservice == "rds prg service"

    connection.send_protocol_message(SUBUNIT, "RDSPRGTYPE", "rds prg type")
    assert initialized_tun.rdsprgtype == "rds prg type"

    connection.send_protocol_message(SUBUNIT, "RDSTXTA", "radiotext a")
    assert initialized_tun.rdstxta == "radiotext a"

    connection.send_protocol_message(SUBUNIT, "RDSTXTB", "radiotext b")
    assert initialized_tun.rdstxtb == "radiotext b"


def test_preset(connection: YncaConnectionMock, initialized_tun: Tun) -> None:
    # Updates from device
    connection.send_protocol_message(SUBUNIT, "PRESET", "11")
    assert initialized_tun.preset == 11

    connection.send_protocol_message(SUBUNIT, "PRESET", "No Preset")
    assert initialized_tun.preset is None

    # Set preset
    initialized_tun.preset = 10
    connection.put.assert_called_with(SUBUNIT, "PRESET", "10")

    # Preset Up Down
    initialized_tun.preset_up()
    connection.put.assert_called_with(SUBUNIT, "PRESET", "Up")

    initialized_tun.preset_down()
    connection.put.assert_called_with(SUBUNIT, "PRESET", "Down")


def test_mem(connection: YncaConnectionMock, initialized_tun: Tun) -> None:
    # Store
    initialized_tun.mem(10)
    connection.put.assert_called_with(SUBUNIT, "MEM", "10")

    initialized_tun.mem()
    connection.put.assert_called_with(SUBUNIT, "MEM", "Auto")
