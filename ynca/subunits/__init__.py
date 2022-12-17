from __future__ import annotations

from ..converters import FloatConverter
from ..function import Cmd, EnumFunction, FloatFunction, StrFunction
from ..enums import Playback, PlaybackInfo, Repeat, Shuffle
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase


class AlbumFunction:
    album = StrFunction("ALBUM", Cmd.GET, init="METAINFO")


class ArtistFunction:
    artist = StrFunction("ARTIST", Cmd.GET, init="METAINFO")


class ChNameFunction:
    chname = StrFunction("CHNAME", Cmd.GET, init="METAINFO")


class PlaybackFunction:
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunction:
    playbackinfo = EnumFunction[PlaybackInfo]("PLAYBACKINFO", PlaybackInfo, Cmd.GET)


class RepeatFunction:
    repeat = EnumFunction[Repeat]("REPEAT", Repeat)


class ShuffleFunction:
    shuffle = EnumFunction[Shuffle]("SHUFFLE", Shuffle)


class SongFunction:
    song = StrFunction("SONG", Cmd.GET, init="METAINFO")


class StationFunction:
    station = StrFunction("STATION", Cmd.GET)


# A number of subunits have the same/similar featureset
# so make a common base that only needs to be tested once
class MediaPlaybackSubunitBase(
    PlaybackFunction,
    PlaybackInfoFunction,
    RepeatFunction,
    ShuffleFunction,
    ArtistFunction,
    AlbumFunction,
    SongFunction,
    SubunitBase,
):
    pass


class FmFreqFunction:

    fmfreq = FloatFunction(
        "FMFREQ",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 2, 0.2)
        ),
    )
    """Read/write FM frequency. Values will be aligned to a valid stepsize."""
