from __future__ import annotations

from .constants import Subunit
from .function_mixins import (PlaybackFunctionMixin, PlaybackInfoFunctionMixin,
                              StationFunctionMixin)
from .subunit import SubunitBase


class NetRadio(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.NETRADIO
