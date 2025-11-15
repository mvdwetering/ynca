from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
)


class McLink(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    ElapsedTimeFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    """Subunit for MusicCast Link (MCLINK)."""

    id = Subunit.MCLINK
