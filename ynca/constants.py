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
    "Surround Decoder"]


class Mute(Enum):
    on = 1
    att_minus_20 = 2
    att_minus_40 = 3
    off = 4

