from __future__ import annotations

from ..converters import FloatConverter
from ..function import Cmd, EnumFunctionMixin, FloatFunctionMixin, StrFunctionMixin
from ..enums import Playback, PlaybackInfo, Repeat, Shuffle
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase


class AlbumFunctionMixin:
    album = StrFunctionMixin(Cmd.GET, init="METAINFO")


class ArtistFunctionMixin:
    artist = StrFunctionMixin(Cmd.GET, init="METAINFO")


class ChNameFunctionMixin:
    chname = StrFunctionMixin(Cmd.GET, init="METAINFO")


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


# A number of subunits have the same/similar featureset
# so make a common base that only needs to be tested once
class MediaPlaybackSubunitBase(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    ArtistFunctionMixin,
    AlbumFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    pass


class FmFreqFunctionMixin:
    fmfreq = FloatFunctionMixin(
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 2, 0.2)
        ),
    )
    """Read/write FM frequency. Values will be aligned to a valid stepsize."""
