from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import (
    ArtistFunctionMixin,
    ChNameFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
)


class Sirius(
    ArtistFunctionMixin,
    SongFunctionMixin,
    ChNameFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUS


class SiriusIr(
    ArtistFunctionMixin,
    SongFunctionMixin,
    ChNameFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUSIR


class SiriusXm(
    PlaybackFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUSXM
