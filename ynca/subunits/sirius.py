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
    ChNameFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUS


class SiriusIr(
    ArtistFunctionMixin,
    ChNameFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUSIR


class SiriusXm(
    PlaybackFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUSXM
