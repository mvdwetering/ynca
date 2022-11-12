from __future__ import annotations

from ..constants import Subunit
from .functions import (
    PlaybackFunction,
    PlaybackInfoFunction,
    StationFunction,
)
from ..subunit import SubunitBase


class NetRadio(
    PlaybackFunction,
    PlaybackInfoFunction,
    StationFunction,
    SubunitBase,
):
    id = Subunit.NETRADIO
