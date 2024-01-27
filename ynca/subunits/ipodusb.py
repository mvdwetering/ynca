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
    SongFunctionMixin,
)


class IpodUsb(
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    id = Subunit.IPODUSB
