from __future__ import annotations

from ..constants import Subunit
from . import MediaPlaybackSubunitBase


class Server(MediaPlaybackSubunitBase):
    id = Subunit.SERVER
