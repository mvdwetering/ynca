from __future__ import annotations

from ..constants import Subunit
from . import MediaPlaybackSubunitBase


class Spotify(MediaPlaybackSubunitBase):
    id = Subunit.SPOTIFY
