from __future__ import annotations

import logging
import re
from enum import Enum
from typing import Dict

from ..connection import YncaConnection, YncaProtocolStatus
from ..constants import Mute, SoundPrg, Subunit, TwoChDecoder
from ..converters import FloatConverter, StrConverter
from .function_mixins import PlaybackFunctionMixin, Pwr
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase
from ..ynca_function import (
    Cmd,
    EnumFunction,
    FloatFunction,
    StrFunction,
)

logger = logging.getLogger(__name__)


class Straight(Enum):
    ON = "On"
    OFF = "Off"


class PureDirMode(Enum):
    ON = "On"
    OFF = "Off"


class ZoneBase(PlaybackFunctionMixin, SubunitBase):

    # BASIC gets a lot of attribute like PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER, SOUNDPRG and more
    # Use it to significantly reduce the amount of commands to send

    inp = StrFunction("INP", init="BASIC")
    maxvol = FloatFunction("MAXVOL", command_type=Cmd.GET)
    mute = EnumFunction[Mute]("MUTE", Mute, init="BASIC")
    puredirmode = EnumFunction[PureDirMode]("PUREDIRMODE", PureDirMode, init="BASIC")
    pwr = EnumFunction[Pwr]("PWR", Pwr, init="BASIC")
    scene1name = StrFunction("SCENE1NAME", cmd=Cmd.GET, init="SCENENAME")
    scene2name = StrFunction("SCENE2NAME", cmd=Cmd.GET, init="SCENENAME")
    scene3name = StrFunction("SCENE3NAME", cmd=Cmd.GET, init="SCENENAME")
    scene4name = StrFunction("SCENE4NAME", cmd=Cmd.GET, init="SCENENAME")
    scene5name = StrFunction("SCENE5NAME", cmd=Cmd.GET, init="SCENENAME")
    scene6name = StrFunction("SCENE6NAME", cmd=Cmd.GET, init="SCENENAME")
    scene7name = StrFunction("SCENE7NAME", cmd=Cmd.GET, init="SCENENAME")
    scene8name = StrFunction("SCENE8NAME", cmd=Cmd.GET, init="SCENENAME")
    scene9name = StrFunction("SCENE9NAME", cmd=Cmd.GET, init="SCENENAME")
    scene10name = StrFunction("SCENE10NAME", cmd=Cmd.GET, init="SCENENAME")
    scene11name = StrFunction("SCENE11NAME", cmd=Cmd.GET, init="SCENENAME")
    scene12name = StrFunction("SCENE12NAME", cmd=Cmd.GET, init="SCENENAME")
    soundprg = EnumFunction[SoundPrg]("SOUNDPRG", SoundPrg, init="BASIC")
    straight = EnumFunction[Straight]("STRAIGHT", Straight, init="BASIC")
    twochdecoder = EnumFunction[TwoChDecoder]("2CHDECODER", TwoChDecoder)
    vol = FloatFunction(
        "VOL",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
        initializer="BASIC",
    )
    zonename = StrFunction("ZONENAME", converter=StrConverter(min_len=0, max_len=9))

    def scene_recall(self, scene_id: int):
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
