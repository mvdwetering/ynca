from __future__ import annotations

from enum import Enum

from ..constants import Playback, PlaybackInfo, Repeat
from ..ynca_function import Cmd, EnumFunction, StrFunction


class PlaybackFunctionMixin:
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunctionMixin:
    playbackinfo = EnumFunction[PlaybackInfo]("PLAYBACKINFO", PlaybackInfo, cmd=Cmd.GET)


class ArtistFunctionMixin:
    artist = StrFunction("ARTIST", cmd=Cmd.GET, init="METAINFO")


class AlbumFunctionMixin:
    album = StrFunction("ALBUM", cmd=Cmd.GET, init="METAINFO")


class SongFunctionMixin:
    song = StrFunction("SONG", cmd=Cmd.GET, init="METAINFO")


class StationFunctionMixin:
    station = StrFunction("STATION", cmd=Cmd.GET)


class RepeatFunctionMixin:
    repeat = EnumFunction[Repeat]("REPEAT", Repeat)


class Shuffle(Enum):
    ON = "On"
    OFF = "Off"


class ShuffleFunctionMixin:
    shuffle = EnumFunction[Shuffle]("SHUFFLE", Shuffle)


class Pwr(Enum):
    ON = "On"
    STANDBY = "Standby"
