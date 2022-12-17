from __future__ import annotations

from ..constants import Subunit
from ..function import Cmd, EnumFunction, StrFunction
from ..enums import (
    BandDab,
)
from ..subunit import SubunitBase
from . import FmFreqFunction


class Dab(SubunitBase, FmFreqFunction):
    id = Subunit.DAB

    band = EnumFunction[BandDab]("BAND", BandDab)

    dabchlabel = StrFunction("DABCHLABEL", Cmd.GET)
    dabdlslabel = StrFunction("DABDLSLABEL", Cmd.GET)
    dabensemblelabel = StrFunction("DABENSEMBLELABEL", Cmd.GET)
    dabservicelabel = StrFunction("DABSERVICELABEL", Cmd.GET)
    dabprgtype = StrFunction("DABPRGTYPE", Cmd.GET)

    fmrdsprgservice = StrFunction("FMRDSPRGSERVICE", Cmd.GET, init="FMRDSINFO")
    fmrdsprgtype = StrFunction("FMRDSPRGTYPE", Cmd.GET, init="FMRDSINFO")
    fmrdstxt = StrFunction("FMRDSTXT", Cmd.GET, init="FMRDSINFO")
