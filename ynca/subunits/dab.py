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

    band = EnumFunction[BandDab](BandDab)

    dabchlabel = StrFunction(Cmd.GET)
    dabdlslabel = StrFunction(Cmd.GET)
    dabensemblelabel = StrFunction(Cmd.GET)
    dabservicelabel = StrFunction(Cmd.GET)
    dabprgtype = StrFunction(Cmd.GET)

    fmrdsprgservice = StrFunction(Cmd.GET, init="FMRDSINFO")
    fmrdsprgtype = StrFunction(Cmd.GET, init="FMRDSINFO")
    fmrdstxt = StrFunction(Cmd.GET, init="FMRDSINFO")
