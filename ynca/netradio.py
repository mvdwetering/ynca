from __future__ import annotations

import logging

from .connection import YncaConnection
from .constants import Subunit
from .function_mixins import (
    StationFunctionMixin,
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
)
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class NetRadio(
    PlaybackFunctionMixin,
    PlaybackInfoFunctionMixin,
    StationFunctionMixin,
    SubunitBase,
):
    def __init__(
        self,
        connection: YncaConnection,
    ):
        super().__init__(Subunit.NETRADIO, connection)
