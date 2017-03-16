from enum import Enum
from math import modf
from .connection import YncaConnection, YncaProtocolStatus



class YncaReceiver:
    _all_zones = ["MAIN", "ZONE2", "ZONE3", "ZONE4"]

    # Map subunits to input names, this is used for discovering what inputs are available
    # Inputs missing because unknown what subunit they map to: NET
    _subunit_input_mapping = {
        "TUN": "TUNER",
        "SIRIUS": "SIRIUS",
        "IPOD": "iPod",
        "BT": "Bluetooth",
        "RHAP": "Rhapsody",
        "SIRIUSIR": "SIRIUS InternetRadio",
        "PANDORA": "Pandora",
        "NAPSTER": "Napster",
        "PC": "PC",
        "NETRADIO": "NET RADIO",
        "IPODUSB": "iPod (USB)",
        "UAW": "UAW",
    }

    # Inputs that are only available on the main unit
    _main_only_inputs = ["HDMI1", "HDMI2", "HDMI3", "HDMI4", "HDMI5", "HDMI6", "HDMI7", "AV1", "AV2", "AV3", "AV4"]

    def __init__(self, port):
        self.modelname = None
        self.software_version = None
        self.zones = {}
        self.inputs = {}
        self._connection = YncaConnection(port, self._connection_update)
        self._connection.connect()

        self._initialize_device()

    def _initialize_device(self):
        """ Communicate with the device to setup initial state and discover capabilities """
        self._connection.get("SYS", "MODELNAME")
        self._connection.get("SYS", "VERSION")

        # Get userfriendly names for inputs (also allows detection of available inputs)
        # Note that these are not all inputs, just the external ones it seems
        self._connection.get("SYS", "INPNAME")

        # There is no way to get which zones are supported by the device to just try all possible
        # The callback will create any zone instances on success responses
        for zone in YncaReceiver._all_zones:
            self._connection.get(zone, "AVAIL")

        # A device also can have a number of 'internal' inputs like the Tuner, USB, Napster etc..
        # There is no way to get which of there inputs are supported by the device so just try all that we know of
        for subunit in YncaReceiver._subunit_input_mapping:
            self._connection.get(subunit, "AVAIL")

    def _connection_update(self, status, subunit, function, value):
        if status == YncaProtocolStatus.OK:
            if subunit == "SYS":
                self._update(function, value)
            elif subunit in YncaReceiver._all_zones:
                if subunit in self.zones:
                    self.zones[subunit].update(function, value)
                else:
                    self.zones[subunit] = YncaZone(subunit, self._connection)
            elif function == "AVAIL":
                if subunit in YncaReceiver._subunit_input_mapping:
                    self.inputs[YncaReceiver._subunit_input_mapping[subunit]] = YncaReceiver._subunit_input_mapping[subunit]

    def _update(self, function, value):
        if function == "MODELNAME":
            self.modelname = value
        elif function == "VERSION":
            self.software_version = value
        elif function.startswith("INPNAME"):
            input_id = function[7:]
            self.inputs[input_id] = value


def number_to_string_with_stepsize_zero_point_five(value, decimals, stepsize):

    steps = round(value / stepsize)
    stepped_value = steps * stepsize
    after_the_point, before_the_point = modf(stepped_value)

    after_the_point = abs(after_the_point * (10 ** decimals))

    return "{}.{}".format(int(before_the_point), int(after_the_point))


class Mute(Enum):
    on = 1
    att_minus_20 = 2
    att_minus_40 = 3
    off = 4

DspSoundPrograms = [
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


class YncaZone:
    def __init__(self, zone, connection):
        self.subunit = zone
        self._connection = connection

        self.name = None
        self._input = None
        self._power = False
        self._volume = None
        self.max_volume = 16.5
        self._mute = None
        self._dsp_sound_program = None
        self._scenes = {}

        self._handler_cache = {}

        self.get("BASIC")  # Gets PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER and SOUNDPRG (if applicable)
        self.get("MAXVOL")
        self.get("ZONENAME")
        self.get("SCENENAME")

    def __str__(self):
        output = []
        for key in self.__dict__:
            output.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return '\n'.join(output)

    def put(self, function, value):
        self._connection.put(self.subunit, function, value)

    def get(self, function):
        self._connection.get(self.subunit, function)

    def update(self, function, value):
        if function not in self._handler_cache:
            self._handler_cache[function] = getattr(self, "_handle_{}".format(function.lower()), None)

        handler = self._handler_cache[function]
        if handler is not None:
            handler(value)
        else:
            if function.startswith("SCENE") and function.endswith("NAME"):
                scene_id = int(function[5:6])
                self._scenes[scene_id] = value

    def _handle_inp(self, value):
        self._input = value

    def _handle_vol(self, value):
        self._volume = float(value)

    def _handle_maxvol(self, value):
        self.max_volume = float(value)

    def _handle_mute(self, value):
        if value == "Off":
            self._mute = Mute.off
        elif value == "Att -20dB":
            self._mute = Mute.att_minus_20
        elif value == "Att -40dB":
            self._mute = Mute.att_minus_40
        else:
            self._mute = Mute.on

    def _handle_pwr(self, value):
        if value == "On":
            self._power = True
        else:
            self._power = False

    def _handle_zonename(self, value):
        self.name = value

    def _handle_soundprg(self, value):
        self._dsp_sound_program = value

    @property
    def on(self):
        return self._power

    @on.setter
    def on(self, value):
        assert value in [True, False]  # Is this usefull?
        self.put("PWR", "On" if value is True else "Standby")

    @property
    def muted(self):
        return self._mute

    @muted.setter
    def muted(self, value):
        command_value = "On"
        if value == Mute.off:
            command_value = "Off"
        elif value == Mute.att_minus_40:
            command_value = "Att -40 dB"
        elif value == Mute.att_minus_20:
            command_value = "Att -20 dB"
        self.put("MUTE", command_value)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        print("VOL={}".format(number_to_string_with_stepsize_zero_point_five(value, 1, 0.5)))
        self.put("VOL", number_to_string_with_stepsize_zero_point_five(value, 1, 0.5))

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        self.put("INP", value)

    @property
    def dsp_sound_program(self):
        return self._dsp_sound_program

    @dsp_sound_program.setter
    def dsp_sound_program(self, value):
        if value in DspSoundPrograms:
            self.put("SOUNDPRG", value)
        else:
            raise ValueError("Soundprogram not in DspSoundPrograms")

    @property
    def scene(self):
        pass  # Not possible to get current scene

    @scene.setter
    def scene(self, value):
        if len(self._scenes) == 0:
            raise ValueError("Zone does not support scenes")
        elif value not in [1, 2 , 3, 4]:
            raise ValueError("Invalid value")
        else:
            self.put("SCENE=Scene {}", value)
