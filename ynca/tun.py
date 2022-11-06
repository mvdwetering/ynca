from __future__ import annotations

from .constants import Band, Subunit
from .helpers import number_to_string_with_stepsize
from .subunit import SubunitBase, YncaFunction


class Tun(SubunitBase):
    id = Subunit.TUN

    band = YncaFunction[Band]("BAND", Band)
    amfreq = YncaFunction[int](
        "AMFREQ",
        int,
        str_converter=lambda v: number_to_string_with_stepsize(v, 0, 10),
    )
    """Read/write AM frequency. When writing the values will be aligned to a valid stepsize."""

    fmfreq = YncaFunction[float](
        "FMFREQ",
        float,
        str_converter=lambda v: number_to_string_with_stepsize(v, 2, 0.2),
    )
    """Read/write FM frequency. When writing the values will be aligned to a valid stepsize."""
