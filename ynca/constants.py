"""Misc constants"""
import logging
from enum import Enum, unique

logger = logging.getLogger(__name__)

MIN_VOLUME = -80.5  # Minimum volume value for receivers

@unique
class Subunit(str, Enum):
    """Known Subunits in YNCA"""

    SYS = "SYS"
    MAIN = "MAIN"
    ZONE2 = "ZONE2"
    ZONE3 = "ZONE3"
    ZONE4 = "ZONE4"
    AIRPLAY = "AIRPLAY"
    BT = "BT"
    DAB = "DAB"
    IPOD = "IPOD"
    IPODUSB = "IPODUSB"
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
    TUN = "TUN"
    UAW = "UAW"
    USB = "USB"

    def __format__(self, spec) -> str:
        return self.value
