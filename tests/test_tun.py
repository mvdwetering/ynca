import pytest

from ynca import BandTun, Preset, SigStereoMono, Tuned
from ynca.enums import AssertNegate
from ynca.subunits.tun import Tun

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
def initialized_tun(connection) -> Tun:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    tun = Tun(connection)
    tun.initialize()
    return tun


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    tun = Tun(connection)
    tun.register_update_callback(update_callback)

    tun.initialize()

    assert tun.band is BandTun.FM
    assert tun.amfreq == 1080
    assert tun.fmfreq == 101.60
    assert tun.preset is None


def test_am(connection, initialized_tun: Tun):

    initialized_tun.band = BandTun.AM
    connection.put.assert_called_with(SUBUNIT, "BAND", "AM")

    # Set value and test stepsize handling (which is why it becomes 1000)
    initialized_tun.amfreq = 999
    connection.put.assert_called_with(SUBUNIT, "AMFREQ", "1000")


def test_fm(connection, initialized_tun: Tun):

    initialized_tun.band = BandTun.FM
    connection.put.assert_called_with(SUBUNIT, "BAND", "FM")

    # Set value and test stepsize handling (which is why it becomes 100.00)
    initialized_tun.fmfreq = 100.05
    connection.put.assert_called_with(SUBUNIT, "FMFREQ", "100.00")


def test_preset(connection, initialized_tun: Tun):

    # Writing to device
    initialized_tun.preset = 33
    connection.put.assert_called_with(SUBUNIT, "PRESET", "33")

    initialized_tun.preset_down()
    connection.put.assert_called_with(SUBUNIT, "PRESET", "Down")

    initialized_tun.preset_up()
    connection.put.assert_called_with(SUBUNIT, "PRESET", "Up")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "PRESET", "42")
    assert initialized_tun.preset == 42
    connection.send_protocol_message(SUBUNIT, "PRESET", "No Preset")
    assert initialized_tun.preset is Preset.NO_PRESET


def test_rds(connection, initialized_tun: Tun):

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "RDSPRGSERVICE", "rds prg service")
    assert initialized_tun.rdsprgservice == "rds prg service"

    connection.send_protocol_message(SUBUNIT, "RDSPRGTYPE", "rds prg type")
    assert initialized_tun.rdsprgtype == "rds prg type"

    connection.send_protocol_message(SUBUNIT, "RDSTXTA", "radiotext a")
    assert initialized_tun.rdstxta == "radiotext a"

    connection.send_protocol_message(SUBUNIT, "RDSTXTB", "radiotext b")
    assert initialized_tun.rdstxtb == "radiotext b"


def test_signal(connection, initialized_tun: Tun):

    connection.send_protocol_message(SUBUNIT, "SIGSTEREOMONO", "Assert")
    assert initialized_tun.sigstereomono is AssertNegate.ASSERT
    connection.send_protocol_message(SUBUNIT, "SIGSTEREOMONO", "Negate")
    assert initialized_tun.sigstereomono is AssertNegate.NEGATE

    connection.send_protocol_message(SUBUNIT, "TUNED", "Assert")
    assert initialized_tun.tuned is AssertNegate.ASSERT
    connection.send_protocol_message(SUBUNIT, "TUNED", "Negate")
    assert initialized_tun.tuned is AssertNegate.NEGATE
