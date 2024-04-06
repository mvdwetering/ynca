from __future__ import annotations

from ..converters import FloatConverter, IntOrNoneConverter
from ..function import (
    Cmd,
    EnumFunctionMixin,
    FloatFunctionMixin,
    IntFunctionMixin,
    StrFunctionMixin,
)
from ..enums import Playback, PlaybackInfo, Repeat, Shuffle
from ..helpers import number_to_string_with_stepsize


class AlbumFunctionMixin:
    album = StrFunctionMixin(Cmd.GET, init="METAINFO")


class ArtistFunctionMixin:
    artist = StrFunctionMixin(Cmd.GET, init="METAINFO")


class ChNameFunctionMixin:
    chname = StrFunctionMixin(Cmd.GET, init="METAINFO")


class FmFreqFunctionMixin:
    fmfreq = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 2, 0.2)
        ),
    )
    """Read/write FM frequency. Values will be aligned to a valid stepsize."""


class MemFunctionMixin:
    def mem(self, parameter: int | None = None):
        """Store preset in memory slot, parameter is a slot number 1-40 or None to select a slot automatically."""
        self._put("MEM", "Auto" if parameter is None else str(parameter))  # type: ignore


class PlaybackFunctionMixin:
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter.value)  # type: ignore


class PlaybackInfoFunctionMixin:
    playbackinfo = EnumFunctionMixin[PlaybackInfo](PlaybackInfo, Cmd.GET)


class PresetFunctionMixin:
    preset = IntFunctionMixin(converter=IntOrNoneConverter())
    """Activate or read preset. Note that only TUN and SIRIUS seem to support GET."""


class PresetUpDownFunctionMixin:
    def preset_up(self):
        """Select next available preset"""
        self._put("PRESET", "Up")  # type: ignore

    def preset_down(self):
        """Select previous available preset"""
        self._put("PRESET", "Down")  # type: ignore


class RepeatFunctionMixin:
    repeat = EnumFunctionMixin[Repeat](Repeat)


class ShuffleFunctionMixin:
    shuffle = EnumFunctionMixin[Shuffle](Shuffle)


class SongFunctionMixin:
    song = StrFunctionMixin(Cmd.GET, init="METAINFO")


class StationFunctionMixin:
    station = StrFunctionMixin(Cmd.GET)


class TrackFunctionMixin:
    track = StrFunctionMixin(Cmd.GET, init="METAINFO")
