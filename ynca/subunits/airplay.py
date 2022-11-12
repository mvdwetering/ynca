from __future__ import annotations

from ..constants import Subunit
from .functions import PlaybackFunction
from ..subunit import SubunitBase


class Airplay(
    PlaybackFunction,
    SubunitBase,
):
    id = Subunit.AIRPLAY
