"""Misc constants"""
from enum import Enum


class SoundPrg(str, Enum):
    HALL_IN_MUNICH = "Hall in Munich"
    HALL_IN_VIENNA = "Hall in Vienna"
    HALL_IN_AMSTERDAM = "Hall in Amsterdam"
    CHURCH_IN_FREIBURG = "Church in Freiburg"
    CHURCH_IN_ROYAUMONT = "Church in Royaumont"
    CHAMBER = "Chamber"
    VILLAGE_VANGUARD = "Village Vanguard"
    WAREHOUSE_LOFT = "Warehouse Loft"
    CELLAR_CLUB = "Cellar Club"
    THE_ROXY_THEATRE = "The Roxy Theatre"
    THE_BOTTOM_LINE = "The Bottom Line"
    SPORTS = "Sports"
    ACTION_GAME = "Action Game"
    ROLEPLAYING_GAME = "Roleplaying Game"
    MUSIC_VIDEO = "Music Video"
    RECITAL_OPERA = "Recital/Opera"
    STANDARD = "Standard"
    SPECTACLE = "Spectacle"
    SCI_FI = "Sci-Fi"
    ADVENTURE = "Adventure"
    DRAMA = "Drama"
    MONO_MOVIE = "Mono Movie"
    TWO_CH_STEREO = "2ch Stereo"
    SEVEN_CH_STEREO = "7ch Stereo"
    NINE_CH_STEREO = "9ch Stereo"
    SURROUND_DECODER = "Surround Decoder"
    ALL_CH_STEREO = "All-Ch Stereo"  # Available on TSR-700


class Mute(str, Enum):
    on = "On"
    att_minus_20 = "Att -20 dB"
    att_minus_40 = "Att -40 dB"
    off = "Off"


class Subunit(str, Enum):
    """Known Subunits in YNCA"""

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
    USB = "USB"
    IPODUSB = "IPODUSB"
    UAW = "UAW"
    # These are from a log found on the internet
    # http://www.remotecentral.com/cgi-bin/mboard/rs232-ip/thread.cgi?694
    SIRIUSXM = "SIRIUSXM"
    SPOTIFY = "SPOTIFY"
    SERVER = "SERVER"
    AIRPLAY = "AIRPLAY"


class Avail(str, Enum):
    NOT_CONNECTED = "Not Connected"
    NOT_READY = "Not Ready"
    READY = "Ready"


class Repeat(str, Enum):
    OFF = "Off"
    SINGLE = "Single"
    ALL = "All"


class PlaybackInfo(str, Enum):
    STOP = "Stop"
    PAUSE = "Pause"
    PLAY = "Play"


class Playback(str, Enum):
    STOP = "Stop"
    PAUSE = "Pause"
    PLAY = "Play"
    SKIP_REV = "Skip Rev"
    SKIP_FWD = "Skip Fwd"


class Band(str, Enum):
    AM = "AM"
    FM = "FM"
