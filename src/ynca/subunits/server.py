from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    SongFunctionMixin,
    TotalTimeFunctionMixin,
)


class Server(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    SongFunctionMixin,
    TotalTimeFunctionMixin,
    SubunitBase,
):
    id = Subunit.SERVER
