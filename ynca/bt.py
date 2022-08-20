from __future__ import annotations

import logging

from .constants import Subunit
from .function_mixins import (
    PlaybackFunctionMixin,
)
from .subunit import SubunitBase


class Bt(
    PlaybackFunctionMixin,
    SubunitBase,
):
    id = Subunit.BT
