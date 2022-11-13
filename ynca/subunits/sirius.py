from __future__ import annotations

from ..constants import Subunit
from .functions import (
    ArtistFunction,
    ChannelnameFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    SongFunction,
)
from ..subunit import SubunitBase


class Sirius(
    ArtistFunction,
    SongFunction,
    ChannelnameFunction,
    SubunitBase,
):
    id = Subunit.SIRIUS


class SiriusIr(
    ArtistFunction,
    SongFunction,
    ChannelnameFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    SubunitBase,
):
    id = Subunit.SIRIUSIR


class SiriusXm(
    PlaybackFunction,
    SubunitBase,
):
    id = Subunit.SIRIUSXM
