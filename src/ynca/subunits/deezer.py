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
    TotalTimeFunctionMixin,
    TrackFunctionMixin,
)


class Deezer(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    TotalTimeFunctionMixin,
    TrackFunctionMixin,
    SubunitBase,
):
    id = Subunit.DEEZER
