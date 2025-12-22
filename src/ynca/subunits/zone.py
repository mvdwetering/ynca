from __future__ import annotations

import logging
from typing import NoReturn

from ..constants import MAX_VOLUME, Subunit
from ..converters import EnumConverter, FloatConverter, MultiConverter, StrConverter
from ..enums import (
    AdaptiveDrc,
    DirMode,
    Enhancer,
    ExBass,
    HdmiOut,
    InitVolLvl,
    InitVolMode,
    Input,
    Mute,
    PureDirMode,
    Pwr,
    PwrB,
    Sleep,
    SoundPrg,
    SpeakerA,
    SpeakerB,
    Straight,
    SurroundAI,
    ThreeDeeCinema,
    TwoChDecoder,
    ZoneBAvail,
    ZoneBMute,
)
from ..function import (
    Cmd,
    EnumFunctionMixin,
    EnumOrFloatFunctionMixin,
    FloatFunctionMixin,
    IntFunctionMixin,
    StrFunctionMixin,
)
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase, SubunitBaseMixinProtocol
from . import PlaybackFunctionMixin

logger = logging.getLogger(__name__)


def raiser(ex: type[Exception]) -> NoReturn:
    raise ex


def do_vol_up(self: SubunitBaseMixinProtocol, step_size: float, function: str) -> None:
    """Increase the volume with given stepsize. Supported stepsizes are: 0.5, 1, 2 and 5."""
    value = "Up"
    if int(step_size) in [1, 2, 5]:
        value = f"Up {step_size} dB"
    self._put(function, value)


def do_vol_down(
    self: SubunitBaseMixinProtocol, step_size: float, function: str
) -> None:
    """Decrease the volume with given stepsize. Supported stepsizes are: 0.5, 1, 2 and 5."""
    value = "Down"
    if int(step_size) in [1, 2, 5]:
        value = f"Down {step_size} dB"
    self._put(function, value)


class ZoneBase(PlaybackFunctionMixin, SubunitBase):
    # BASIC gets a lot of attribute like PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER, SOUNDPRG and more
    # Use it to significantly reduce the amount of commands to send

    adaptivedrc = EnumFunctionMixin[AdaptiveDrc](AdaptiveDrc)
    dirmode = EnumFunctionMixin[DirMode](DirMode, init="BASIC")
    enhancer = EnumFunctionMixin[Enhancer](Enhancer)
    exbass = EnumFunctionMixin[ExBass](ExBass)
    hdmiout = EnumFunctionMixin[HdmiOut](HdmiOut)
    hpbass = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    hptreble = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    initvollvl = EnumOrFloatFunctionMixin[InitVolLvl](
        InitVolLvl,
        MultiConverter(
            [
                FloatConverter(
                    to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
                ),
                EnumConverter[InitVolLvl](InitVolLvl),
            ]
        ),
    )
    initvolmode = EnumFunctionMixin[InitVolMode](InitVolMode)
    inp = EnumFunctionMixin[Input](Input, init="BASIC")

    lipsynchdmiout1offset = IntFunctionMixin()

    def lipsynchdmiout1offset_down(self) -> None:
        """Increase by 1 step (=1 ms)."""
        self._put("LIPSYNCHDMIOUT1OFFSET", "Down")

    def lipsynchdmiout1offset_up(self) -> None:
        """Decrease by 1 step (=1 ms)."""
        self._put("LIPSYNCHDMIOUT1OFFSET", "Up")

    lipsynchdmiout2offset = IntFunctionMixin()

    def lipsynchdmiout2offset_down(self) -> None:
        """Increase by 1 step (=1 ms)."""
        self._put("LIPSYNCHDMIOUT2OFFSET", "Down")

    def lipsynchdmiout2offset_up(self) -> None:
        """Decrease by 1 step (=1 ms)."""
        self._put("LIPSYNCHDMIOUT2OFFSET", "Up")

    maxvol = FloatFunctionMixin(
        converter=MultiConverter(
            [
                # Special handling for 16.5 which is valid, but does not fit stepsize of 5
                FloatConverter(
                    to_str=lambda v: "16.5" if v == MAX_VOLUME else raiser(ValueError)
                ),
                FloatConverter(
                    to_str=lambda v: number_to_string_with_stepsize(v, 1, 5)
                ),
            ]
        ),
    )
    mute = EnumFunctionMixin[Mute](Mute, init="BASIC")
    puredirmode = EnumFunctionMixin[PureDirMode](
        PureDirMode
    )  # , init="BASIC")  # Not in BASIC on RX-V1067
    pwr = EnumFunctionMixin[Pwr](Pwr, init="BASIC")
    scene1name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene2name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene3name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene4name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene5name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene6name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene7name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene8name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene9name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene10name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene11name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    scene12name = StrFunctionMixin(Cmd.GET, init="SCENENAME")
    sleep = EnumFunctionMixin[Sleep](Sleep)
    soundprg = EnumFunctionMixin[SoundPrg](SoundPrg, init="BASIC")
    spbass = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    sptreble = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    straight = EnumFunctionMixin[Straight](Straight, init="BASIC")
    surroundai = EnumFunctionMixin[SurroundAI](SurroundAI)
    threedcinema = EnumFunctionMixin[ThreeDeeCinema](
        ThreeDeeCinema, name_override="3DCINEMA"
    )
    twochdecoder = EnumFunctionMixin[TwoChDecoder](
        TwoChDecoder, name_override="2CHDECODER"
    )
    vol = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
        init="BASIC",
    )
    zonename = StrFunctionMixin(converter=StrConverter(max_len=9))

    def scene(self, scene_id: int | str) -> None:
        """Recall a scene."""
        self._put("SCENE", f"Scene {scene_id}")

    def vol_up(self, step_size: float = 0.5) -> None:
        do_vol_up(self, step_size=step_size, function="VOL")

    def vol_down(self, step_size: float = 0.5) -> None:
        do_vol_down(self, step_size, function="VOL")


class Main(ZoneBase):
    id = Subunit.MAIN

    # ZoneA/B only exists as "subzones" on the main subunit

    # Speaker A/B are in BASIC on RX-V583, but are not on RX-V573 it seems
    speakera = EnumFunctionMixin[SpeakerA](SpeakerA)  # , init="BASIC")
    speakerb = EnumFunctionMixin[SpeakerB](SpeakerB)  # , init="BASIC")

    pwrb = EnumFunctionMixin[PwrB](PwrB, init="BASIC")

    zonebavail = EnumFunctionMixin[ZoneBAvail](ZoneBAvail, init="BASIC")
    zonebmute = EnumFunctionMixin[ZoneBMute](ZoneBMute, init="BASIC")
    zonebname = StrFunctionMixin(converter=StrConverter(max_len=9))
    zonebvol = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
        init="BASIC",
    )

    def zonebvol_up(self, step_size: float = 0.5) -> None:
        do_vol_up(self, step_size, function="ZONEBVOL")

    def zonebvol_down(self, step_size: float = 0.5) -> None:
        do_vol_down(self, step_size, function="ZONEBVOL")


class Zone2(ZoneBase):
    id = Subunit.ZONE2


class Zone3(ZoneBase):
    id = Subunit.ZONE3


class Zone4(ZoneBase):
    id = Subunit.ZONE4
