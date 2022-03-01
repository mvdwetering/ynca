"""Misc constants"""
from enum import Enum

DSP_SOUND_PROGRAMS = [
    "Hall in Munich",
    "Hall in Vienna",
    "Chamber",
    "Cellar Club",
    "The Roxy Theatre",
    "The Bottom Line",
    "Sports",
    "Action Game",
    "Roleplaying Game",
    "Music Video",
    "Standard",
    "Spectacle",
    "Sci-Fi",
    "Adventure",
    "Drama",
    "Mono Movie",
    "2ch Stereo",
    "7ch Stereo",
    "Surround Decoder",
]


class Mute(Enum):
    on = 1
    att_minus_20 = 2
    att_minus_40 = 3
    off = 4


"""Known Subunits in YNCA"""


class Subunit(str, Enum):
    SYS = "SYS"
    MAIN = "MAIN"
    ZONE2 = "ZONE2"
    ZONE3 = "ZONE3"
    ZONE4 = "ZONE4"
    TUN = "TUN"
    SIRIUS = "SIRIUS"
    IPOD = "IPOD"
    BT = "BT"
    RHAP = "RHAP"
    SIRIUSIR = "SIRIUSIR"
    PANDORA = "PANDORA"
    NAPSTER = "NAPSTER"
    PC = "PC"
    NETRADIO = "NETRADIO"
    IPODUSB = "IPODUSB"
    UAW = "UAW"


"""Subunits that are zones """
ZONES = [Subunit.MAIN, Subunit.ZONE2, Subunit.ZONE3, Subunit.ZONE4]
