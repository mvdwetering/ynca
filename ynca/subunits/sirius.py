from __future__ import annotations

from ..constants import Subunit
from .functions import (
    ArtistFunction,
    ChNameFunction,
    PlaybackFunction,
    PlaybackInfoFunction,
    SongFunction,
)
from ..subunit import SubunitBase


class Sirius(
    ArtistFunction,
    SongFunction,
    ChNameFunction,
    SubunitBase,
):
    id = Subunit.SIRIUS


class SiriusIr(
    ArtistFunction,
    SongFunction,
    ChNameFunction,
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
