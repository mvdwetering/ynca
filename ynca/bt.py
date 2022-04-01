from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    PlaybackFunctionMixin,
)
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class Bt(
    PlaybackFunctionMixin,
    SubunitBase,
):
    id = Subunit.BT
