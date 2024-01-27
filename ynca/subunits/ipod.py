from __future__ import annotations


from ..constants import Subunit
from ..subunit import SubunitBase
from . import MediaPlaybackMixins


class Ipod(MediaPlaybackMixins, SubunitBase):
    id = Subunit.IPOD
