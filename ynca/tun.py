from __future__ import annotations

from .constants import Band, Subunit
from .helpers import number_to_string_with_stepsize
from .converters import (
    FloatConverter,
    IntConverter,
)
from .ynca_function import (
    YncaFunctionEnum,
    YncaFunctionFloat,
    YncaFunctionInt,
)
from .subunit import SubunitBase


class Tun(SubunitBase):
    id = Subunit.TUN

    band = YncaFunctionEnum[Band]("BAND", Band)

    amfreq = YncaFunctionInt(
        "AMFREQ",
        converter=IntConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 0, 10)
        ),
    )
    """Read/write AM frequency. Values will be aligned to a valid stepsize."""

    fmfreq = YncaFunctionFloat(
        "FMFREQ",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 2, 0.2)
        ),
    )
    """Read/write FM frequency. Values will be aligned to a valid stepsize."""
