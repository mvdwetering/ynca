import logging

# Import intended API so it is easily accessible through `from  ynca import Something`

from .api import YncaApi, YncaConnectionCheckResult
from .connection import YncaConnection, YncaProtocolStatus
from .errors import (
    YncaConnectionError,
    YncaConnectionFailed,
    YncaException,
    YncaInitializationFailedException,
)
from .enums import (
    Avail,
    AdaptiveDrc,
    BandDab,
    BandTun,
    DabPreset,
    Enhancer,
    FmPreset,
    HdmiOut,
    HdmiOutOnOff,
    InitVolLvl,
    InitVolMode,
    Input,
    Mute,
    Party,
    PartyMute,
    Playback,
    PlaybackInfo,
    PureDirMode,
    Pwr,
    Repeat,
    Shuffle,
    Sleep,
    SoundPrg,
    Straight,
    ThreeDeeCinema,
    TwoChDecoder,
)
from .modelinfo import YncaModelInfo

__all__ = [
    "YncaApi",
    "YncaConnectionCheckResult",
    "YncaConnection",
    "YncaProtocolStatus",
    "YncaException",
    "YncaConnectionError",
    "YncaConnectionFailed",
    "YncaInitializationFailedException",
    "YncaModelInfo",
    "Avail",
    "AdaptiveDrc",
    "BandDab",
    "BandTun",
    "DabPreset",
    "Enhancer",
    "FmPreset",
    "HdmiOut",
    "HdmiOutOnOff",
    "InitVolLvl",
    "InitVolMode",
    "Input",
    "Mute",
    "Party",
    "PartyMute",
    "Playback",
    "PlaybackInfo",
    "PureDirMode",
    "Pwr",
    "Repeat",
    "Shuffle",
    "Sleep",
    "SoundPrg",
    "Straight",
    "ThreeDeeCinema",
    "TwoChDecoder",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
