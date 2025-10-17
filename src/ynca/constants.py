"""Misc constants."""

from enum import StrEnum, unique
import logging

logger = logging.getLogger(__name__)

MIN_VOLUME = -80.5  # Minimum volume value for receivers
MAX_VOLUME = 16.5  # Maximum volume value for receivers


@unique
class Subunit(StrEnum):
    """Known Subunits in YNCA."""

    SYS = "SYS"
    MAIN = "MAIN"
    ZONE2 = "ZONE2"
    ZONE3 = "ZONE3"
    ZONE4 = "ZONE4"
    AIRPLAY = "AIRPLAY"
    BT = "BT"
    DAB = "DAB"
    DEEZER = "DEEZER"
    IPOD = "IPOD"
    IPODUSB = "IPODUSB"
    MCLINK = "MCLINK"
    NAPSTER = "NAPSTER"
    NETRADIO = "NETRADIO"
    PANDORA = "PANDORA"
    PC = "PC"
    RHAP = "RHAP"
    SIRIUS = "SIRIUS"
    SIRIUSIR = "SIRIUSIR"
    SIRIUSXM = "SIRIUSXM"
    SERVER = "SERVER"
    SPOTIFY = "SPOTIFY"
    TIDAL = "TIDAL"
    TUN = "TUN"
    UAW = "UAW"
    USB = "USB"
