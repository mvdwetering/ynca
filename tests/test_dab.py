import pytest

from ynca import BandDab, Preset
from ynca.function_enums import (
    AssertNegate,
    BandDab,
    DabAudioMode,
    DabOffAir,
    FmSigStereoMono,
    FmTuned,
)
from ynca.subunits.dab import Dab

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
        (SUBUNIT, "FMFREQ"),
        [
            (SUBUNIT, "FMFREQ", "101.60"),
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
            ),  # DAB is a bit weird, but it came from a log
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
def initialized_dab(connection) -> Dab:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    dab = Dab(connection)
    dab.initialize()
    return dab


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    dab = Dab(connection)
    dab.register_update_callback(update_callback)

    dab.initialize()

    assert dab.band is BandDab.FM
    assert dab.fmfreq == 101.60
    assert dab.fmpreset is None


def test_band(connection, initialized_dab: Dab):

    initialized_dab.band = BandDab.DAB
    connection.put.assert_called_with(SUBUNIT, "BAND", "DAB")

    connection.send_protocol_message(SUBUNIT, "BAND", "FM")
    assert initialized_dab.band is BandDab.FM

    initialized_dab.band = BandDab.FM
    connection.put.assert_called_with(SUBUNIT, "BAND", "FM")

    connection.send_protocol_message(SUBUNIT, "BAND", "DAB")
    assert initialized_dab.band is BandDab.DAB


def test_dab(connection, initialized_dab: Dab):

    connection.send_protocol_message(SUBUNIT, "DABAUDIOMODE", "Stereo")
    assert initialized_dab.dabaudiomode is DabAudioMode.STEREO

    connection.send_protocol_message(SUBUNIT, "DABCHLABEL", "dab ch label")
    assert initialized_dab.dabchlabel == "dab ch label"

    connection.send_protocol_message(SUBUNIT, "DABDLSLABEL", "dab dls label")
    assert initialized_dab.dabdlslabel == "dab dls label"

    connection.send_protocol_message(SUBUNIT, "DABENSEMBLELABEL", "dab ensemble label")
    assert initialized_dab.dabensemblelabel == "dab ensemble label"

    connection.send_protocol_message(SUBUNIT, "DABOFFAIR", "Negate")
    assert initialized_dab.daboffair is DabOffAir.NEGATE

    connection.send_protocol_message(SUBUNIT, "DABPRGTYPE", "dab prog type")
    assert initialized_dab.dabprgtype == "dab prog type"

    connection.send_protocol_message(SUBUNIT, "DABSERVICELABEL", "dab service label")
    assert initialized_dab.dabservicelabel == "dab service label"


def test_dabpreset(connection, initialized_dab: Dab):

    # Writing to device
    initialized_dab.dabpreset = 33
    connection.put.assert_called_with(SUBUNIT, "DABPRESET", "33")

    initialized_dab.dabpreset_down()
    connection.put.assert_called_with(SUBUNIT, "DABPRESET", "Down")

    initialized_dab.dabpreset_up()
    connection.put.assert_called_with(SUBUNIT, "DABPRESET", "Up")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "DABPRESET", "42")
    assert initialized_dab.dabpreset == 42
    connection.send_protocol_message(SUBUNIT, "DABPRESET", "No Preset")
    assert initialized_dab.dabpreset is Preset.NO_PRESET


def test_fmpreset(connection, initialized_dab: Dab):

    # Writing to device
    initialized_dab.fmpreset = 33
    connection.put.assert_called_with(SUBUNIT, "FMPRESET", "33")

    initialized_dab.fmpreset_down()
    connection.put.assert_called_with(SUBUNIT, "FMPRESET", "Down")

    initialized_dab.fmpreset_up()
    connection.put.assert_called_with(SUBUNIT, "FMPRESET", "Up")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "FMPRESET", "42")
    assert initialized_dab.fmpreset == 42
    connection.send_protocol_message(SUBUNIT, "FMPRESET", "No Preset")
    assert initialized_dab.fmpreset is Preset.NO_PRESET


def test_fmrds(connection, initialized_dab: Dab):

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "FMRDSPRGSERVICE", "rds prg service")
    assert initialized_dab.fmrdsprgservice == "rds prg service"

    connection.send_protocol_message(SUBUNIT, "FMRDSPRGTYPE", "rds prg type")
    assert initialized_dab.fmrdsprgtype == "rds prg type"

    connection.send_protocol_message(SUBUNIT, "FMRDSTXT", "radiotext")
    assert initialized_dab.fmrdstxt == "radiotext"


def test_fmsignal(connection, initialized_dab: Dab):

    # Set value and test stepsize handling (which is why it becomes 100.00)
    initialized_dab.fmfreq = 100.05
    connection.put.assert_called_with(SUBUNIT, "FMFREQ", "100.00")

    connection.send_protocol_message(SUBUNIT, "FMSIGSTEREOMONO", "Assert")
    assert initialized_dab.fmsigstereomono is FmSigStereoMono.ASSERT
    connection.send_protocol_message(SUBUNIT, "FMSIGSTEREOMONO", "Negate")
    assert initialized_dab.fmsigstereomono is FmSigStereoMono.NEGATE

    connection.send_protocol_message(SUBUNIT, "FMTUNED", "Assert")
    assert initialized_dab.fmtuned is FmTuned.ASSERT
    connection.send_protocol_message(SUBUNIT, "FMTUNED", "Negate")
    assert initialized_dab.fmtuned is FmTuned.NEGATE
