import logging

# Import intended API so it is easily accessible through `from ynca import Something`
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
    ExBass,
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
from .subunit import SubunitBase
from .subunits.airplay import Airplay
from .subunits.bt import Bt
from .subunits.dab import Dab
from .subunits.deezer import Deezer
from .subunits.ipod import Ipod
from .subunits.ipodusb import IpodUsb
from .subunits.mclink import McLink
from .subunits.napster import Napster
from .subunits.netradio import NetRadio
from .subunits.pandora import Pandora
from .subunits.pc import Pc
from .subunits.rhap import Rhap
from .subunits.server import Server
from .subunits.sirius import Sirius, SiriusIr, SiriusXm
from .subunits.spotify import Spotify
from .subunits.system import System
from .subunits.tidal import Tidal
from .subunits.tun import Tun
from .subunits.uaw import Uaw
from .subunits.usb import Usb
from .subunits.zone import Main, Zone2, Zone3, Zone4, ZoneBase

__all__ = [
    "AdaptiveDrc",
    "Airplay",
    "Avail",
    "BandDab",
    "BandTun",
    "Bt",
    "Dab",
    "DabPreset",
    "Deezer",
    "DirMode",
    "Enhancer",
    "ExBass",
    "FmPreset",
    "HdmiOut",
    "HdmiOutOnOff",
    "InitVolLvl",
    "InitVolMode",
    "Input",
    "Ipod",
    "IpodUsb",
    "Main",
    "McLink",
    "Mute",
    "Napster",
    "NetRadio",
    "Pandora",
    "Party",
    "PartyMute",
    "Pc",
    "Playback",
    "PlaybackInfo",
    "PureDirMode",
    "Pwr",
    "PwrB",
    "Repeat",
    "Rhap",
    "Server",
    "Shuffle",
    "Sirius",
    "SiriusIr",
    "SiriusXm",
    "Sleep",
    "SoundPrg",
    "SpPattern",
    "SpeakerA",
    "SpeakerB",
    "Spotify",
    "Straight",
    "SubunitBase",
    "SurroundAI",
    "System",
    "ThreeDeeCinema",
    "Tidal",
    "Tun",
    "TwoChDecoder",
    "Uaw",
    "Usb",
    "YncaApi",
    "YncaConnection",
    "YncaConnectionCheckResult",
    "YncaConnectionError",
    "YncaConnectionFailed",
    "YncaException",
    "YncaInitializationFailedException",
    "YncaModelInfo",
    "YncaProtocolStatus",
    "Zone2",
    "Zone3",
    "Zone4",
    "ZoneBAvail",
    "ZoneBMute",
    "ZoneBase",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
