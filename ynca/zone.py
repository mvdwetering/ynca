from __future__ import annotations
import re
import logging

from typing import Dict

from .connection import YncaConnection, YncaProtocolStatus
from .constants import Mute, Subunit
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
        self._max_volume = 16.5  # is 16.5 for zones where it is not configurable
        self._volume = None
        self._scenenames: Dict[str, str] = {}

        self._attr_inp = None
        self._attr_mute = None
        self._attr_soundprg = None
        self._attr_straight = None
        self._attr_zonename = None

    def on_initialize(self):
        self._reset_internal_state()

        # BASIC gets PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER and SOUNDPRG (if applicable)
        self._get("BASIC")
        self._get("MAXVOL")
        self._get("SCENENAME")
        self._get("ZONENAME")

    def _subunit_message_received_without_handler(
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
        self._volume = float(value)

    def _handle_maxvol(self, value: str):
        self._max_volume = float(value)

    @property
    def name(self) -> str | None:
        """Get zone name"""
        logger.warning(
            "The 'name' attribute is deprecated and replaced with 'zonename' to better match the naming in the YNCA spec"
        )
        return self.zonename

    @property
    def zonename(self) -> str | None:
        """Get zone name"""
        return self._attr_zonename

    @zonename.setter
    def zonename(self, zonename: str):
        """Set zone name (0-9 characters)"""
        if len(zonename) > 9:
            raise ValueError("The provided name is too long, should be <= 9 characters")
        self._put("ZONENAME", zonename)

    @property
    def mute(self) -> Mute | None:
        """Get current mute state"""
        return Mute(self._attr_mute) if self._attr_mute is not None else None

    @mute.setter
    def mute(self, value: Mute):
        """Mute"""
        self._put("MUTE", value)

    @property
    def max_volume(self) -> float | None:
        """Get maximum volume in dB"""
        return self._max_volume

    @property
    def min_volume(self) -> float:
        """Get minimum volume in dB"""
        return -80.5  # Seems to be fixed and the same for all zones

    @property
    def volume(self) -> float:
        """Get current volume in dB"""
        return self._volume

    @volume.setter
    def volume(self, value: float):
        """Set volume in dB. The receiver only works with 0.5 increments. Input values will be rounded to nearest 0.5 step."""
        if self.min_volume <= value <= self._max_volume:
            self._put("VOL", number_to_string_with_stepsize(value, 1, 0.5))
        else:
            raise ValueError(
                "Volume out of range, must be between min_volume and max_volume"
            )

    def volume_up(self, step_size: float = 0.5):
        """
        Increase the volume with given stepsize.
        Supported stepsizes are: 0.5, 1, 2 and 5
        """
        value = "Up"
        if step_size in [1, 2, 5]:
            value = "Up {} dB".format(step_size)
        self._put("VOL", value)

    def volume_down(self, step_size: float = 0.5):
        """
        Decrease the volume with given stepsize.
        Supported stepsizes are: 0.5, 1, 2 and 5
        """
        value = "Down"
        if step_size in [1, 2, 5]:
            value = "Down {} dB".format(step_size)
        self._put("VOL", value)

    @property
    def input(self) -> str:
        """Get current input"""
        logger.warning("zone.input is deprecated, use zone.inp instead")
        return self._attr_inp

    @input.setter
    def input(self, value: str):
        """Set input"""
        logger.warning("zone.input is deprecated, use zone.inp instead")
        self._put("INP", value)

    @property
    def inp(self) -> str:
        """Get current inp"""
        return self._attr_inp

    @inp.setter
    def inp(self, value: str):
        """Set inp"""
        self._put("INP", value)

    @property
    def soundprg(self) -> str | None:
        """Get the current DSP sound program"""
        return self._attr_soundprg

    @soundprg.setter
    def soundprg(self, value: str):
        """Set the DSP sound program"""
        self._put("SOUNDPRG", value)

    @property
    def straight(self) -> bool | None:
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

    @property
    def scenes(self) -> Dict[str, str]:
        """Get the dictionary with scenes where key, value = id, name"""
        logger.warning(
            "The 'scenes' attribute is deprecated and replaced with 'scene_names' to better match the naming in the YNCA spec"
        )
        return self.scenenames

    def activate_scene(self, scene_id: str):
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
