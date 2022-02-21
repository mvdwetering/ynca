import threading
import logging

from typing import Dict

from serial import SerialException

from .connection import YncaConnection, YncaProtocolStatus
from .errors import YncaConnectionError
from .zone import YncaZone

logger = logging.getLogger(__name__)

ALL_ZONES = ["MAIN", "ZONE2", "ZONE3", "ZONE4"]

# Map subunits to input names, this is used for discovering what inputs are available
# Inputs missing because unknown what subunit they map to: NET
SUBUNIT_INPUT_MAPPINGS = {
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


class YncaReceiver:
    def __init__(self, port, on_update=None):
        """
        Constructor for a Receiver object.
        """
        self._port = port
        self._initialized_event = threading.Event()
        self._on_update_callback = on_update
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._power = None
        self.model_name = None
        self.firmware_version = None
        self.zones: Dict[str, YncaZone] = {}
        self.inputs: Dict[str, str] = {}

    def initialize(self):
        """
        Initializes the receiver.

        Communicates with the device to determine capabilities.
        This is a long running function!
        It will take several seconds to complete
        """
        self._reset_internal_state()

        # Avoid update callbacks during initialization
        stored_on_update_callback = self._on_update_callback
        self._on_update_callback = None

        try:
            self._connection = YncaConnection(self._port, self._connection_update)
            self._connection.connect()
            self._initialize_device()
        except SerialException as e:
            raise YncaConnectionError(e)
        finally:
            self._connection.disconnect()

        # Re-install on_update callback and call it to signal changes occurred during initialization
        self._on_update_callback = stored_on_update_callback
        if self._on_update_callback:
            self._on_update_callback()

    def close(self):
        if self._connection:
            self._connection.disconnect()

    def __str__(self):
        output = []
        for key in self.__dict__:
            output.append("{key}={value}".format(key=key, value=self.__dict__[key]))

        return "\n".join(output)

    def _initialize_device(self):
        """ Communicate with the device to setup initial state and discover capabilities """
        logger.info("Receiver initialization start.")

        self._sys_get("MODELNAME")
        self._sys_get("PWR")

        # Get user-friendly names for inputs (also allows detection of a number of available inputs)
        # Note that these are not all inputs, just the external ones it seems.
        self._sys_get("INPNAME")

        # A device also can have a number of 'internal' inputs like the Tuner, USB, Napster etc..
        # There is no way to get which of there inputs are supported by the device so just try all that we know of.
        for subunit in SUBUNIT_INPUT_MAPPINGS:
            self._connection.get(subunit, "AVAIL")

        # There is no way to get which zones are supported by the device to just try all possible.
        # The callback will create any zone instances on success responses.
        for zone in ALL_ZONES:
            self._connection.get(zone, "AVAIL")

        self._sys_get("VERSION")  # Use version as a "sync" command
        if not self._initialized_event.wait(
            10
        ):  # Each command is 100ms (at least) and a lot are sent.
            logger.error("Receiver initialization phase 1 failed!")

        # Initialize the zones (constructors are synchronous)
        for zone in self._zones_to_initialize:
            logger.info("Initializing zone {}.".format(zone))
            self.zones[zone] = YncaZone(zone, self._connection, self.inputs)
            self.zones[zone].initialize()
        self._zones_to_initialize = None

        logger.info("Receiver initialization done.")

    def _connection_update(self, status, subunit, function_, value):
        if status == YncaProtocolStatus.OK:
            if subunit == "SYS":
                self._sys_update(function_, value)
            elif subunit in self.zones:
                self.zones[subunit].update(function_, value)
            elif subunit in ALL_ZONES:
                self._zones_to_initialize.append(subunit)
            elif function_ == "AVAIL":
                if subunit in SUBUNIT_INPUT_MAPPINGS:
                    self.inputs[
                        SUBUNIT_INPUT_MAPPINGS[subunit]
                    ] = SUBUNIT_INPUT_MAPPINGS[subunit]

    def _sys_update(self, function_, value):
        updated = True
        if function_ == "MODELNAME":
            self.model_name = value
        elif function_ == "VERSION":
            self.firmware_version = value
            self._initialized_event.set()
        elif function_ == "PWR":
            if value == "On":
                self._power = True
            else:
                self._power = False
        elif function_.startswith("INPNAME"):
            input_id = function_[7:]
            if input_id == "VAUX":
                # Input ID used to set/get INP is actually V-AUX so compensate for that
                input_id = "V-AUX"
            self.inputs[input_id] = value
        else:
            updated = False

        if updated and self._on_update_callback:
            self._on_update_callback()

    def _sys_put(self, function_, value):
        self._connection.put("SYS", function_, value)

    def _sys_get(self, function_):
        self._connection.get("SYS", function_)

    @property
    def on(self):
        """Get current on state"""
        return self._power

    @on.setter
    def on(self, value):
        """Turn on/off receiver"""
        assert value in [True, False]  # Is this usefull?
        self._sys_put("PWR", "On" if value is True else "Standby")
