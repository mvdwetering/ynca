from __future__ import annotations
from enum import Enum
import re
import logging

from typing import Dict

from .connection import YncaConnection, YncaProtocolStatus
from .constants import Mute, SoundPrg, Subunit, TwoChDecoder
from .function_mixins import PlaybackFunctionMixin, Pwr
from .helpers import number_to_string_with_stepsize
from .subunit import (
    CommandType,
    FloatConverter,
    StrConverter,
    SubunitBase,
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
    pwr = YncaFunctionEnum[Pwr]("PWR", Pwr, initialize_function_name="BASIC")
    puredirmode = YncaFunctionEnum[PureDirMode](
        "PUREDIRMODE", PureDirMode, initialize_function_name="BASIC"
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

    def __init__(
        self,
        connection: YncaConnection,
    ):
        super().__init__(connection)
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._scenenames: Dict[str, str] = {}

    def on_initialize(self):
        self._reset_internal_state()
        self._get("SCENENAME")

    def on_message_received_without_handler(
        self, status: YncaProtocolStatus, function_: str, value: str
    ) -> bool:
        updated = True

        if matches := re.match(r"SCENE(\d+)NAME", function_):
            scene_id = matches[1]
            self._scenenames[scene_id] = value
        else:
            updated = False

        return updated

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

    @property
    def scenenames(self) -> Dict[str, str]:
        """Get a dictionary with scene names where key, value = id, name"""
        return dict(self._scenenames)

    def scene_activate(self, scene_id: str):
        """Activate a scene"""
        if scene_id not in self._scenenames.keys():
            raise ValueError("Invalid scene ID")
        else:
            self._put("SCENE", f"Scene {scene_id}")


class Main(ZoneBase):
    id = Subunit.MAIN


class Zone2(ZoneBase):
    id = Subunit.ZONE2


class Zone3(ZoneBase):
    id = Subunit.ZONE3


class Zone4(ZoneBase):
    id = Subunit.ZONE4
