from __future__ import annotations

from ..subunit import SubunitBase
from ..constants import Playback, PlaybackInfo, Repeat, Shuffle
from ..function import Cmd, EnumFunction, StrFunction


class AlbumFunction:
    album = StrFunction("ALBUM", cmd=Cmd.GET, init="METAINFO")


class ArtistFunction:
    artist = StrFunction("ARTIST", cmd=Cmd.GET, init="METAINFO")


class ChNameFunction:
    chname = StrFunction("CHNAME", cmd=Cmd.GET, init="METAINFO")


class PlaybackFunction:
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunction:
    playbackinfo = EnumFunction[PlaybackInfo]("PLAYBACKINFO", PlaybackInfo, cmd=Cmd.GET)


class RepeatFunction:
    repeat = EnumFunction[Repeat]("REPEAT", Repeat)


class ShuffleFunction:
    shuffle = EnumFunction[Shuffle]("SHUFFLE", Shuffle)


class SongFunction:
    song = StrFunction("SONG", cmd=Cmd.GET, init="METAINFO")


class StationFunction:
    station = StrFunction("STATION", cmd=Cmd.GET)


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
