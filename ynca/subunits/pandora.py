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
    TrackFunction,
)


class Pandora(
    PlaybackFunction,
    PlaybackInfoFunction,
    ArtistFunction,
    AlbumFunction,
    SongFunction,
    TrackFunction,    # Pandora seems to use TRACK or SONG for title based on logs. Maybe depends on firmware version?
    StationFunction,
    SubunitBase,
):
    id = Subunit.PANDORA
