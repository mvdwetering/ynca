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
)


class McLink(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    """Subunit for MusicCast Link (MCLINK)."""

    id = Subunit.MCLINK
