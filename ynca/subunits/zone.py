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
    CommandType,
    YncaFunctionEnum,
    YncaFunctionFloat,
    YncaFunctionStr,
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

    inp = YncaFunctionStr("INP", initialize_function_name="BASIC")
    maxvol = YncaFunctionFloat("MAXVOL", command_type=CommandType.GET)
    mute = YncaFunctionEnum[Mute]("MUTE", Mute, initialize_function_name="BASIC")
    puredirmode = YncaFunctionEnum[PureDirMode](
        "PUREDIRMODE", PureDirMode, initialize_function_name="BASIC"
    )
    pwr = YncaFunctionEnum[Pwr]("PWR", Pwr, initialize_function_name="BASIC")
    scene1name = YncaFunctionStr(
        "SCENE1NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene2name = YncaFunctionStr(
        "SCENE2NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene3name = YncaFunctionStr(
        "SCENE3NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene4name = YncaFunctionStr(
        "SCENE4NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene5name = YncaFunctionStr(
        "SCENE5NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene6name = YncaFunctionStr(
        "SCENE6NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene7name = YncaFunctionStr(
        "SCENE7NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene8name = YncaFunctionStr(
        "SCENE8NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene9name = YncaFunctionStr(
        "SCENE9NAME", command_type=CommandType.GET, initialize_function_name="SCENENAME"
    )
    scene10name = YncaFunctionStr(
        "SCENE10NAME",
        command_type=CommandType.GET,
        initialize_function_name="SCENENAME",
    )
    scene11name = YncaFunctionStr(
        "SCENE11NAME",
        command_type=CommandType.GET,
        initialize_function_name="SCENENAME",
    )
    scene12name = YncaFunctionStr(
        "SCENE12NAME",
        command_type=CommandType.GET,
        initialize_function_name="SCENENAME",
    )
    soundprg = YncaFunctionEnum[SoundPrg](
        "SOUNDPRG", SoundPrg, initialize_function_name="BASIC"
    )
    straight = YncaFunctionEnum[Straight](
        "STRAIGHT", Straight, initialize_function_name="BASIC"
    )
    twochdecoder = YncaFunctionEnum[TwoChDecoder]("2CHDECODER", TwoChDecoder)
    vol = YncaFunctionFloat(
        "VOL",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 1, 0.5)
        ),
        initialize_function_name="BASIC",
    )
    zonename = YncaFunctionStr("ZONENAME", converter=StrConverter(min_len=0, max_len=9))

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
