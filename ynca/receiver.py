import sys

import time
from enum import Enum
from math import modf

from .connection import YncaConnection, YncaProtocol


class YncaReceiver:
    _all_zones = ["MAIN", "ZONE2", "ZONE3", "ZONE4"]

    # Map subunits to input names, this is used for discovering what inputs are available
    # This list currently contains only what my receiver supports, I cannot guess the others
    _subunit_input_mapping = {
        "TUN": "Tuner",
        "NAPSTER": "Napster",
        "PC": "PC",
        "NETRADIO": "NET RADIO",
        "USB": "USB",
    }

    def __init__(self, port=None):
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

        # There is no way to get which zones are supported by the device to just try all possible
        # The callback will create any zone instances on success responses
        for zone in YncaReceiver._all_zones:
            self._connection.get(zone, "ZONENAME")

        # Get userfriendly names for inputs (also allows detection of available inputs)
        # Note that these are not all inputs, just the external ones
        self._connection.get("SYS", "INPNAME")

        # A device also can have a number of 'internal' inputs like the Tuner, USB, Napster etc..
        # There is no way to get which of there inputs are supported by the device so just try all that we know of
        for input in YncaReceiver._subunit_input_mapping:
            self._connection.get(input, "AVAIL")

    def _connection_update(self, status, subunit, function, value):
        print(status, subunit, function, value)
        if status == YncaProtocol.STATUS_OK:
            if subunit == "SYS":
                self._update(function, value)
            elif subunit in YncaReceiver._all_zones:
                if subunit in self.zones:
                    self.zones[subunit].update(function, value)
                else:
                    self.zones[subunit] = YncaZone(subunit, self._connection)
            elif function == "AVAIL":
                # subunit in YncaReceiver._all_inputs
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

class YncaZone:
    def __init__(self, zone, connection):
        self.id = zone
        self._connection = connection

        self.name = None
        self.input = None
        self._power = False
        self._volume = None
        self.max_volume = 0
        self._mute = None
        self._handler_cache = {}

        self.get("BASIC")  # Gets PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER and SOUNDPROG (if applicable)
        self.get("MAXVOL")
        self.get("ZONENAME")

    def put(self, function, value):
        self._connection.put(self.id, function, value)

    def get(self, function):
        self._connection.get(self.id, function)

    def update(self, function, value):
        if function not in self._handler_cache:
            self._handler_cache[function] = getattr(self, "_handle_{}".format(function.lower()), None)

        handler = self._handler_cache[function]
        if handler is not None:
            handler(value)

    def _handle_inp(self, value):
        self.input = value

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
