from __future__ import annotations

import logging

from .connection import YncaConnection
from .constants import Subunit
from .function_mixins import (
    MetainfoFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    RepeatShuffleFunctionMixin,
)
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class Pc(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    MetainfoFunctionMixin,
    RepeatShuffleFunctionMixin,
    SubunitBase,
):
    def __init__(
        self,
        connection: YncaConnection,
    ):
        super().__init__(Subunit.PC, connection)
