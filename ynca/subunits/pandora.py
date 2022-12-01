from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunction,
    ArtistFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    SongFunction,
    StationFunction,
)


class Pandora(
    PlaybackFunction,
    PlaybackInfoFunction,
    ArtistFunction,
    AlbumFunction,
    SongFunction,
    StationFunction,
    SubunitBase,
):
    id = Subunit.PANDORA
