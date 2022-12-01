"""Misc constants"""
from enum import Enum

MIN_VOLUME = -80.5  # Minimum volume value for receivers


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
    FIVE_CH_STEREO = "5ch Stereo"
    SEVEN_CH_STEREO = "7ch Stereo"
    NINE_CH_STEREO = "9ch Stereo"
    SURROUND_DECODER = "Surround Decoder"
    ALL_CH_STEREO = "All-Ch Stereo"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value):
        return SoundPrg.UNKNOWN


class Mute(str, Enum):
    ON = "On"
    ATT_MINUS_20 = "Att -20 dB"
    ATT_MINUS_40 = "Att -40 dB"
    OFF = "Off"


class Subunit(str, Enum):
    """Known Subunits in YNCA"""

    SYS = "SYS"
    MAIN = "MAIN"
    ZONE2 = "ZONE2"
    ZONE3 = "ZONE3"
    ZONE4 = "ZONE4"
    AIRPLAY = "AIRPLAY"
    BT = "BT"
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


class Avail(str, Enum):
    NOT_CONNECTED = "Not Connected"
    NOT_READY = "Not Ready"
    READY = "Ready"


class InitVolLvl(str, Enum):
    MUTE = "Mute"


class InitVolMode(str, Enum):
    ON = "On"
    OFF = "Off"


class Input(Enum):
    # Inputs with connectors on the receiver
    AUDIO1 = "AUDIO1"
    AUDIO2 = "AUDIO2"
    AUDIO3 = "AUDIO3"
    AUDIO4 = "AUDIO4"
    AV1 = "AV1"
    AV2 = "AV2"
    AV3 = "AV3"
    AV4 = "AV4"
    AV5 = "AV5"
    AV6 = "AV6"
    AV7 = "AV7"
    DOCK = "DOCK"  # Selecting DOCK selects iPod for me, might depend on what dock is attached (I have no dock connected)
    HDMI1 = "HDMI1"
    HDMI2 = "HDMI2"
    HDMI3 = "HDMI3"
    HDMI4 = "HDMI4"
    HDMI5 = "HDMI5"
    HDMI6 = "HDMI6"
    HDMI7 = "HDMI7"
    MULTICH = "MULTI CH"
    PHONO = "PHONO"
    VAUX = "V-AUX"

    # Inputs provided by subunits
    AIRPLAY = "Airplay"
    BLUETOOTH = "Bluetooth"
    IPOD = "iPod"
    IPOD_USB = "iPod (USB)"
    NAPSTER = "Napster"
    NETRADIO = "NET RADIO"
    PANDORA = "Pandora"
    PC = "PC"
    RHAPSODY = "Rhapsody"
    SERVER = "SERVER"
    SIRIUS = "SIRIUS"
    SIRIUS_IR = "SIRIUS InternetRadio"
    SIRIUS_XM = "SiriusXM"
    SPOTIFY = "Spotify"
    TUNER = "TUNER"  # This can be different tuners like AM/FM, DAB/FM or HDRADIO
    UAW = "UAW"
    USB = "USB"

    UNKNOWN = "Unknown"
    """Not a real input, but used to map inputs not in the list so library does not break on new/unknown inputs"""

    @classmethod
    def _missing_(cls, value):
        return Input.UNKNOWN


class Party(Enum):
    ON = "On"
    OFF = "Off"


class PartyMute(Enum):
    ON = "On"
    OFF = "Off"


class PureDirMode(Enum):
    ON = "On"
    OFF = "Off"


class Pwr(Enum):
    ON = "On"
    STANDBY = "Standby"


class Shuffle(Enum):
    ON = "On"
    OFF = "Off"


class Straight(Enum):
    ON = "On"
    OFF = "Off"


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


class BandTun(str, Enum):
    AM = "AM"
    FM = "FM"


class TwoChDecoder(str, Enum):
    DolbyPl = "Dolby PL"
    DolbyPl2Movie = "Dolby PLII Movie"
    DolbyPl2Music = "Dolby PLII Music"
    DolbyPl2Game = "Dolby PLII Game"
    DolbyPl2xMovie = "Dolby PLIIx Movie"
    DolbyPl2xMusic = "Dolby PLIIx Music"
    DolbyPl2xGame = "Dolby PLIIx Game"
    DtsNeo6Cinema = "DTS NEO:6 Cinema"
    DtsNeo6Music = "DTS NEO:6 Music"
