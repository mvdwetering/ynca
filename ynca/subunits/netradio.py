from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import PlaybackFunctionMixin, PlaybackInfoFunctionMixin, StationFunctionMixin


class NetRadio(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    id = Subunit.NETRADIO
