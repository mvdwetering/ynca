from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import PlaybackFunction, PlaybackInfoFunction, StationFunction


class NetRadio(
    PlaybackFunction,
    PlaybackInfoFunction,
    StationFunction,
    SubunitBase,
):
    id = Subunit.NETRADIO
