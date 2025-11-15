from collections.abc import Callable
from typing import Any
from unittest import mock

import pytest

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import (
    DirMode,
    InitVolLvl,
    InitVolMode,
    Input,
    Main,
    Mute,
    PureDirMode,
    Pwr,
    PwrB,
    SoundPrg,
    SpeakerA,
    SpeakerB,
    Straight,
    SurroundAI,
    TwoChDecoder,
    ZoneBase,
    ZoneBMute,
)

SYS = "SYS"
SUBUNIT = "MAIN"
NUM_SCENES = 12

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
        ],
    ),
    (
        (SUBUNIT, "BASIC"),
        [
            (SUBUNIT, "PWR", "Standby"),
            (SUBUNIT, "PWRB", "On"),
            (SUBUNIT, "SLEEP", "Off"),
            (SUBUNIT, "VOL", "-30.0"),
            (SUBUNIT, "MUTE", "Off"),
            (SUBUNIT, "ZONEBAVAIL", "Ready"),
            (SUBUNIT, "ZONEBVOL", "-20.5"),
            (SUBUNIT, "ZONEBMUTE", "On"),
            (SUBUNIT, "INP", "HDMI1"),
            (SUBUNIT, "STRAIGHT", "Off"),
            (SUBUNIT, "ENHANCER", "On"),
            (SUBUNIT, "SOUNDPRG", "Standard"),
            (SUBUNIT, "3DCINEMA", "Auto"),
            (SUBUNIT, "PUREDIRMODE", "Off"),
            (SUBUNIT, "SPBASS", "4"),
            (SUBUNIT, "SPTREBLE", "-4"),
            (SUBUNIT, "ADAPTIVEDRC", "Off"),
            (SUBUNIT, "SPEAKERA", "Off"),
            (SUBUNIT, "SPEAKERB", "On"),
            (SUBUNIT, "DIRMODE", "On"),
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
            (SUBUNIT, "SCENE5NAME", "Scene name 5"),
            (SUBUNIT, "SCENE6NAME", "Scene name 6"),
            (SUBUNIT, "SCENE7NAME", "Scene name 7"),
            (SUBUNIT, "SCENE8NAME", "Scene name 8"),
            (SUBUNIT, "SCENE9NAME", "Scene name 9"),
            (SUBUNIT, "SCENE10NAME", "Scene name 10"),
            (SUBUNIT, "SCENE11NAME", "Scene name 11"),
            (SUBUNIT, "SCENE12NAME", "Scene name 12"),
        ],
    ),
    (
        (SUBUNIT, "2CHDECODER"),
        [
            (SUBUNIT, "2CHDECODER", "Dolby PLIIx Movie"),
        ],
    ),
    (
        (SUBUNIT, "ZONEBNAME"),
        [
            (SUBUNIT, "ZONEBNAME", "ZoneBName"),
        ],
    ),
    (
        (SUBUNIT, "ZONENAME"),
        [
            (SUBUNIT, "ZONENAME", "ZoneName"),
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
def update_callback() -> Callable[[], None]:
    return mock.MagicMock()


@pytest.fixture
def initialized_zone(
    connection: YncaConnectionMock,
) -> ZoneBase:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    z = Main(connection)
    z.initialize()
    return z


def test_construct(connection: YncaConnectionMock, update_callback: mock.Mock) -> None:
    Main(connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_minimal(
    connection: YncaConnectionMock, update_callback: mock.Mock
) -> None:
    connection.get_response_list = [
        (
            (SUBUNIT, "ZONENAME"),
            [
                (SUBUNIT, "ZONENAME", "ZoneName"),
            ],
        ),
        (
            (SYS, "VERSION"),
            [
                (SYS, "VERSION", "Version"),
            ],
        ),
    ]

    z = Main(connection)
    z.register_update_callback(update_callback)
    z.unregister_update_callback(update_callback)

    z.initialize()

    assert update_callback.call_count == 0
    assert z.zonename == "ZoneName"
    assert z.pwr is None
    assert z.inp is None
    assert z.vol is None
    assert z.maxvol is None
    assert z.mute is None
    assert z.straight is None
    assert z.soundprg is None
    assert z.twochdecoder is None
    assert z.puredirmode is None
    assert z.dirmode is None
    for scene_id in range(1, NUM_SCENES + 1):
        assert getattr(z, f"scene{scene_id}name") is None


def test_initialize_full(
    connection: YncaConnectionMock, update_callback: Callable[[str, Any], None]
) -> None:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    z = Main(connection)
    z.register_update_callback(update_callback)

    z.initialize()

    assert z.pwr is Pwr.STANDBY
    assert z.inp == Input.HDMI1
    assert z.vol == -30.0
    assert z.maxvol == 1.2
    assert z.mute is Mute.OFF
    assert z.straight is Straight.OFF
    assert z.soundprg is SoundPrg.STANDARD
    assert z.zonename == "ZoneName"
    assert z.twochdecoder is TwoChDecoder.DolbyPl2xMovie
    assert z.puredirmode is PureDirMode.OFF
    assert z.dirmode is DirMode.ON

    for scene_id in range(1, NUM_SCENES + 1):
        assert getattr(z, f"scene{scene_id}name") == f"Scene name {scene_id}"

    assert z.pwrb is PwrB.ON
    assert z.zonebmute is ZoneBMute.ON
    assert z.zonebname == "ZoneBName"
    assert z.zonebvol == -20.5
    assert z.speakera is SpeakerA.OFF
    assert z.speakerb is SpeakerB.ON


def test_mute(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.mute = Mute.ON
    connection.put.assert_called_with(SUBUNIT, "MUTE", "On")
    initialized_zone.mute = Mute.ATT_MINUS_20
    connection.put.assert_called_with(SUBUNIT, "MUTE", "Att -20 dB")
    initialized_zone.mute = Mute.ATT_MINUS_40
    connection.put.assert_called_with(SUBUNIT, "MUTE", "Att -40 dB")
    initialized_zone.mute = Mute.OFF
    connection.put.assert_called_with(SUBUNIT, "MUTE", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "MUTE", "On")
    assert initialized_zone.mute is Mute.ON
    connection.send_protocol_message(SUBUNIT, "MUTE", "Att -20 dB")
    assert initialized_zone.mute is Mute.ATT_MINUS_20
    connection.send_protocol_message(SUBUNIT, "MUTE", "Att -40 dB")
    assert initialized_zone.mute is Mute.ATT_MINUS_40
    connection.send_protocol_message(SUBUNIT, "MUTE", "Off")
    assert initialized_zone.mute is Mute.OFF


def test_zoneb_mute(connection: YncaConnectionMock, initialized_zone: Main) -> None:
    # Writing to device
    initialized_zone.zonebmute = ZoneBMute.ON
    connection.put.assert_called_with(SUBUNIT, "ZONEBMUTE", "On")
    initialized_zone.zonebmute = ZoneBMute.OFF
    connection.put.assert_called_with(SUBUNIT, "ZONEBMUTE", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "ZONEBMUTE", "On")
    assert initialized_zone.zonebmute is ZoneBMute.ON
    connection.send_protocol_message(SUBUNIT, "ZONEBMUTE", "Off")
    assert initialized_zone.zonebmute is ZoneBMute.OFF


def test_volume(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device

    # Positive with step rounding
    initialized_zone.vol = 0
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.0")
    initialized_zone.vol = 0.1
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.0")
    initialized_zone.vol = 0.4
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.5")

    # Negative with step rounding
    initialized_zone.vol = -5
    connection.put.assert_called_with(SUBUNIT, "VOL", "-5.0")
    initialized_zone.vol = -0.5
    connection.put.assert_called_with(SUBUNIT, "VOL", "-0.5")
    initialized_zone.vol = -0.4
    connection.put.assert_called_with(SUBUNIT, "VOL", "-0.5")
    initialized_zone.vol = -0.1
    connection.put.assert_called_with(SUBUNIT, "VOL", "0.0")

    # Up
    initialized_zone.vol_up()
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up")
    initialized_zone.vol_up(1)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up 1 dB")
    initialized_zone.vol_up(2)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up 2 dB")
    initialized_zone.vol_up(5)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up 5 dB")
    initialized_zone.vol_up(50)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Up")

    # Down
    initialized_zone.vol_down()
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down")
    initialized_zone.vol_down(1)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down 1 dB")
    initialized_zone.vol_down(2)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down 2 dB")
    initialized_zone.vol_down(5)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down 5 dB")
    initialized_zone.vol_down(50)
    connection.put.assert_called_with(SUBUNIT, "VOL", "Down")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "VOL", "0.0")
    assert initialized_zone.vol == 0
    connection.send_protocol_message(SUBUNIT, "VOL", "10.0")
    assert initialized_zone.vol == 10
    connection.send_protocol_message(SUBUNIT, "VOL", "-10.0")
    assert initialized_zone.vol == -10


def test_zoneb_volume(connection: YncaConnectionMock, initialized_zone: Main) -> None:
    # Writing to device

    # Positive with step rounding
    initialized_zone.zonebvol = 0
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "0.0")
    initialized_zone.zonebvol = 0.1
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "0.0")
    initialized_zone.zonebvol = 0.4
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "0.5")

    # Negative with step rounding
    initialized_zone.zonebvol = -5
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "-5.0")
    initialized_zone.zonebvol = -0.5
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "-0.5")
    initialized_zone.zonebvol = -0.4
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "-0.5")
    initialized_zone.zonebvol = -0.1
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "0.0")

    # Up
    initialized_zone.zonebvol_up()
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Up")
    initialized_zone.zonebvol_up(1)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Up 1 dB")
    initialized_zone.zonebvol_up(2)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Up 2 dB")
    initialized_zone.zonebvol_up(5)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Up 5 dB")
    initialized_zone.zonebvol_up(50)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Up")

    # Down
    initialized_zone.zonebvol_down()
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Down")
    initialized_zone.zonebvol_down(1)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Down 1 dB")
    initialized_zone.zonebvol_down(2)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Down 2 dB")
    initialized_zone.zonebvol_down(5)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Down 5 dB")
    initialized_zone.zonebvol_down(50)
    connection.put.assert_called_with(SUBUNIT, "ZONEBVOL", "Down")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "ZONEBVOL", "0.0")
    assert initialized_zone.zonebvol == 0
    connection.send_protocol_message(SUBUNIT, "ZONEBVOL", "10.0")
    assert initialized_zone.zonebvol == 10
    connection.send_protocol_message(SUBUNIT, "ZONEBVOL", "-10.0")
    assert initialized_zone.zonebvol == -10


