from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import AlbumFunctionMixin, PlaybackFunctionMixin, PlaybackInfoFunctionMixin, SongFunctionMixin, StationFunctionMixin


class NetRadio(
    AlbumFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.NETRADIO
