from __future__ import annotations

from typing import TYPE_CHECKING

from ..converters import FloatConverter, IntOrNoneConverter, TimedeltaOrNoneConverter
from ..enums import Playback, PlaybackInfo, Repeat, Shuffle
from ..function import (
    Cmd,
    EnumFunctionMixin,
    FloatFunctionMixin,
    IntFunctionMixin,
    StrFunctionMixin,
    TimedeltaFunctionMixin,
)
from ..helpers import number_to_string_with_stepsize

if TYPE_CHECKING:  # pragma: no cover
    from ..subunit import SubunitBaseMixinProtocol


class AlbumFunctionMixin:
    album = StrFunctionMixin(Cmd.GET, init="METAINFO")


class ArtistFunctionMixin:
    artist = StrFunctionMixin(Cmd.GET, init="METAINFO")


class ChNameFunctionMixin:
    chname = StrFunctionMixin(Cmd.GET, init="METAINFO")


class ElapsedTimeFunctionMixin:
    elapsedtime = TimedeltaFunctionMixin(Cmd.GET, converter=TimedeltaOrNoneConverter())
    """Elapsed time of current track/station. Note that this data is updated from the receiver every second while playing."""


class FmFreqFunctionMixin:
    fmfreq = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 2, 0.2)
        ),
    )
    """Read/write FM frequency. Values will be aligned to a valid stepsize."""


class MemFunctionMixin:

    def mem(self: SubunitBaseMixinProtocol, parameter: int | None = None) -> None:
        """Store preset in memory slot, parameter is a slot number 1-40 or None to select a slot automatically."""
        self._put("MEM", "Auto" if parameter is None else str(parameter))


class PlaybackFunctionMixin:

    def playback(self: SubunitBaseMixinProtocol, parameter: Playback) -> None:
        """Change playback state."""
        self._put("PLAYBACK", parameter.value)


class PlaybackInfoFunctionMixin:
    playbackinfo = EnumFunctionMixin[PlaybackInfo](PlaybackInfo, Cmd.GET)


class PresetFunctionMixin:
    preset = IntFunctionMixin(converter=IntOrNoneConverter())
    """Activate or read preset. Note that only TUN and SIRIUS seem to support GET."""


class PresetUpDownFunctionMixin:

    def preset_up(self: SubunitBaseMixinProtocol) -> None:
        """Select next available preset."""
        self._put("PRESET", "Up")

    def preset_down(self: SubunitBaseMixinProtocol) -> None:
        """Select previous available preset."""
        self._put("PRESET", "Down")


class RepeatFunctionMixin:
    repeat = EnumFunctionMixin[Repeat](Repeat)


class ShuffleFunctionMixin:
    shuffle = EnumFunctionMixin[Shuffle](Shuffle)


class SongFunctionMixin:
    song = StrFunctionMixin(Cmd.GET, init="METAINFO")


class StationFunctionMixin:
    station = StrFunctionMixin(Cmd.GET)


class TotalTimeFunctionMixin:
    totaltime = TimedeltaFunctionMixin(Cmd.GET, converter=TimedeltaOrNoneConverter())


class TrackFunctionMixin:
    track = StrFunctionMixin(Cmd.GET, init="METAINFO")
