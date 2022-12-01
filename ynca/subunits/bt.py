from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import PlaybackFunction


class Bt(SubunitBase, PlaybackFunction):
    id = Subunit.BT
