from collections.abc import Callable
from typing import Any

import pytest

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import BandDab, Dab, DabPreset, FmPreset

SYS = "SYS"
SUBUNIT = "DAB"

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
        (SUBUNIT, "DABPRESET"),
        [
            (SUBUNIT, "DABPRESET", "33"),
        ],
    ),
    (
        (SUBUNIT, "FMFREQ"),
        [
            (SUBUNIT, "FMFREQ", "101.60"),
        ],
    ),
    (
        (SUBUNIT, "FMPRESET"),
        [
            (SUBUNIT, "FMPRESET", "40"),
        ],
    ),
    (
        (SUBUNIT, "FMRDSINFO"),
        [
            (SUBUNIT, "FMRDSPRGTYPE", "RDS PRG TYPE"),
            (SUBUNIT, "FMRDSPRGSERVICE", "RDS PRG SERVICE"),
            (SUBUNIT, "FMRDSTXT", "RDS RADIO TEXT"),
            (SUBUNIT, "FMRDSCLOCK", "RDS CLOCK"),
            (
                SUBUNIT,
                "DABDATETIME",
                "13DEC'22 11:05",
            ),  # DAB is a bit weird, but it came from a log OF RX-V500D
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
def initialized_dab(
    connection: YncaConnectionMock,
) -> Dab:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    dab = Dab(connection)
    dab.initialize()
    return dab


def test_initialize(
    connection: YncaConnectionMock, update_callback: Callable[[str, Any], None]
) -> None:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    dab = Dab(connection)
    dab.register_update_callback(update_callback)

    dab.initialize()

    assert dab.band is BandDab.FM
    assert dab.fmfreq == 101.60


def test_band(connection: YncaConnectionMock, initialized_dab: Dab) -> None:
    initialized_dab.band = BandDab.DAB
    connection.put.assert_called_with(SUBUNIT, "BAND", "DAB")

    connection.send_protocol_message(SUBUNIT, "BAND", "FM")
    assert initialized_dab.band is BandDab.FM

    initialized_dab.band = BandDab.FM
    connection.put.assert_called_with(SUBUNIT, "BAND", "FM")

    connection.send_protocol_message(SUBUNIT, "BAND", "DAB")
    assert initialized_dab.band is BandDab.DAB


def test_dab(connection: YncaConnectionMock, initialized_dab: Dab) -> None:
    connection.send_protocol_message(SUBUNIT, "DABCHLABEL", "dab ch label")
    assert initialized_dab.dabchlabel == "dab ch label"

    connection.send_protocol_message(SUBUNIT, "DABDLSLABEL", "dab dls label")
    assert initialized_dab.dabdlslabel == "dab dls label"

    connection.send_protocol_message(SUBUNIT, "DABENSEMBLELABEL", "dab ensemble label")
    assert initialized_dab.dabensemblelabel == "dab ensemble label"

    connection.send_protocol_message(SUBUNIT, "DABPRGTYPE", "dab prog type")
    assert initialized_dab.dabprgtype == "dab prog type"

    connection.send_protocol_message(SUBUNIT, "DABSERVICELABEL", "dab service label")
    assert initialized_dab.dabservicelabel == "dab service label"


def test_fmrds(connection: YncaConnectionMock, initialized_dab: Dab) -> None:
    # Updates from device
    connection.send_protocol_message(SUBUNIT, "FMRDSPRGSERVICE", "rds prg service")
    assert initialized_dab.fmrdsprgservice == "rds prg service"

    connection.send_protocol_message(SUBUNIT, "FMRDSPRGTYPE", "rds prg type")
    assert initialized_dab.fmrdsprgtype == "rds prg type"

    connection.send_protocol_message(SUBUNIT, "FMRDSTXT", "radiotext")
    assert initialized_dab.fmrdstxt == "radiotext"


def test_fmfreq(connection: YncaConnectionMock, initialized_dab: Dab) -> None:
    # Set value and test stepsize handling (which is why it becomes 100.00)
    initialized_dab.fmfreq = 100.05
    connection.put.assert_called_with(SUBUNIT, "FMFREQ", "100.00")


def test_fmpreset(connection: YncaConnectionMock, initialized_dab: Dab) -> None:
    assert initialized_dab.fmpreset == 40

    initialized_dab.fmpreset = 12
    connection.put.assert_called_with(SUBUNIT, "FMPRESET", "12")

    connection.send_protocol_message(SUBUNIT, "FMPRESET", "No Preset")
    initialized_dab.fmpreset = FmPreset.NO_PRESET


def test_dabpreset(connection: YncaConnectionMock, initialized_dab: Dab) -> None:
    assert initialized_dab.dabpreset == 33

    initialized_dab.dabpreset = 22
    connection.put.assert_called_with(SUBUNIT, "DABPRESET", "22")

    connection.send_protocol_message(SUBUNIT, "DABPRESET", "No Preset")
    initialized_dab.dabpreset = DabPreset.NO_PRESET
