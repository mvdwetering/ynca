from __future__ import annotations

import logging
from typing import Optional

from .constants import Subunit
from .function_mixins import (
    FunctionMixinBase,
    MetainfoFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
)
from .subunit import SubunitBase


class ChannelnameFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["CHNAME"]

    def function_mixin_on_initialize_attributes(self):
        self._attr_chname: str | None = None

    @property
    def chname(self) -> Optional[str]:
        """Get channelname of subunit"""
        return self._attr_chname


class Sirius(
    # Note that Sirius subunit does not support Album,
    # so it will stay None which should be fine
    # It does support additional items with the METAINFO request
    # like CATNAM, CHNUM, CHNAME, but have no use for those right now
    MetainfoFunctionMixin,
    ChannelnameFunctionMixin,
    SubunitBase,
):
    id = Subunit.SIRIUS


class SiriusIr(
    # Note that SiriusIR subunit does not support Album,
    # so it will stay None which should be fine
    # It does support additional items with the METAINFO request
    # like CHNAME, but have no use for that right now
    MetainfoFunctionMixin,
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
