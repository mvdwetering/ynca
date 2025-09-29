from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    TotalTimeFunctionMixin,
)


class Airplay(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    TotalTimeFunctionMixin,
    SubunitBase,
):
    id = Subunit.AIRPLAY
