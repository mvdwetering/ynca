from __future__ import annotations

import logging

from .constants import Subunit
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class Uaw(
    SubunitBase,
):
    id = Subunit.UAW
