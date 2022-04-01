from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    MetainfoFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatShuffleFunctionMixin,
)
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class Usb(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    MetainfoFunctionMixin,
    RepeatShuffleFunctionMixin,
    SubunitBase,
):
    id = Subunit.USB
