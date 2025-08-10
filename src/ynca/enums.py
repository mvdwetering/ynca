"""Enums used for mapping YNCA values."""

from enum import StrEnum, unique
import logging
from typing import Self

logger = logging.getLogger(__name__)

UNKNOWN_STRING = "< UNKNOWN >"


@unique
class AdaptiveDrc(StrEnum):
    OFF = "Off"
    AUTO = "Auto"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Avail(StrEnum):
    NOT_CONNECTED = "Not Connected"
    NOT_READY = "Not Ready"
    READY = "Ready"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class BandDab(StrEnum):
    DAB = "DAB"
    FM = "FM"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class BandTun(StrEnum):
    AM = "AM"
    FM = "FM"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class DabPreset(StrEnum):
    NO_PRESET = "No Preset"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class DirMode(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Enhancer(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class FmPreset(StrEnum):
    NO_PRESET = "No Preset"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class HdmiOut(StrEnum):
    OFF = "Off"
    OUT = (
        "OUT"  # OUT is on receivers with 1 HDMI, multiple HDMI outputs use OUT1 + OUT 2
    )
    OUT1 = "OUT1"
    OUT2 = "OUT2"
    OUT1_PLUS_2 = "OUT1 + 2"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class HdmiOutOnOff(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class InitVolLvl(StrEnum):
    MUTE = "Mute"
    OFF = "Off"
    """Only some receivers report Off, most seem to use InitVolMode to indicate On/Off"""

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class InitVolMode(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Input(StrEnum):
    # Inputs with connectors on the receiver
    AUDIO = "AUDIO"  # This input is kind of weird since it is not reported by INPNAME=?
    AUDIO1 = "AUDIO1"
    AUDIO2 = "AUDIO2"
    AUDIO3 = "AUDIO3"
    AUDIO4 = "AUDIO4"
    AUDIO5 = "AUDIO5"
    AV1 = "AV1"
    AV2 = "AV2"
    AV3 = "AV3"
    AV4 = "AV4"
    AV5 = "AV5"
    AV6 = "AV6"
    AV7 = "AV7"
    DOCK = "DOCK"  # Selecting DOCK selects iPod for me, might depend on what dock is attached (I have no dock to test)
    HDMI1 = "HDMI1"
    HDMI2 = "HDMI2"
    HDMI3 = "HDMI3"
    HDMI4 = "HDMI4"
    HDMI5 = "HDMI5"
    HDMI6 = "HDMI6"
    HDMI7 = "HDMI7"
    MULTICH = "MULTI CH"
    OPTICAL1 = "OPTICAL1"
    OPTICAL2 = "OPTICAL2"
    PHONO = "PHONO"
    TV = "TV"
    VAUX = "V-AUX"

    # Inputs provided by subunits
    AIRPLAY = "AirPlay"
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
    TUNER = "TUNER"  # AM/FM tuner (@TUN) or DAB/FM tuner (@DAB)
    UAW = "UAW"
    USB = "USB"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Mute(StrEnum):
    ON = "On"
    ATT_MINUS_20 = "Att -20 dB"
    ATT_MINUS_40 = "Att -40 dB"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Party(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class PartyMute(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Playback(StrEnum):
    STOP = "Stop"
    PAUSE = "Pause"
    PLAY = "Play"
    SKIP_REV = "Skip Rev"
    SKIP_FWD = "Skip Fwd"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class PlaybackInfo(StrEnum):
    STOP = "Stop"
    PAUSE = "Pause"
    PLAY = "Play"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class PureDirMode(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Pwr(StrEnum):
    ON = "On"
    STANDBY = "Standby"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class PwrB(StrEnum):
    ON = "On"
    STANDBY = "Standby"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Repeat(StrEnum):
    OFF = "Off"
    SINGLE = "Single"
    ALL = "All"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Shuffle(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Sleep(StrEnum):
    OFF = "Off"
    THIRTY_MIN = "30 min"
    SIXTY_MIN = "60 min"
    NINETY_MIN = "90 min"
    ONEHUNDREDTWENTY_MIN = "120 min"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class SoundPrg(StrEnum):
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
    ELEVEN_CH_STEREO = "11ch Stereo"
    SURROUND_DECODER = "Surround Decoder"
    ALL_CH_STEREO = "All-Ch Stereo"
    ENHANCED = "Enhanced"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class SpeakerA(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class SpeakerB(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class SpPattern(StrEnum):
    PATTERN_1 = "Pattern 1"
    PATTERN_2 = "Pattern 2"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class Straight(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class SurroundAI(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class ThreeDeeCinema(StrEnum):
    OFF = "Off"
    AUTO = "Auto"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class TwoChDecoder(StrEnum):
    # Older models support Dolby Prologic and DTS:Neo settings
    DolbyPl = "Dolby PL"
    DolbyPl2Movie = "Dolby PLII Movie"
    DolbyPl2Music = "Dolby PLII Music"
    DolbyPl2Game = "Dolby PLII Game"
    DolbyPl2xMovie = "Dolby PLIIx Movie"
    DolbyPl2xMusic = "Dolby PLIIx Music"
    DolbyPl2xGame = "Dolby PLIIx Game"
    DtsNeo6Cinema = "DTS NEO:6 Cinema"
    DtsNeo6Music = "DTS NEO:6 Music"

    # Newer models seem to have different values
    # These have been seen (Note that RX-A3070 also supports the DTS NEO presets)
    Auto = "Auto"  # Seen on RX-A3070
    DolbySurround = "Dolby Surround"  # Seen on RX-A3070
    DtsNeuralX = "DTS Neural:X"  # Seen on RX-A1060 and RX-A3070
    Auro3d = "AURO-3D"  # Seen on RX-A6A

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class ZoneBAvail(StrEnum):
    NOT_CONNECTED = "Not Connected"
    NOT_READY = "Not Ready"
    READY = "Ready"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""


@unique
class ZoneBMute(StrEnum):
    ON = "On"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""
