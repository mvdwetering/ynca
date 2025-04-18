import logging

# Import intended API so it is easily accessible through `from  ynca import Something`
from .api import YncaApi, YncaConnectionCheckResult
from .connection import YncaConnection, YncaProtocolStatus
from .enums import (
    AdaptiveDrc,
    Avail,
    BandDab,
    BandTun,
    DabPreset,
    DirMode,
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
    PwrB,
    Repeat,
    Shuffle,
    Sleep,
    SoundPrg,
    SpeakerA,
    SpeakerB,
    SpPattern,
    Straight,
    SurroundAI,
    ThreeDeeCinema,
    TwoChDecoder,
    ZoneBAvail,
    ZoneBMute,
)
from .errors import (
    YncaConnectionError,
    YncaConnectionFailed,
    YncaException,
    YncaInitializationFailedException,
)
from .modelinfo import YncaModelInfo

__all__ = [
    "AdaptiveDrc",
    "Avail",
    "BandDab",
    "BandTun",
    "DabPreset",
    "DirMode",
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
    "PwrB",
    "Repeat",
    "Shuffle",
    "Sleep",
    "SoundPrg",
    "SpPattern",
    "SpeakerA",
    "SpeakerB",
    "Straight",
    "SurroundAI",
    "ThreeDeeCinema",
    "TwoChDecoder",
    "YncaApi",
    "YncaConnection",
    "YncaConnectionCheckResult",
    "YncaConnectionError",
    "YncaConnectionFailed",
    "YncaException",
    "YncaInitializationFailedException",
    "YncaModelInfo",
    "YncaProtocolStatus",
    "ZoneBAvail",
    "ZoneBMute",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
