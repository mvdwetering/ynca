from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import PlaybackFunctionMixin


class Bt(SubunitBase, PlaybackFunctionMixin):
    id = Subunit.BT
