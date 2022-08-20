from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    MetainfoFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatShuffleFunctionMixin,
)
from .subunit import SubunitBase


# A number of subunits have the same featureset
# so make a common base that only needs to be tested once
class MediaPlaybackSubunitBase(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    MetainfoFunctionMixin,
    RepeatShuffleFunctionMixin,
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


# These are assumed capabilities
# Could not really get it correctly from the logs
# But this is what I would expect.
class Spotify(MediaPlaybackSubunitBase):
    id = Subunit.SPOTIFY


class Server(MediaPlaybackSubunitBase):
    id = Subunit.SERVER
