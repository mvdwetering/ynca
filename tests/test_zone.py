"""Test YNCA Zone"""

from typing import Callable
from unittest import mock
import pytest

from ynca.connection import YncaConnection, YncaProtocolStatus
from ynca.constants import Mute
from ynca.zone import Zone
from ynca.errors import YncaInitializationFailedException

from .connectionmock import YncaConnectionMock

SUBUNIT = "SUBUNIT"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "BASIC"),
        [
            (SUBUNIT, "PWR", "Standby"),
            (SUBUNIT, "SLEEP", "Off"),
            (SUBUNIT, "VOL", "-30.0"),
            (SUBUNIT, "MUTE", "Off"),
            (SUBUNIT, "INP", "HDMI1"),
            (SUBUNIT, "STRAIGHT", "Off"),
            (SUBUNIT, "ENHANCER", "On"),
            (SUBUNIT, "SOUNDPRG", "Standard"),
            (SUBUNIT, "3DCINEMA", "Auto"),
            (SUBUNIT, "PUREDIRMODE", "Off"),
            (SUBUNIT, "SPBASS", "Scene name 4"),
            (SUBUNIT, "SPTREBLE", "Scene name 4"),
            (SUBUNIT, "ADAPTIVEDRC", "Off"),
        ],
    ),
    (
        (SUBUNIT, "MAXVOL"),
        [
            (SUBUNIT, "MAXVOL", "1.2"),
        ],
    ),
    (
        (SUBUNIT, "SCENENAME"),
        [
            (SUBUNIT, "SCENE1NAME", "Scene name 1"),
            (SUBUNIT, "SCENE2NAME", "Scene name 2"),
            (SUBUNIT, "SCENE3NAME", "Scene name 3"),
            (SUBUNIT, "SCENE4NAME", "Scene name 4"),
        ],
    ),
    (
        (SUBUNIT, "ZONENAME"),
        [
            (SUBUNIT, "ZONENAME", "ZoneName"),
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


@pytest.fixture
def initialized_zone(connection) -> Zone:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    z = Zone(SUBUNIT, connection)
    z.initialize()
    return z


def test_construct(connection, update_callback):

    z = Zone(SUBUNIT, connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_fail(connection, update_callback):

    z = Zone(SUBUNIT, connection)
    z.register_update_callback(update_callback)

    with pytest.raises(YncaInitializationFailedException):
        z.initialize()

    assert update_callback.call_count == 0


def test_initialize_minimal(connection, update_callback):
    connection.get_response_list = [
        (
            (SUBUNIT, "ZONENAME"),
            [
                (SUBUNIT, "ZONENAME", "ZoneName"),
            ],
        ),
    ]

    z = Zone(SUBUNIT, connection)
    z.register_update_callback(update_callback)
    z.unregister_update_callback(update_callback)

    z.initialize()

    assert update_callback.call_count == 0
    assert z.name == "ZoneName"
    assert z.on is None
    assert z.input is None
    assert z.volume is None
    assert z.max_volume == 16.5
    assert z.min_volume == -80.5
    assert z.mute is None
    assert z.straight is None
    assert z.dsp_sound_program is None
    assert len(z.scenes.keys()) == 0


def test_initialize_full(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    z = Zone(SUBUNIT, connection)
    z.register_update_callback(update_callback)

    z.initialize()

    assert update_callback.call_count == 1
    assert z.on is False
    assert z.input == "HDMI1"
    assert z.volume == -30.0
    assert z.max_volume == 1.2
    assert z.min_volume == -80.5
    assert z.mute is Mute.off
    assert z.straight is False
    assert z.dsp_sound_program == "Standard"
    assert z.name == "ZoneName"

    assert len(z.scenes.keys()) == 4
    assert z.scenes["1"] == "Scene name 1"
    assert z.scenes["2"] == "Scene name 2"
    assert z.scenes["3"] == "Scene name 3"
    assert z.scenes["4"] == "Scene name 4"


def test_on(connection, initialized_zone):
    # Writing to device
    initialized_zone.on = True
    connection.put.assert_called_with(SUBUNIT, "PWR", "On")
    initialized_zone.on = False
    connection.put.assert_called_with(SUBUNIT, "PWR", "Standby")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "PWR", "On")
    assert initialized_zone.on == True
    connection.send_protocol_message(SUBUNIT, "PWR", "Standby")
    assert initialized_zone.on == False


def test_mute(connection, initialized_zone):
    # Writing to device
    initialized_zone.mute = Mute.on
    connection.put.assert_called_with(SUBUNIT, "MUTE", "On")
    initialized_zone.mute = Mute.att_minus_20
    connection.put.assert_called_with(SUBUNIT, "MUTE", "Att -20 dB")
    initialized_zone.mute = Mute.att_minus_40
    connection.put.assert_called_with(SUBUNIT, "MUTE", "Att -40 dB")
    initialized_zone.mute = Mute.off
    connection.put.assert_called_with(SUBUNIT, "MUTE", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "MUTE", "On")
    assert initialized_zone.mute is Mute.on
    connection.send_protocol_message(SUBUNIT, "MUTE", "Att -20 dB")
    assert initialized_zone.mute is Mute.att_minus_20
    connection.send_protocol_message(SUBUNIT, "MUTE", "Att -40 dB")
    assert initialized_zone.mute is Mute.att_minus_40
    connection.send_protocol_message(SUBUNIT, "MUTE", "Off")
    assert initialized_zone.mute is Mute.off


def test_volume(connection, initialized_zone):
    # Writing to device

    # Positive with step rounding
    initialized_zone.volume = 0
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.0")
    initialized_zone.volume = 0.1
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.0")
    initialized_zone.volume = 0.4
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.5")

    # Negative with step rounding
    initialized_zone.volume = -5
    connection.put.assert_called_with(SUBUNIT, "VOL", "-5.0")
    initialized_zone.volume = -0.5
    connection.put.assert_called_with(SUBUNIT, "VOL", "-0.5")
    initialized_zone.volume = -0.4
    connection.put.assert_called_with(SUBUNIT, "VOL", "-0.5")
    initialized_zone.volume = -0.1
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.0")

    # Out of range
    with pytest.raises(ValueError):
        initialized_zone.volume = initialized_zone.min_volume - 1
    with pytest.raises(ValueError):
        initialized_zone.volume = initialized_zone.max_volume + 1

    # Up
    initialized_zone.volume_up()
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up")
    initialized_zone.volume_up(1)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up 1 dB")
    initialized_zone.volume_up(2)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up 2 dB")
    initialized_zone.volume_up(5)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up 5 dB")
    initialized_zone.volume_up(50)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up")

    # Down
    initialized_zone.volume_down()
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down")
    initialized_zone.volume_down(1)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down 1 dB")
    initialized_zone.volume_down(2)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down 2 dB")
    initialized_zone.volume_down(5)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down 5 dB")
    initialized_zone.volume_down(50)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "VOL", "0.0")
    assert initialized_zone.volume == 0
    connection.send_protocol_message(SUBUNIT, "VOL", "10.0")
    assert initialized_zone.volume == 10
    connection.send_protocol_message(SUBUNIT, "VOL", "-10.0")
    assert initialized_zone.volume == -10


def test_input(connection, initialized_zone):
    # Writing to device
    initialized_zone.input = "Input"
    connection.put.assert_called_with(SUBUNIT, "INP", "Input")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "INP", "NewInput")
    assert initialized_zone.input == "NewInput"


def test_dsp_sound_program(connection, initialized_zone):
    # Writing to device
    with pytest.raises(ValueError):
        initialized_zone.dsp_sound_program = "Invalid"

    initialized_zone.dsp_sound_program = "The Roxy Theatre"
    connection.put.assert_called_with(SUBUNIT, "SOUNDPRG", "The Roxy Theatre")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SOUNDPRG", "Sci-Fi")
    assert initialized_zone.dsp_sound_program == "Sci-Fi"


def test_straight(connection, initialized_zone):
    # Writing to device
    initialized_zone.straight = True
    connection.put.assert_called_with(SUBUNIT, "STRAIGHT", "On")
    initialized_zone.straight = False
    connection.put.assert_called_with(SUBUNIT, "STRAIGHT", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "STRAIGHT", "On")
    assert initialized_zone.straight == True
    connection.send_protocol_message(SUBUNIT, "STRAIGHT", "Off")
    assert initialized_zone.straight == False


def test_scene(connection, initialized_zone):
    # Writing to device
    with pytest.raises(ValueError):
        initialized_zone.activate_scene("Invalid")

    initialized_zone.activate_scene("2")
    connection.put.assert_called_with(SUBUNIT, "SCENE", "Scene 2")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SCENE3NAME", "New Name")
    assert initialized_zone.scenes["3"] == "New Name"


def test_callbacks(connection, initialized_zone, update_callback):
    update_callback_2 = mock.MagicMock()

    # Register multiple callbacks, both get called
    initialized_zone.register_update_callback(update_callback)
    initialized_zone.register_update_callback(update_callback_2)
    connection.send_protocol_message(SUBUNIT, "VOL", "1")
    assert update_callback.call_count == 1
    assert update_callback_2.call_count == 1

    # Double registration (second gets ignored)
    initialized_zone.register_update_callback(update_callback_2)
    connection.send_protocol_message(SUBUNIT, "VOL", "1")
    assert update_callback.call_count == 2
    assert update_callback_2.call_count == 2

    # Unregistration
    initialized_zone.unregister_update_callback(update_callback_2)
    connection.send_protocol_message(SUBUNIT, "VOL", "1")
    assert update_callback.call_count == 3
    assert update_callback_2.call_count == 2
