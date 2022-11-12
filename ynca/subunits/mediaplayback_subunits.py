from __future__ import annotations

from ..constants import Subunit
from .function_mixins import (
    AlbumFunctionMixin,
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    SongFunctionMixin,
)
from ..subunit import SubunitBase


# A number of subunits have the same/similar featureset
# so make a common base that only needs to be tested once
class MediaPlaybackSubunitBase(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatFunctionMixin,
    ShuffleFunctionMixin,
    ArtistFunctionMixin,
    AlbumFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    pass


class Rhap(MediaPlaybackSubunitBase):
    id = Subunit.RHAP


class Usb(MediaPlaybackSubunitBase):
    id = Subunit.USB


class Pc(MediaPlaybackSubunitBase):
    id = Subunit.PC


class Ipod(MediaPlaybackSubunitBase):
    id = Subunit.IPOD


class Napster(MediaPlaybackSubunitBase):
    id = Subunit.NAPSTER


class IpodUsb(MediaPlaybackSubunitBase):
    id = Subunit.IPODUSB


class Spotify(MediaPlaybackSubunitBase):
    id = Subunit.SPOTIFY


class Server(MediaPlaybackSubunitBase):
    id = Subunit.SERVER
