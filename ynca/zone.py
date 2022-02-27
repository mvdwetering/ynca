import threading
import logging

from typing import Callable, Dict, Set


from .connection import YncaConnection, YncaProtocolStatus
from .constants import DSP_SOUND_PROGRAMS, Mute
from .helpers import number_to_string_with_stepsize
from .errors import YncaInitializationFailedException
from .subunit import Subunit

logger = logging.getLogger(__name__)


class YncaZone(Subunit):
    def __init__(
        self,
        subunit_id: str,
        connection: YncaConnection,
        inputs: Dict[str, str],
    ):
        super().__init__(subunit_id, connection)
        self._inputs = inputs
        self._initialized = False

        self._initialized_event = threading.Event()
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._name = None
        self._max_volume = 16.5  # is 16.5 for zones where it is not configurable
        self._input = None
        self._power = None
        self._volume = None
        self._mute = None
        self._dsp_sound_program = None
        self._straight = None
        self._scenes: Dict[str, str] = {}

        self._initialized_event.clear()

    def initialize(self):
        """
        Initialize the Zone based on capabilities of the device.
        This is a long running function!
        """
        self._initialized = False

        # BASIC gets PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER and SOUNDPRG (if applicable)
        self._get("BASIC")
        self._get("MAXVOL")
        self._get("SCENENAME")
        self._get("ZONENAME")

        # Receiving Zonename during initialization will set the event
        if self._initialized_event.wait(
            2
        ):  # Each command takes at least 100ms + big margin
            self._initialized = True
        else:
            raise YncaInitializationFailedException(
                f"Zone {self._subunit_id} initialization failed"
            )

        self._call_registered_update_callbacks()

    def __str__(self):
        output = []
        for key in self.__dict__:
            output.append("{key}={value}".format(key=key, value=self.__dict__[key]))

        return "\n".join(output)

    def _unhandled_subunit_message_received(
        self, status: YncaProtocolStatus, function_: str, value: str
    ) -> bool:
        updated = True

        if (
            len(function_) == 10
            and function_.startswith("SCENE")
            and function_.endswith("NAME")
        ):
            scene_id = function_[5:6]
            self._scenes[scene_id] = value
        else:
            updated = False

        return updated

    def _handle_inp(self, value: str):
        self._input = value

    def _handle_vol(self, value: str):
        self._volume = float(value)

    def _handle_maxvol(self, value: str):
        self._max_volume = float(value)

    def _handle_mute(self, value: str):
        if value == "Off":
            self._mute = Mute.off
        elif value == "Att -20 dB":
            self._mute = Mute.att_minus_20
        elif value == "Att -40 dB":
            self._mute = Mute.att_minus_40
        else:
            self._mute = Mute.on

    def _handle_pwr(self, value: str):
        self._power = value == "On"

    def _handle_zonename(self, value: str):
        self._name = value

        # During initialization this is used to signal
        # that initialization is done
        if not self._initialized:
            self._initialized_event.set()

    def _handle_soundprg(self, value: str):
        self._dsp_sound_program = value

    def _handle_straight(self, value: str):
        self._straight = value == "On"

    @property
    def name(self):
        """Get zone name"""
        return self._name

    @property
    def on(self):
        """Get current on state"""
        return self._power

    @on.setter
    def on(self, value: bool):
        """Turn on/off zone"""
        self._put("PWR", "On" if value is True else "Standby")

    @property
    def mute(self):
        """Get current mute state"""
        return self._mute

    @mute.setter
    def mute(self, value: Mute):
        """Mute"""
        assert value in Mute  # Is this usefull?
        command_value = "On"
        if value == Mute.off:
            command_value = "Off"
        elif value == Mute.att_minus_40:
            command_value = "Att -40 dB"
        elif value == Mute.att_minus_20:
            command_value = "Att -20 dB"
        self._put("MUTE", command_value)

    @property
    def max_volume(self):
        """Get maximum volume in dB"""
        return self._max_volume

    @property
    def min_volume(self):
        """Get minimum volume in dB"""
        return -80.5  # Seems to be fixed and the same for all zones

    @property
    def volume(self):
        """Get current volume in dB"""
        return self._volume

    @volume.setter
    def volume(self, value: float):
        """Set volume in dB. The receiver only works with 0.5 increments. Input values will be rounded to nearest 0.5 step."""
        if self.min_volume <= value <= self._max_volume:
            self._put("VOL", number_to_string_with_stepsize(value, 1, 0.5))
        else:
            raise ValueError(
                "Volume out of range, must be between min_volume and max_volume"
            )

    def volume_up(self, step_size: float = 0.5):
        """
        Increase the volume with given stepsize.
        Supported stepsizes are: 0.5, 1, 2 and 5
        """
        value = "Up"
        if step_size in [1, 2, 5]:
            value = "Up {} dB".format(step_size)
        self._put("VOL", value)

    def volume_down(self, step_size: float = 0.5):
        """
        Decrease the volume with given stepsize.
        Supported stepsizes are: 0.5, 1, 2 and 5
        """
        value = "Down"
        if step_size in [1, 2, 5]:
            value = "Down {} dB".format(step_size)
        self._put("VOL", value)

    @property
    def input(self):
        """Get current input"""
        return self._input

    @input.setter
    def input(self, value: str):
        """Set input"""
        self._put("INP", value)

    @property
    def inputs(self):
        """Get full list of inputs, some may not be applicable to this zone."""
        # TODO filter inputs based on availability in this zone.
        return self._inputs

    @property
    def dsp_sound_program(self):
        """Get the current DSP sound program"""
        return self._dsp_sound_program

    @dsp_sound_program.setter
    def dsp_sound_program(self, value: str):
        """Set the DSP sound program"""
        if value in DSP_SOUND_PROGRAMS:
            self._put("SOUNDPRG", value)
        else:
            raise ValueError("Soundprogram not in DspSoundPrograms")

    @property
    def straight(self):
        """Get the current Straight value"""
        return self._straight

    @straight.setter
    def straight(self, value: bool):
        """Set the Straight value"""
        self._put("STRAIGHT", "On" if value is True else "Off")

    @property
    def scenes(self):
        """Get the dictionary with scenes where key, value = id, name"""
        return self._scenes

    def activate_scene(self, scene_id: str):
        """Activate a scene"""
        if len(self._scenes) == 0:
            raise ValueError("Zone does not support scenes")
        elif scene_id not in self._scenes.keys():
            raise ValueError("Invalid scene ID")
        else:
            self._put("SCENE", f"Scene {scene_id}")