def test_maxvol(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device

    # Positive with step rounding
    initialized_zone.maxvol = 0
    connection.put.assert_called_with(SUBUNIT, "MAXVOL", "0.0")
    initialized_zone.maxvol = 0.1
    connection.put.assert_called_with(SUBUNIT, "MAXVOL", "0.0")
    initialized_zone.maxvol = 4
    connection.put.assert_called_with(SUBUNIT, "MAXVOL", "5.0")

    # Negative with step rounding
    initialized_zone.maxvol = -5
    connection.put.assert_called_with(SUBUNIT, "MAXVOL", "-5.0")
    initialized_zone.maxvol = -5.5
    connection.put.assert_called_with(SUBUNIT, "MAXVOL", "-5.0")

    # 16.5 is special as it is valid, but does not fit normal step size
    initialized_zone.maxvol = 16.5
    connection.put.assert_called_with(SUBUNIT, "MAXVOL", "16.5")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "MAXVOL", "0.0")
    assert initialized_zone.maxvol == 0
    connection.send_protocol_message(SUBUNIT, "MAXVOL", "10.0")
    assert initialized_zone.maxvol == 10
    connection.send_protocol_message(SUBUNIT, "MAXVOL", "-10.0")
    assert initialized_zone.maxvol == -10


def test_input(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.inp = Input.RHAPSODY
    connection.put.assert_called_with(SUBUNIT, "INP", "Rhapsody")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "INP", "Napster")
    assert initialized_zone.inp == Input.NAPSTER

    connection.send_protocol_message(SUBUNIT, "INP", "Some unknown input")
    assert initialized_zone.inp == Input.UNKNOWN


