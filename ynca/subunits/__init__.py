from __future__ import annotations

from ..converters import FloatConverter
from ..function import Cmd, EnumFunctionMixin, FloatFunctionMixin, StrFunctionMixin
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


class PlaybackFunctionMixin:
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunctionMixin:
    playbackinfo = EnumFunctionMixin[PlaybackInfo](PlaybackInfo, Cmd.GET)


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
