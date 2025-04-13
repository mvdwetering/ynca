from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    AlbumFunctionMixin,
    MemFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    PresetFunctionMixin,
    SongFunctionMixin,
    StationFunctionMixin,
)


class NetRadio(
    AlbumFunctionMixin,
    MemFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    PresetFunctionMixin,
    SongFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.NETRADIO
