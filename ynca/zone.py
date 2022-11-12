from __future__ import annotations
import re
import logging

from typing import Dict, Optional

from .connection import YncaConnection, YncaProtocolStatus
from .constants import Mute, Subunit, MIN_VOLUME, TwoChDecoder
from .function_mixins import PlaybackFunctionMixin, PowerFunctionMixin
from .helpers import number_to_string_with_stepsize
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class ZoneBase(PowerFunctionMixin, PlaybackFunctionMixin, SubunitBase):
    def __init__(
        self,
        connection: YncaConnection,
    ):
        super().__init__(connection)
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._maxvol = 16.5  # is 16.5 for zones where it is not configurable
        self._vol = None
        self._scenenames: Dict[str, str] = {}

        self._attr_inp = None
        self._attr_mute = None
        self._attr_soundprg = None
        self._attr_straight = None
        self._attr_zonename = None
        self._attr_twochdecoder = None
        self._attr_puredirmode = None

    def on_initialize(self):
        self._reset_internal_state()

        # BASIC gets PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER and SOUNDPRG (if applicable)
        self._get("BASIC")
        self._get("MAXVOL")
        self._get("SCENENAME")
        self._get("ZONENAME")
        self._get("2CHDECODER")
        self._get("PUREDIRMODE")

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

    def _handle_vol(self, value: str):
        self._vol = float(value)

    def _handle_maxvol(self, value: str):
        self._maxvol = float(value)

    @property
    def zonename(self) -> Optional[str]:
        """Get zone name"""
        return self._attr_zonename

    @zonename.setter
    def zonename(self, zonename: str):
        """Set zone name (0-9 characters)"""
        if len(zonename) > 9:
            raise ValueError("The provided name is too long, should be <= 9 characters")
        self._put("ZONENAME", zonename)

    @property
    def mute(self) -> Optional[Mute]:
        """Get current mute state"""
        return Mute(self._attr_mute) if self._attr_mute is not None else None

    @mute.setter
    def mute(self, value: Mute):
        """Mute"""
        self._put("MUTE", value)

    @property
    def maxvol(self) -> Optional[float]:
        """
        Get maximum volume supported in dB

        Note that the API provides no way to retrieve MinVol
        this seems to be -80.5 for all zones
        """
        return self._maxvol

    @property
    def vol(self) -> float:
        """Get current volume in dB"""
        return self._vol

    @vol.setter
    def vol(self, value: float):
        """Set volume in dB. The receiver only works with 0.5 increments. Input values will be rounded to nearest 0.5 step."""
        if MIN_VOLUME <= value <= self._maxvol:
            self._put("VOL", number_to_string_with_stepsize(value, 1, 0.5))
        else:
            raise ValueError(
                f"Volume out of range, must be between {MIN_VOLUME} and maxvol ({self._maxvol})"
            )

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
    def inp(self) -> str:
        """Get current inp"""
        return self._attr_inp

    @inp.setter
    def inp(self, value: str):
        """Set inp"""
        self._put("INP", value)

    @property
    def soundprg(self) -> Optional[str]:
        """Get the current DSP sound program"""
        return self._attr_soundprg

    @soundprg.setter
    def soundprg(self, value: str):
        """Set the DSP sound program"""
        self._put("SOUNDPRG", value)

    @property
    def straight(self) -> Optional[bool]:
        """Get the current Straight value"""
        return self._attr_straight == "On" if self._attr_straight is not None else None

    @straight.setter
    def straight(self, value: bool):
        """Set the Straight value"""
        self._put("STRAIGHT", "On" if value is True else "Off")

    @property
    def scenenames(self) -> Dict[str, str]:
        """Get a dictionary with scene names where key, value = id, name"""
        return dict(self._scenenames)

    def activate_scene(self, scene_id: str):
        """Activate a scene"""
        if scene_id not in self._scenenames.keys():
            raise ValueError("Invalid scene ID")
        else:
            self._put("SCENE", f"Scene {scene_id}")

    @property
    def twochdecoder(self) -> Optional[TwoChDecoder]:
        """Get 2ch decoder state"""
        return (
            TwoChDecoder(self._attr_twochdecoder)
            if self._attr_twochdecoder is not None
            else None
        )

    @twochdecoder.setter
    def twochdecoder(self, value: TwoChDecoder):
        """Set 2ch decoder value"""
        self._put("2CHDECODER", value.value)

    def _handle_2chdecoder(self, value: str):
        self._attr_twochdecoder = value

    @property
    def puredirmode(self) -> Optional[bool]:
        """Get the current Straight value"""
        return (
            self._attr_puredirmode == "On"
            if self._attr_puredirmode is not None
            else None
        )

    @puredirmode.setter
    def puredirmode(self, value: bool):
        """Set the Pure Direct Mode value"""
        self._put("PUREDIRMODE", "On" if value is True else "Off")


class Main(ZoneBase):
    id = Subunit.MAIN


class Zone2(ZoneBase):
    id = Subunit.ZONE2


class Zone3(ZoneBase):
    id = Subunit.ZONE3


class Zone4(ZoneBase):
    id = Subunit.ZONE4
