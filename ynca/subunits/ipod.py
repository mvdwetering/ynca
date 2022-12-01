from __future__ import annotations

from ..constants import Subunit
from . import MediaPlaybackSubunitBase


class Ipod(MediaPlaybackSubunitBase):
    id = Subunit.IPOD
