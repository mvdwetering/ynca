from __future__ import annotations

from enum import Enum

from ..constants import Playback, PlaybackInfo, Repeat
from ..function import Cmd, EnumFunction, StrFunction


class PlaybackFunction:
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunction:
    playbackinfo = EnumFunction[PlaybackInfo]("PLAYBACKINFO", PlaybackInfo, cmd=Cmd.GET)


class ArtistFunction:
    artist = StrFunction("ARTIST", cmd=Cmd.GET, init="METAINFO")


class AlbumFunction:
    album = StrFunction("ALBUM", cmd=Cmd.GET, init="METAINFO")


class SongFunction:
    song = StrFunction("SONG", cmd=Cmd.GET, init="METAINFO")


class StationFunction:
    station = StrFunction("STATION", cmd=Cmd.GET)


class RepeatFunction:
    repeat = EnumFunction[Repeat]("REPEAT", Repeat)


class Shuffle(Enum):
    ON = "On"
    OFF = "Off"


class ShuffleFunction:
    shuffle = EnumFunction[Shuffle]("SHUFFLE", Shuffle)


class Pwr(Enum):
    ON = "On"
    STANDBY = "Standby"
