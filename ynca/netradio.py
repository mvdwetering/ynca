from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    StationFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
)
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class NetRadio(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.NETRADIO
