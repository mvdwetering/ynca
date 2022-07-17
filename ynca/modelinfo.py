"""This file contains info that is specific per model"""

from dataclasses import dataclass
from typing import List, Optional

from .constants import SoundPrg


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
    SoundPrg.SEVEN_CH_STEREO,
    SoundPrg.SURROUND_DECODER,
]

ExtendedSoundPrgListSevenChannel: List[SoundPrg] = list(BasicSoundPrgList)
ExtendedSoundPrgListSevenChannel.extend(
    [
        SoundPrg.HALL_IN_AMSTERDAM,
        SoundPrg.CHURCH_IN_FREIBURG,
        SoundPrg.CHURCH_IN_ROYAUMONT,
        SoundPrg.VILLAGE_VANGUARD,
        SoundPrg.WAREHOUSE_LOFT,
        SoundPrg.RECITAL_OPERA,
    ]
)

ExtendedSoundPrgListNineChannel: List[SoundPrg] = list(
    ExtendedSoundPrgListSevenChannel
)
ExtendedSoundPrgListNineChannel.remove(SoundPrg.SEVEN_CH_STEREO)
ExtendedSoundPrgListNineChannel.append(SoundPrg.NINE_CH_STEREO)


MODELINFO = {
    "HTR-7065": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-V671": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-V673": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-V773": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A700": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A710": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A720": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A800": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A810": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A820": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A1000": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A1010": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A1020": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-A2000": ModelInfo(soundprg=ExtendedSoundPrgListSevenChannel),
    "RX-A2010": ModelInfo(soundprg=ExtendedSoundPrgListNineChannel),
    "RX-A2020": ModelInfo(soundprg=ExtendedSoundPrgListNineChannel),
    "RX-A3000": ModelInfo(soundprg=ExtendedSoundPrgListSevenChannel),
    "RX-A3010": ModelInfo(soundprg=ExtendedSoundPrgListNineChannel),
    "RX-A3020": ModelInfo(soundprg=ExtendedSoundPrgListNineChannel),
    "RX-V867": ModelInfo(soundprg=BasicSoundPrgList),
    "RX-V871": ModelInfo(soundprg=BasicSoundPrgList),
}


def get_modelinfo(modelname: str) -> Optional[ModelInfo]:
    return MODELINFO.get(modelname, None)
