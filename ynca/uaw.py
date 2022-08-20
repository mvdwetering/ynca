from __future__ import annotations

import logging

from .constants import Subunit
from .subunit import SubunitBase


class Uaw(
    SubunitBase,
):
    id = Subunit.UAW
