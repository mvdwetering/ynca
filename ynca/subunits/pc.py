from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    MemFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    PresetFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    SongFunctionMixin,
)


class Pc(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    MemFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    PresetFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    id = Subunit.PC
