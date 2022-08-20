from __future__ import annotations
import logging
from typing import Optional, List

from .constants import Repeat, Playback, PlaybackInfo


class FunctionMixinBase:
    """
    Mixin baseclass that handles a function (or group of related functions) of the YNCA interface.
    Using subclasses should make it easy to share function implementations between Subunits.

    This base is needed to find them in the inheritance tree.
    It does not really feel in the spirit of Mixins, but it gets the job done.
    Using prefixes on everything to keep chance on collisions low.

    Note that FunctionMixins are intended to be used with Subunits.
    This means that methods like `_put` will exist, but `mypy` can not
    figure that out (understandably) so will be ignored in those places.
    """

    # Functions to request on initialization of the subunit
    FUNCTION_MIXIN_FUNCTIONS: List[str] = []

    def function_mixin_on_initialize_attributes(self):
        # Initialize attributes managed by this mixin
        # To be implemented in subclasses
        pass

    def function_mixin_functions(self):
        functions = []
        for function_mixin_class in self._function_mixin_classes():
            functions.extend(function_mixin_class.FUNCTION_MIXIN_FUNCTIONS)
        return functions

    def function_mixin_initialize_function_attributes(self):
        for function_mixin_class in self._function_mixin_classes():
            function_mixin_class.function_mixin_on_initialize_attributes(self)

    def _function_mixin_classes(self):
        # Go through the inheritance list and return direct descendants of FunctionMixinBase
        # Direct descendant derived from mro list has length 3
        # which is the [mixinclass, mixinfunctionbaseclass, object]
        for function_mixin_class in self.__class__.__mro__:
            if (
                issubclass(function_mixin_class, FunctionMixinBase)
                and len(function_mixin_class.__mro__) == 3
            ):
                yield function_mixin_class


class PlaybackFunctionMixin(FunctionMixinBase):
    def playback(self, parameter: Playback):
        """Change playback state"""
        self._put("PLAYBACK", parameter)  # type: ignore


class PlaybackInfoFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["PLAYBACKINFO"]

    def function_mixin_on_initialize_attributes(self):
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

    def function_mixin_on_initialize_attributes(self):
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


class StationFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["STATION"]

    def function_mixin_on_initialize_attributes(self):
        self._attr_station: str | None = None

    @property
    def station(self) -> Optional[str]:
        """Get current station"""
        return self._attr_station


class RepeatShuffleFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["REPEAT", "SHUFFLE"]

    def function_mixin_on_initialize_attributes(self):
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


class PowerFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["PWR"]

    def function_mixin_on_initialize_attributes(self):
        self._attr_pwr: str | None = None

    @property
    def pwr(self) -> Optional[bool]:
        """Get power state of subunit"""
        return self._attr_pwr == "On" if self._attr_pwr is not None else None

    @pwr.setter
    def pwr(self, value: bool):
        """Turn on/off subunit"""
        self._put("PWR", "On" if value is True else "Standby")  # type: ignore
