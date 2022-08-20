from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    StationFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
)
from .subunit import SubunitBase


class NetRadio(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.NETRADIO
