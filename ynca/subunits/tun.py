from __future__ import annotations

from ynca.subunits import FmFreqFunction

from ..constants import AssertNegate, BandTun, Preset, SigStereoMono, Subunit, Tuned
from ..converters import IntConverter
from ..helpers import number_to_string_with_stepsize
from ..subunit import SubunitBase
from ..function import (
    Cmd,
    EnumFunction,
    EnumOrIntFunction,
    IntFunction,
    StrFunction,
)


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

    preset = EnumOrIntFunction("PRESET", Preset)

    def preset_down(self):
        self._put("PRESET", "Down")  # type: ignore

    def preset_up(self):
        self._put("PRESET", "Up")  # type: ignore

    rdsprgservice = StrFunction("RDSPRGSERVICE", Cmd.GET, init="RDSINFO")
    rdsprgtype = StrFunction("RDSPRGTYPE", Cmd.GET, init="RDSINFO")
    rdstxta = StrFunction("RDSTXTA", Cmd.GET, init="RDSINFO")
    rdstxtb = StrFunction("RDSTXTB", Cmd.GET, init="RDSINFO")
    sigstereomono = EnumFunction[AssertNegate]("SIGSTEREOMONO", AssertNegate, Cmd.GET)
    tuned = EnumFunction[AssertNegate]("TUNED", AssertNegate, Cmd.GET)
