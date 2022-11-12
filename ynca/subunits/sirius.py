from __future__ import annotations

from ..constants import Subunit
from .function_mixins import (
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
)
from ..subunit import SubunitBase
from ..ynca_function import Cmd, StrFunction


class ChannelnameFunctionMixin:
    chname = StrFunction("CHNAME", cmd=Cmd.GET, init="METAINFO")


class Sirius(
    ArtistFunctionMixin,
    SongFunctionMixin,
    ChannelnameFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUS


class SiriusIr(
    ArtistFunctionMixin,
    SongFunctionMixin,
    ChannelnameFunctionMixin,
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
