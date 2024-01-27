from __future__ import annotations

from ..constants import Subunit
from . import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    SubunitBase,
    TrackFunctionMixin,
)


class Spotify(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    ArtistFunctionMixin,
    AlbumFunctionMixin,
    TrackFunctionMixin,
    SubunitBase,
):
    id = Subunit.SPOTIFY
