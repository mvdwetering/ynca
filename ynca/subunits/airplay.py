from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunction,
    ArtistFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    SongFunction,
)


class Airplay(
    AlbumFunction,
    ArtistFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    SongFunction,
    SubunitBase,
):
    id = Subunit.AIRPLAY
