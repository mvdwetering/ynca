from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    StationFunctionMixin,
    TrackFunctionMixin,
)


class Pandora(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    StationFunctionMixin,
    TrackFunctionMixin,  # Pandora seems to use TRACK or SONG for title based on logs. Maybe depends on firmware version?
    SubunitBase,
):
    id = Subunit.PANDORA
