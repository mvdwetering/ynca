from __future__ import annotations

from ..function import Cmd, EnumFunction, EnumOrIntFunction, StrFunction

from ..constants import (
    BandDab,
    DabAudioMode,
    DabOffAir,
    Preset,
    FmSigStereoMono,
    FmTuned,
    Subunit,
)
from ..subunit import SubunitBase
from . import FmFreqFunction


class Dab(SubunitBase, FmFreqFunction):
    id = Subunit.DAB

    band = EnumFunction[BandDab]("BAND", BandDab)

    dabaudiomode = EnumFunction[DabAudioMode]("DABAUDIOMODE", DabAudioMode, Cmd.GET)
    dabchlabel = StrFunction("DABCHLABEL", Cmd.GET)
    dabdlslabel = StrFunction("DABDLSLABEL", Cmd.GET)
    dabensemblelabel = StrFunction("DABENSEMBLELABEL", Cmd.GET)
    daboffair = EnumFunction[DabOffAir]("DABOFFAIR", DabOffAir, Cmd.GET)
    dabservicelabel = StrFunction("DABSERVICELABEL", Cmd.GET)
    dabpreset = EnumOrIntFunction("DABPRESET", Preset)
    dabprgtype = StrFunction("DABPRGTYPE", Cmd.GET)

    def dabpreset_down(self):
        self._put("DABPRESET", "Down")

    def dabpreset_up(self):
        self._put("DABPRESET", "Up")

    fmpreset = EnumOrIntFunction("FMPRESET", Preset)

    def fmpreset_down(self):
        self._put("FMPRESET", "Down")  # type: ignore

    def fmpreset_up(self):
        self._put("FMPRESET", "Up")  # type: ignore

    fmrdsprgservice = StrFunction("FMRDSPRGSERVICE", Cmd.GET, init="FMRDSINFO")
    fmrdsprgtype = StrFunction("FMRDSPRGTYPE", Cmd.GET, init="FMRDSINFO")
    fmrdstxt = StrFunction("FMRDSTXT", Cmd.GET, init="FMRDSINFO")
    fmsigstereomono = EnumFunction[FmSigStereoMono](
        "FMSIGSTEREOMONO", FmSigStereoMono, Cmd.GET
    )
    fmtuned = EnumFunction[FmTuned]("FMTUNED", FmTuned, Cmd.GET)
