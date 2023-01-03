from __future__ import annotations

import logging
from typing import Type

from ..constants import Subunit
from ..converters import EnumConverter, FloatConverter, MultiConverter, StrConverter
from ..function import (
    Cmd,
    EnumFunction,
    EnumOrFloatFunction,
    FloatFunction,
    StrFunction,
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
from . import PlaybackFunction

logger = logging.getLogger(__name__)


def raiser(ex: Type[Exception]):
    raise ex


class ZoneBase(PlaybackFunction, SubunitBase):

    # BASIC gets a lot of attribute like PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER, SOUNDPRG and more
    # Use it to significantly reduce the amount of commands to send

    adaptivedrc = EnumFunction[AdaptiveDrc]("ADAPTIVEDRC", AdaptiveDrc)
    enhancer = EnumFunction[Enhancer]("ENHANCER", Enhancer)
    hdmiout = EnumFunction[HdmiOut]("HDMIOUT", HdmiOut)
    hpbass = FloatFunction(
        "HPBASS",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    hptreble = FloatFunction(
        "HPTREBLE",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    initvollvl = EnumOrFloatFunction[InitVolLvl](
        "INITVOLLVL",
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
    initvolmode = EnumFunction[InitVolMode]("INITVOLMODE", InitVolMode)
    inp = EnumFunction[Input]("INP", Input, init="BASIC")
    maxvol = FloatFunction(
        "MAXVOL",
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
    mute = EnumFunction[Mute]("MUTE", Mute, init="BASIC")
    puredirmode = EnumFunction[PureDirMode]("PUREDIRMODE", PureDirMode, init="BASIC")
    pwr = EnumFunction[Pwr]("PWR", Pwr, init="BASIC")
    scene1name = StrFunction("SCENE1NAME", Cmd.GET, init="SCENENAME")
    scene2name = StrFunction("SCENE2NAME", Cmd.GET, init="SCENENAME")
    scene3name = StrFunction("SCENE3NAME", Cmd.GET, init="SCENENAME")
    scene4name = StrFunction("SCENE4NAME", Cmd.GET, init="SCENENAME")
    scene5name = StrFunction("SCENE5NAME", Cmd.GET, init="SCENENAME")
    scene6name = StrFunction("SCENE6NAME", Cmd.GET, init="SCENENAME")
    scene7name = StrFunction("SCENE7NAME", Cmd.GET, init="SCENENAME")
    scene8name = StrFunction("SCENE8NAME", Cmd.GET, init="SCENENAME")
    scene9name = StrFunction("SCENE9NAME", Cmd.GET, init="SCENENAME")
    scene10name = StrFunction("SCENE10NAME", Cmd.GET, init="SCENENAME")
    scene11name = StrFunction("SCENE11NAME", Cmd.GET, init="SCENENAME")
    scene12name = StrFunction("SCENE12NAME", Cmd.GET, init="SCENENAME")
    sleep = EnumFunction[Sleep]("SLEEP", Sleep)
    soundprg = EnumFunction[SoundPrg]("SOUNDPRG", SoundPrg, init="BASIC")
    spbass = FloatFunction(
        "SPBASS",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    sptreble = FloatFunction(
        "SPTREBLE",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
    )
    straight = EnumFunction[Straight]("STRAIGHT", Straight, init="BASIC")
    threedcinema = EnumFunction[ThreeDeeCinema]("3DCINEMA", ThreeDeeCinema)
    twochdecoder = EnumFunction[TwoChDecoder]("2CHDECODER", TwoChDecoder)
    vol = FloatFunction(
        "VOL",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
        init="BASIC",
    )
    zonename = StrFunction("ZONENAME", converter=StrConverter(min_len=0, max_len=9))

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
