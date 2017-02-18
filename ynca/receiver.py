import sys

import time

from connection import YncaConnection, YncaProtocol


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
        self.powered = False
        self.zones = {}
        self.inputs = {}
        self._connection = YncaConnection(port, self._update)
        self._connection.connect()

        self._initialize_device()

    def _initialize_device(self):
        """ Communicate with the device to setup initial state and discover capabilities """
        self._connection.get("SYS", "MODELNAME")
        self._connection.get("SYS", "VERSION")
        self._connection.get("SYS", "PWR")

        # There is no way to get which zones are supported by the device to just try all possible
        # The callback will create any zone instances on success responses
        for zone in YncaReceiver._all_zones:
            self._connection.get(zone, "ZONENAME")

        # Get userfriendly names for inputs (also allows detection of available inputs)
        # Note that these are not all inputs, just the external ones
        self._connection.get("SYS", "INPNAME")

        # A device also can have a number of 'internal' inputs like the Tuner, USB, NAPSTER etc..
        # There is no way to get which of there inputs are supported by the device to just try all that we know of
        for input in YncaReceiver._subunit_input_mapping:
            self._connection.get(input, "AVAIL")

    def _update(self, status, subunit, function, value):
        print(status, subunit, function, value)
        if status == YncaProtocol.STATUS_OK:
            if subunit == "SYS":
                self._handle_update(function, value)
            elif subunit in YncaReceiver._all_zones:
                if subunit in self.zones:
                    self.zones[subunit].update(function, value)
                else:
                    self.zones[subunit] = YncaZone(subunit, self._connection)
            elif function == "AVAIL":
                # subunit in YncaReceiver._all_inputs
                if subunit in YncaReceiver._subunit_input_mapping:
                    self.inputs[YncaReceiver._subunit_input_mapping[subunit]] = YncaReceiver._subunit_input_mapping[subunit]

    def _handle_update(self, function, value):
        if function == "MODELNAME":
            self.modelname = value
        elif function == "VERSION":
            self.software_version = value
        elif function == "PWR":
            if value == "On":
                self.powered = True
            else:
                self.powered = False
        elif function.startswith("INPNAME"):
            input_id = function[7:]
            self.inputs[input_id] = value


class YncaZone:
    def __init__(self, zone, connection):
        self.id = zone
        self._connection = connection

        self.name = None
        self.input = None
        self.volume = None
        self.max_volume = 0
        self.muted = None

        self.get("BASIC")  # Gets PWR, SLEEP, VOL, MUTE, INP, STRAIGHT, ENHANCER and SOUNDPROG (if applicable)
        self.get("MAXVOL")
        self.get("ZONENAME")

    def update(self, function, value):
        if function == "INP":
            self.input = value
        elif function == "VOL":
            self.volume = float(value)
        elif function == "MUTE":
            if value == "Off":
                self.muted = False
            else:
                self.muted = True
        elif function == "ZONENAME":
            self.name = value

    def put(self, function, value):
        self._connection.put(self.id, function, value)

    def get(self, function):
        self._connection.get(self.id, function)


if __name__ == "__main__":

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    receiver = YncaReceiver(port)
    # ynca.connect()
    # ynca.get("SYS", "VERSION")

    remaining = 5
    while remaining >= 0:
        print("Remaining: {}".format(remaining))
        # ynca.get("SYS", "PWR")
        time.sleep(1)
        remaining -= 1

    print(receiver)

    print("Zones:")
    print(receiver.zones)
    print("Inputs:")
    print(receiver.inputs)
    # ynca.disconnect()
