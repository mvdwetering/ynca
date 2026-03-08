from __future__ import annotations

from ..constants import Subunit
from ..enums import SiriusSearchMode
from ..function import EnumFunctionMixin
from ..subunit import SubunitBase
from . import (
    ArtistFunctionMixin,
    ChNameFunctionMixin,
    MemFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    PresetFunctionMixin,
    PresetUpDownFunctionMixin,
    SongFunctionMixin,
)


class Sirius(
    ArtistFunctionMixin,
    ChNameFunctionMixin,
    MemFunctionMixin,
    PresetFunctionMixin,
    PresetUpDownFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUS

    searchmode = EnumFunctionMixin[SiriusSearchMode](SiriusSearchMode)


class SiriusIr(
    ArtistFunctionMixin,
    ChNameFunctionMixin,
    MemFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    PresetFunctionMixin,
    SongFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUSIR


class SiriusXm(
    PlaybackFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUSXM
