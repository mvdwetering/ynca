from __future__ import annotations

from ..constants import Subunit
from ..function import Cmd, EnumFunctionMixin, StrFunctionMixin
from ..enums import (
    BandDab,
)
from ..subunit import SubunitBase
from . import FmFreqFunctionMixin


class Dab(SubunitBase, FmFreqFunctionMixin):
    id = Subunit.DAB

    band = EnumFunctionMixin[BandDab](BandDab)

    dabchlabel = StrFunctionMixin(Cmd.GET)
    dabdlslabel = StrFunctionMixin(Cmd.GET)
    dabensemblelabel = StrFunctionMixin(Cmd.GET)
    dabservicelabel = StrFunctionMixin(Cmd.GET)
    dabprgtype = StrFunctionMixin(Cmd.GET)

    fmrdsprgservice = StrFunctionMixin(Cmd.GET, init="FMRDSINFO")
    fmrdsprgtype = StrFunctionMixin(Cmd.GET, init="FMRDSINFO")
    fmrdstxt = StrFunctionMixin(Cmd.GET, init="FMRDSINFO")
