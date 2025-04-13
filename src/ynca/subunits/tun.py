from __future__ import annotations

from ..constants import Subunit
from ..converters import IntConverter
from ..enums import BandTun
from ..function import Cmd, EnumFunctionMixin, IntFunctionMixin, StrFunctionMixin
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase
from . import (
    FmFreqFunctionMixin,
    MemFunctionMixin,
    PresetFunctionMixin,
    PresetUpDownFunctionMixin,
)


class Tun(
    FmFreqFunctionMixin,
    MemFunctionMixin,
    PresetFunctionMixin,
    PresetUpDownFunctionMixin,
    SubunitBase,
):
    id = Subunit.TUN

    amfreq = IntFunctionMixin(
        converter=IntConverter(
            to_str=lambda v: number_to_string_with_stepsize(v, 0, 10)
        ),
    )
    """Read/write AM frequency. Values will be aligned to a valid stepsize."""

    band = EnumFunctionMixin[BandTun](BandTun)

    rdsprgservice = StrFunctionMixin(Cmd.GET, init="RDSINFO")
    rdsprgtype = StrFunctionMixin(Cmd.GET, init="RDSINFO")
    rdstxta = StrFunctionMixin(Cmd.GET, init="RDSINFO")
    rdstxtb = StrFunctionMixin(Cmd.GET, init="RDSINFO")
