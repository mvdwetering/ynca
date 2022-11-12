from __future__ import annotations

from enum import Enum

from .constants import Playback, PlaybackInfo, Repeat
from .ynca_function import CommandType, YncaFunctionEnum, YncaFunctionStr


class PlaybackFunctionMixin:
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunctionMixin:
    playbackinfo = YncaFunctionEnum[PlaybackInfo](
        "PLAYBACKINFO", PlaybackInfo, command_type=CommandType.GET
    )


class ArtistFunctionMixin:
    artist = YncaFunctionStr(
        "ARTIST", command_type=CommandType.GET, initialize_function_name="METAINFO"
    )


class AlbumFunctionMixin:
    album = YncaFunctionStr(
        "ALBUM", command_type=CommandType.GET, initialize_function_name="METAINFO"
    )


class SongFunctionMixin:
    song = YncaFunctionStr(
        "SONG", command_type=CommandType.GET, initialize_function_name="METAINFO"
    )


class StationFunctionMixin:
    station = YncaFunctionStr("STATION", command_type=CommandType.GET)


class RepeatFunctionMixin:
    repeat = YncaFunctionEnum[Repeat]("REPEAT", Repeat)


class Shuffle(Enum):
    ON = "On"
    OFF = "Off"


class ShuffleFunctionMixin:
    shuffle = YncaFunctionEnum[Shuffle]("SHUFFLE", Shuffle)


class Pwr(Enum):
    ON = "On"
    STANDBY = "Standby"
