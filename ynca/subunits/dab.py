from __future__ import annotations

from ..constants import Subunit
from ..enums import BandDab, DabPreset, FmPreset
from ..function import (
    Cmd,
    EnumFunctionMixin,
    EnumOrIntFunctionMixin,
    StrFunctionMixin,
)
from ..subunit import SubunitBase
from . import FmFreqFunctionMixin, MemFunctionMixin


class Dab(SubunitBase, FmFreqFunctionMixin, MemFunctionMixin):
    id = Subunit.DAB

    band = EnumFunctionMixin[BandDab](BandDab)

    dabchlabel = StrFunctionMixin(Cmd.GET)
    dabdlslabel = StrFunctionMixin(Cmd.GET)
    dabensemblelabel = StrFunctionMixin(Cmd.GET)
    dabservicelabel = StrFunctionMixin(Cmd.GET)
    dabpreset = EnumOrIntFunctionMixin[DabPreset](DabPreset)
    dabprgtype = StrFunctionMixin(Cmd.GET)

    fmpreset = EnumOrIntFunctionMixin[FmPreset](FmPreset)
    fmrdsprgservice = StrFunctionMixin(Cmd.GET, init="FMRDSINFO")
    fmrdsprgtype = StrFunctionMixin(Cmd.GET, init="FMRDSINFO")
    fmrdstxt = StrFunctionMixin(Cmd.GET, init="FMRDSINFO")
