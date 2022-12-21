"""This file contains info that is specific per model"""

from dataclasses import dataclass
from typing import List, Optional

from .enums import SoundPrg


@dataclass
class ModelInfo:
    soundprg: List[SoundPrg]


BasicSoundPrgList: List[SoundPrg] = [
    SoundPrg.HALL_IN_MUNICH,
    SoundPrg.HALL_IN_VIENNA,
    SoundPrg.CHAMBER,
    SoundPrg.CELLAR_CLUB,
    SoundPrg.THE_ROXY_THEATRE,
    SoundPrg.THE_BOTTOM_LINE,
    SoundPrg.SPORTS,
    SoundPrg.ACTION_GAME,
    SoundPrg.ROLEPLAYING_GAME,
    SoundPrg.MUSIC_VIDEO,
    SoundPrg.STANDARD,
    SoundPrg.SPECTACLE,
    SoundPrg.SCI_FI,
    SoundPrg.ADVENTURE,
    SoundPrg.DRAMA,
    SoundPrg.MONO_MOVIE,
    SoundPrg.TWO_CH_STEREO,
    SoundPrg.SURROUND_DECODER,
]

ExtendedSoundPrgList: List[SoundPrg] = list(BasicSoundPrgList)
ExtendedSoundPrgList.extend(
    [
        SoundPrg.HALL_IN_AMSTERDAM,
        SoundPrg.CHURCH_IN_FREIBURG,
        SoundPrg.CHURCH_IN_ROYAUMONT,
        SoundPrg.VILLAGE_VANGUARD,
        SoundPrg.WAREHOUSE_LOFT,
        SoundPrg.RECITAL_OPERA,
    ]
)


BasicSoundPrgFiveChannel: List[SoundPrg] = list(BasicSoundPrgList)
BasicSoundPrgFiveChannel.append(SoundPrg.FIVE_CH_STEREO)

BasicSoundPrgSevenChannel: List[SoundPrg] = list(BasicSoundPrgList)
BasicSoundPrgSevenChannel.append(SoundPrg.SEVEN_CH_STEREO)

ExtendedSoundPrgSevenChannel: List[SoundPrg] = list(ExtendedSoundPrgList)
ExtendedSoundPrgSevenChannel.append(SoundPrg.SEVEN_CH_STEREO)

ExtendedSoundPrgNineChannel: List[SoundPrg] = list(ExtendedSoundPrgList)
ExtendedSoundPrgNineChannel.append(SoundPrg.NINE_CH_STEREO)

ExtendedSoundPrgAllChannel: List[SoundPrg] = list(ExtendedSoundPrgList)
ExtendedSoundPrgAllChannel.append(SoundPrg.ALL_CH_STEREO)
ExtendedSoundPrgAllChannel.append(SoundPrg.ENHANCED)


MODELINFO = {
    "HTR-7065": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A6A": ModelInfo(soundprg=ExtendedSoundPrgAllChannel),
    "RX-A700": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A710": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A720": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A800": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A810": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A820": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A1000": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A1010": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A1020": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-A2000": ModelInfo(soundprg=ExtendedSoundPrgSevenChannel),
    "RX-A2010": ModelInfo(soundprg=ExtendedSoundPrgNineChannel),
    "RX-A2020": ModelInfo(soundprg=ExtendedSoundPrgNineChannel),
    "RX-A3000": ModelInfo(soundprg=ExtendedSoundPrgSevenChannel),
    "RX-A3010": ModelInfo(soundprg=ExtendedSoundPrgNineChannel),
    "RX-A3020": ModelInfo(soundprg=ExtendedSoundPrgNineChannel),
    "RX-V475": ModelInfo(soundprg=BasicSoundPrgFiveChannel),
    "RX-V671": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-V673": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-V773": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-V867": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
    "RX-V871": ModelInfo(soundprg=BasicSoundPrgSevenChannel),
}


class YncaModelInfo:
    @staticmethod
    def get(modelname: str) -> Optional[ModelInfo]:
        return MODELINFO.get(modelname, None)
