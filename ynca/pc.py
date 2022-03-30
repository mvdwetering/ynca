from __future__ import annotations
import logging
from typing import Optional

from .connection import YncaConnection
from .constants import Repeat
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class Pc(SubunitBase):
    def __init__(
        self,
        subunit_id: str,
        connection: YncaConnection,
    ):
        super().__init__(subunit_id, connection)
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._attr_repeat: str | None = None
        self._attr_shuffle: str | None = None
        self._attr_playbackinfo: str | None = None
        self._attr_artist: str | None = None
        self._attr_album: str | None = None
        self._attr_song: str | None = None

    def on_initialize(self):
        self._reset_internal_state()

        self._get("REPEAT")
        self._get("SHUFFLE")
        self._get("PLAYBACKINFO")
        # METAINFO gets ARTIST, ALBUM and SONG
        self._get("METAINFO")

    @property
    def repeat(self) -> Optional[Repeat]:
        """Get repeat"""
        return Repeat(self._attr_repeat) if self._attr_repeat is not None else None

    @repeat.setter
    def repeat(self, value: Repeat):
        """Set repeat mode"""
        self._put("REPEAT", value)

    @property
    def shuffle(self) -> Optional[bool]:
        """Get current shuffle state"""
        return self._attr_shuffle == "On" if self._attr_shuffle is not None else None

    @shuffle.setter
    def shuffle(self, value: bool):
        """Turn on/off shuffle"""
        self._put("SHUFFLE", "On" if value is True else "Off")

    @property
    def artist(self) -> Optional[str]:
        """Get current artist"""
        return self._attr_artist

    @property
    def album(self) -> Optional[str]:
        """Get current album"""
        return self._attr_album

    @property
    def song(self) -> Optional[str]:
        """Get current song"""
        return self._attr_song

    def play(self):
        """Play current song"""
        self._put("PLAYBACK", "Play")

    def pause(self):
        """Pause current song"""
        self._put("PLAYBACK", "Pause")

    def stop(self):
        """Stop current song"""
        self._put("PLAYBACK", "Stop")

    def skip_reverse(self):
        """Skip reverse song"""
        # self._put("PLAYBACK", "Skip Rev")
        self._put("PLAYBACK", "|<<")

    def skip_forward(self):
        """Skip forward song"""
        # self._put("PLAYBACK", "Skip Fwd")
        self._put("PLAYBACK", ">>|")
