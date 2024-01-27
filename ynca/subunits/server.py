from __future__ import annotations

from ..constants import Subunit
from ..subunit import SubunitBase
from . import MediaPlaybackMixins


class Server(MediaPlaybackMixins, SubunitBase):
    id = Subunit.SERVER
