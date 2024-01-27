from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
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
