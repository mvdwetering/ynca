from __future__ import annotations

from ..constants import Subunit
from .functions import (
    AlbumFunction,
    ArtistFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    SongFunction,
    StationFunction,
)
from ..subunit import SubunitBase


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
