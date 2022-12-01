from __future__ import annotations

from ..constants import Subunit
from . import MediaPlaybackSubunitBase


class Usb(MediaPlaybackSubunitBase):
    id = Subunit.USB
