from __future__ import annotations

from ..constants import Subunit
from . import (
    AlbumFunction,
    ArtistFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    RepeatFunction,
    ShuffleFunction,
    SubunitBase,
    TrackFunction,
)


class Spotify(
    PlaybackFunction,
    PlaybackInfoFunction,
    RepeatFunction,
    ShuffleFunction,
    ArtistFunction,
    AlbumFunction,
    TrackFunction,
    SubunitBase,
):
    id = Subunit.SPOTIFY
