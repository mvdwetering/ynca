from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    ArtistFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    SongFunctionMixin,
)
from .ynca_function import CommandType, YncaFunctionStr
from .subunit import SubunitBase


class ChannelnameFunctionMixin:
    chname = YncaFunctionStr(
        "CHNAME", command_type=CommandType.GET, initialize_function_name="METAINFO"
    )


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
