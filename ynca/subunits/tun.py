from __future__ import annotations

from ..constants import Subunit
from ..converters import IntConverter
from ..function import Cmd, EnumFunctionMixin, IntFunctionMixin, StrFunctionMixin
from ..enums import BandTun
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase
from . import FmFreqFunctionMixin


class Tun(FmFreqFunctionMixin, SubunitBase):
    id = Subunit.TUN

    band = EnumFunctionMixin[BandTun](BandTun)

    amfreq = IntFunctionMixin(
        converter=IntConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 0, 10)
        ),
    )
    """Read/write AM frequency. Values will be aligned to a valid stepsize."""

    rdsprgservice = StrFunctionMixin(Cmd.GET, init="RDSINFO")
    rdsprgtype = StrFunctionMixin(Cmd.GET, init="RDSINFO")
    rdstxta = StrFunctionMixin(Cmd.GET, init="RDSINFO")
    rdstxtb = StrFunctionMixin(Cmd.GET, init="RDSINFO")
