from __future__ import annotations

from ..constants import Subunit
from ..converters import IntConverter
from ..function import Cmd, EnumFunction, IntFunction, StrFunction
from ..enums import BandTun
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase
from . import FmFreqFunction


class Tun(SubunitBase, FmFreqFunction):
    id = Subunit.TUN

    band = EnumFunction[BandTun]("BAND", BandTun)

    amfreq = IntFunction(
        "AMFREQ",
        converter=IntConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 0, 10)
        ),
    )
    """Read/write AM frequency. Values will be aligned to a valid stepsize."""

    rdsprgservice = StrFunction("RDSPRGSERVICE", Cmd.GET, init="RDSINFO")
    rdsprgtype = StrFunction("RDSPRGTYPE", Cmd.GET, init="RDSINFO")
    rdstxta = StrFunction("RDSTXTA", Cmd.GET, init="RDSINFO")
    rdstxtb = StrFunction("RDSTXTB", Cmd.GET, init="RDSINFO")
