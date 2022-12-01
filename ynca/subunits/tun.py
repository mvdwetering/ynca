from __future__ import annotations

from ..constants import BandTun, Subunit
from ..converters import FloatConverter, IntConverter
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase
from ..function import EnumFunction, FloatFunction, IntFunction


class Tun(SubunitBase):
    id = Subunit.TUN

    band = EnumFunction[BandTun]("BAND", BandTun)

    amfreq = IntFunction(
        "AMFREQ",
        converter=IntConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 0, 10)
        ),
    )
    """Read/write AM frequency. Values will be aligned to a valid stepsize."""

    fmfreq = FloatFunction(
        "FMFREQ",
        converter=FloatConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 2, 0.2)
        ),
    )
    """Read/write FM frequency. Values will be aligned to a valid stepsize."""
