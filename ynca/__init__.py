import logging
from .receiver import YncaReceiver
from .connection import ynca_console
from .constants import DSP_SOUND_PROGRAMS, Mute

logging.getLogger(__name__).addHandler(logging.NullHandler())