def test_soundprg(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.soundprg = SoundPrg.THE_ROXY_THEATRE
    connection.put.assert_called_with(SUBUNIT, "SOUNDPRG", "The Roxy Theatre")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SOUNDPRG", "Sci-Fi")
    assert initialized_zone.soundprg == SoundPrg.SCI_FI

    connection.send_protocol_message(SUBUNIT, "SOUNDPRG", "Unmapped soundprg")
    assert initialized_zone.soundprg == SoundPrg.UNKNOWN


def test_straight(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.straight = Straight.ON
    connection.put.assert_called_with(SUBUNIT, "STRAIGHT", "On")
    initialized_zone.straight = Straight.OFF
    connection.put.assert_called_with(SUBUNIT, "STRAIGHT", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "STRAIGHT", "On")
    assert initialized_zone.straight == Straight.ON
    connection.send_protocol_message(SUBUNIT, "STRAIGHT", "Off")
    assert initialized_zone.straight == Straight.OFF


def test_surroundai(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.surroundai = SurroundAI.ON
    connection.put.assert_called_with(SUBUNIT, "SURROUNDAI", "On")
    initialized_zone.surroundai = SurroundAI.OFF
    connection.put.assert_called_with(SUBUNIT, "SURROUNDAI", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SURROUNDAI", "On")
    assert initialized_zone.surroundai == SurroundAI.ON
    connection.send_protocol_message(SUBUNIT, "SURROUNDAI", "Off")
    assert initialized_zone.surroundai == SurroundAI.OFF


def test_scene(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    initialized_zone.scene(42)
    connection.put.assert_called_with(SUBUNIT, "SCENE", "Scene 42")
    initialized_zone.scene("42")
    connection.put.assert_called_with(SUBUNIT, "SCENE", "Scene 42")


def test_scenename(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SCENE3NAME", "New Name")
    assert initialized_zone.scene3name == "New Name"


def test_zonename(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.zonename = "new name"
    connection.put.assert_called_with(SUBUNIT, "ZONENAME", "new name")
    with pytest.raises(ValueError, match="is too long"):
        initialized_zone.zonename = "new name is very long"

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "ZONENAME", "updated")
    assert initialized_zone.zonename == "updated"


def test_zonebname(connection: YncaConnectionMock, initialized_zone: Main) -> None:
    # Writing to device
    initialized_zone.zonebname = "new name"
    connection.put.assert_called_with(SUBUNIT, "ZONEBNAME", "new name")
    with pytest.raises(ValueError, match="is too long"):
        initialized_zone.zonebname = "new name is very long"

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "ZONEBNAME", "updated")
    assert initialized_zone.zonebname == "updated"


def test_twochdecoder(
    connection: YncaConnectionMock, initialized_zone: ZoneBase
) -> None:
    # Writing to device
    initialized_zone.twochdecoder = TwoChDecoder.DolbyPl
    connection.put.assert_called_with(SUBUNIT, "2CHDECODER", "Dolby PL")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "2CHDECODER", "DTS NEO:6 Cinema")
    assert initialized_zone.twochdecoder is TwoChDecoder.DtsNeo6Cinema

    # Unknown value
    connection.send_protocol_message(SUBUNIT, "2CHDECODER", "UnknownValue")
    assert initialized_zone.twochdecoder is TwoChDecoder.UNKNOWN


def test_puredirmode(
    connection: YncaConnectionMock, initialized_zone: ZoneBase
) -> None:
    # Writing to device
    initialized_zone.puredirmode = PureDirMode.ON
    connection.put.assert_called_with(SUBUNIT, "PUREDIRMODE", "On")
    initialized_zone.puredirmode = PureDirMode.OFF
    connection.put.assert_called_with(SUBUNIT, "PUREDIRMODE", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "PUREDIRMODE", "On")
    assert initialized_zone.puredirmode == PureDirMode.ON
    connection.send_protocol_message(SUBUNIT, "PUREDIRMODE", "Off")
    assert initialized_zone.puredirmode == PureDirMode.OFF


def test_dirmode(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.dirmode = DirMode.ON
    connection.put.assert_called_with(SUBUNIT, "DIRMODE", "On")
    initialized_zone.dirmode = DirMode.OFF
    connection.put.assert_called_with(SUBUNIT, "DIRMODE", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "DIRMODE", "On")
    assert initialized_zone.dirmode == DirMode.ON
    connection.send_protocol_message(SUBUNIT, "DIRMODE", "Off")
    assert initialized_zone.dirmode == DirMode.OFF


def test_initvolmode(
    connection: YncaConnectionMock, initialized_zone: ZoneBase
) -> None:
    # Writing to device
    initialized_zone.initvolmode = InitVolMode.ON
    connection.put.assert_called_with(SUBUNIT, "INITVOLMODE", "On")
    initialized_zone.initvolmode = InitVolMode.OFF
    connection.put.assert_called_with(SUBUNIT, "INITVOLMODE", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "INITVOLMODE", "On")
    assert initialized_zone.initvolmode == InitVolMode.ON
    connection.send_protocol_message(SUBUNIT, "INITVOLMODE", "Off")
    assert initialized_zone.initvolmode == InitVolMode.OFF


def test_initvollvl(connection: YncaConnectionMock, initialized_zone: ZoneBase) -> None:
    # Writing to device
    initialized_zone.initvollvl = InitVolLvl.MUTE
    connection.put.assert_called_with(SUBUNIT, "INITVOLLVL", "Mute")
    initialized_zone.initvollvl = -12.3
    connection.put.assert_called_with(SUBUNIT, "INITVOLLVL", "-12.5")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "INITVOLLVL", "Mute")
    assert initialized_zone.initvollvl == InitVolLvl.MUTE
    connection.send_protocol_message(SUBUNIT, "INITVOLLVL", "-10.5")
    assert initialized_zone.initvollvl == -10.5


def test_lipsynchdmioutoffset(
    connection: YncaConnectionMock, initialized_zone: ZoneBase
) -> None:
    # Writing to device

    # Values
    initialized_zone.lipsynchdmiout1offset = 0
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "0")
    initialized_zone.lipsynchdmiout2offset = 0
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "0")

    initialized_zone.lipsynchdmiout1offset = 250
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "250")
    initialized_zone.lipsynchdmiout2offset = 250
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "250")

    initialized_zone.lipsynchdmiout1offset = -250
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "-250")
    initialized_zone.lipsynchdmiout2offset = -250
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "-250")

    # Up
    initialized_zone.lipsynchdmiout1offset_up()
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "Up")
    initialized_zone.lipsynchdmiout2offset_up()
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "Up")

    # Down
    initialized_zone.lipsynchdmiout1offset_down()
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "Down")
    initialized_zone.lipsynchdmiout2offset_down()
    connection.put.assert_called_with(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "Down")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "0")
    assert initialized_zone.lipsynchdmiout1offset == 0
    connection.send_protocol_message(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "250")
    assert initialized_zone.lipsynchdmiout1offset == 250
    connection.send_protocol_message(SUBUNIT, "LIPSYNCHDMIOUT1OFFSET", "-250")
    assert initialized_zone.lipsynchdmiout1offset == -250

    connection.send_protocol_message(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "0")
    assert initialized_zone.lipsynchdmiout2offset == 0
    connection.send_protocol_message(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "250")
    assert initialized_zone.lipsynchdmiout2offset == 250
    connection.send_protocol_message(SUBUNIT, "LIPSYNCHDMIOUT2OFFSET", "-250")
    assert initialized_zone.lipsynchdmiout2offset == -250


def test_speaker_ab(connection: YncaConnectionMock, initialized_zone: Main) -> None:
    # Writing to device
    initialized_zone.speakera = SpeakerA.ON
    connection.put.assert_called_with(SUBUNIT, "SPEAKERA", "On")
    initialized_zone.speakera = SpeakerA.OFF
    connection.put.assert_called_with(SUBUNIT, "SPEAKERA", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SPEAKERA", "On")
    assert initialized_zone.speakera is SpeakerA.ON
    connection.send_protocol_message(SUBUNIT, "SPEAKERA", "Off")
    assert initialized_zone.speakera is SpeakerA.OFF

    # Writing to device
    initialized_zone.speakerb = SpeakerB.ON
    connection.put.assert_called_with(SUBUNIT, "SPEAKERB", "On")
    initialized_zone.speakerb = SpeakerB.OFF
    connection.put.assert_called_with(SUBUNIT, "SPEAKERB", "Off")

    # Updates from device
    connection.send_protocol_message(SUBUNIT, "SPEAKERB", "On")
    assert initialized_zone.speakerb is SpeakerB.ON
    connection.send_protocol_message(SUBUNIT, "SPEAKERB", "Off")
    assert initialized_zone.speakerb is SpeakerB.OFF
