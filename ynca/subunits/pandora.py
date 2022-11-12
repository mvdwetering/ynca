from __future__ import annotations

from ..constants import Subunit
from .function_mixins import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    StationFunctionMixin,
)
from ..subunit import SubunitBase


class Pandora(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    ArtistFunctionMixin,
    AlbumFunctionMixin,
    SongFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.PANDORA
