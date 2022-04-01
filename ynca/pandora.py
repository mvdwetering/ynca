from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    MetainfoFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    StationFunctionMixin,
)
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class Pandora(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    MetainfoFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.PANDORA
