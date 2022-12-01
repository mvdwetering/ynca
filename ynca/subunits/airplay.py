from __future__ import annotations

from ..constants import Subunit
from . import PlaybackFunction
from ..subunit import SubunitBase


class Airplay(
    PlaybackFunction,
    SubunitBase,
):
    id = Subunit.AIRPLAY
