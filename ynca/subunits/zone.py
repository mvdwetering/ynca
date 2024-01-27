from __future__ import annotations

import logging
from typing import Type

from ..constants import Subunit
from ..converters import EnumConverter, FloatConverter, MultiConverter, StrConverter
from ..function import (
    Cmd,
    EnumFunctionMixin,
    EnumOrFloatFunctionMixin,
    FloatFunctionMixin,
    StrFunctionMixin,
)
from ..enums import (
    HdmiOut,
    InitVolLvl,
    InitVolMode,
    Input,
    Mute,
    AdaptiveDrc,
    Enhancer,
    PureDirMode,
    Pwr,
    Sleep,
    SoundPrg,
    Straight,
    ThreeDeeCinema,
    TwoChDecoder,
)
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase
from . import PlaybackFunctionMixin

logger = logging.getLogger(__name__)


def raiser(ex: Type[Exception]):
    raise ex


class ZoneBase(PlaybackFunctionMixin, SubunitBase):

    # BASIC gets a lot of attribute like PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER, SOUNDPRG and more
    # Use it to significantly reduce the amount of commands to send

    adaptivedrc = EnumFunctionMixin[AdaptiveDrc](AdaptiveDrc)
    enhancer = EnumFunctionMixin[Enhancer](Enhancer)
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
    maxvol = FloatFunctionMixin(
        converter=MultiConverter(
            [
                # Special handling for 16.5 which is valid, but does not fit stepsize of 5
                FloatConverter(
                    to_str=lambda v: "16.5" if v == 16.5 else raiser(ValueError)
                ),
                FloatConverter(
                    to_str=lambda v: number_to_string_with_stepsize(v, 1, 5)
                ),
            ]
        ),
    )
    mute = EnumFunctionMixin[Mute](Mute, init="BASIC")
    puredirmode = EnumFunctionMixin[PureDirMode](PureDirMode, init="BASIC")
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
    threedcinema = EnumFunctionMixin[ThreeDeeCinema](
        ThreeDeeCinema, name_override="3DCINEMA"
    )
    twochdecoder = EnumFunctionMixin[TwoChDecoder](TwoChDecoder, name_override="2CHDECODER")
    vol = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
        init="BASIC",
    )
    zonename = StrFunctionMixin(converter=StrConverter(min_len=0, max_len=9))

    def scene(self, scene_id: int | str):
        """Recall a scene"""
        self._put("SCENE", f"Scene {scene_id}")

    def vol_up(self, step_size: float = 0.5):
        """
        Increase the volume with given stepsize.
        Supported stepsizes are: 0.5, 1, 2 and 5
        """
        value = "Up"
        if step_size in [1, 2, 5]:
            value = "Up {} dB".format(step_size)
        self._put("VOL", value)

    def vol_down(self, step_size: float = 0.5):
        """
        Decrease the volume with given stepsize.
        Supported stepsizes are: 0.5, 1, 2 and 5
        """
        value = "Down"
        if step_size in [1, 2, 5]:
            value = "Down {} dB".format(step_size)
        self._put("VOL", value)


class Main(ZoneBase):
    id = Subunit.MAIN


class Zone2(ZoneBase):
    id = Subunit.ZONE2


class Zone3(ZoneBase):
    id = Subunit.ZONE3


class Zone4(ZoneBase):
    id = Subunit.ZONE4
