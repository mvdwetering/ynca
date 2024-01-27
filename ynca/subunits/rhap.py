from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import MediaPlaybackMixins


class Rhap(MediaPlaybackMixins, SubunitBase):
    id = Subunit.RHAP
