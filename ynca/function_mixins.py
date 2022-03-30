from __future__ import annotations
import logging
from typing import Optional, List

from .constants import Repeat, Playback, PlaybackInfo

logger = logging.getLogger(__name__)


class FunctionMixinBase:
    """
    Mixin baseclass that handles a function (or group of related functions) of the YNCA interface.
    Using subclasses should make it easy to share function implementations between Subunits.

    This base is needed to find them in the inheritance tree.
    It does not really feel in the spiriti of Mixins, but it gets the job done.
    Using prefixes on everything to keep chance on collisions low.

    Note that FunctionMixins are intended to be used with Subunits.
    This means that methods like `_put` will exist, but `mypy` can not
    figure that out (understandably) so will be ignored in those places.
    """

    # Functions to request on initialization of the subunit
    FUNCTION_MIXIN_FUNCTIONS: List[str] = []

    def function_mixin_initialize_attributes(self):
        # Initialize attributes managed by this mixin
        pass


class PlaybackFunctionMixin(FunctionMixinBase):
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["PLAYBACKINFO"]

    def function_mixin_initialize_attributes(self):
        self._attr_playbackinfo: str | None = None

    @property
    def playbackinfo(self):
        return (
            PlaybackInfo(self._attr_playbackinfo)
            if self._attr_playbackinfo is not None
            else None
        )


class MetainfoFunctionMixin(FunctionMixinBase):

    # METAINFO gets ARTIST, ALBUM and SONG
    FUNCTION_MIXIN_FUNCTIONS = ["METAINFO"]

    def function_mixin_initialize_attributes(self):
        self._attr_artist: str | None = None
        self._attr_album: str | None = None
        self._attr_song: str | None = None

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


class RepeatShuffleFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["REPEAT", "SHUFFLE"]

    def function_mixin_initialize_attributes(self):
        self._attr_repeat: str | None = None
        self._attr_shuffle: str | None = None

    @property
    def repeat(self) -> Optional[Repeat]:
        """Get repeat"""
        return Repeat(self._attr_repeat) if self._attr_repeat is not None else None

    @repeat.setter
    def repeat(self, value: Repeat):
        """Set repeat mode"""
        self._put("REPEAT", value)  # type: ignore

    @property
    def shuffle(self) -> Optional[bool]:
        """Get current shuffle state"""
        return self._attr_shuffle == "On" if self._attr_shuffle is not None else None

    @shuffle.setter
    def shuffle(self, value: bool):
        """Turn on/off shuffle"""
        self._put("SHUFFLE", "On" if value is True else "Off")  # type: ignore