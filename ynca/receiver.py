import threading
import logging

from typing import Callable, Dict, List, Set

from .connection import YncaConnection, YncaProtocolStatus
from .errors import YncaInitializationFailedException

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
    def __init__(self, connection: YncaConnection):
        """
        Constructor for a Receiver object.
        """
        self._update_callbacks: Set[Callable[[], None]] = set()

        self._connection = connection
        connection.register_message_callback(self._protocol_message_received)

        self.zones: List[str] = []

        self._initialized_event = threading.Event()
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._initialized = False
        self._power = None
        self.zones = []
        self.model_name = None
        self.firmware_version = None
        self.zones: List[str] = []
        self.inputs: Dict[str, str] = {}
        self._initialized_event.clear()

    def initialize(self):
        """
        Initializes the receiver.

        Communicates with the device to determine capabilities.
        This is a long running function!
        It will take several seconds to complete
        """
        logger.info("Receiver initialization start.")

        self._reset_internal_state()

        self._get("MODELNAME")
        self._get("PWR")

        # Get user-friendly names for inputs (also allows detection of a number of available inputs)
        # Note that these are not all inputs, just the external ones it seems.
        self._get("INPNAME")

        # A device also can have a number of 'internal' inputs like the Tuner, USB, Napster etc..
        # There is no way to get a list of inputs that are supported by the device so just try all that we know of.
        for subunit in SUBUNIT_INPUT_MAPPINGS:
            self._connection.get(subunit, "AVAIL")

        # There is no way to get a list of zones that are supported by the device to just try all possible.
        # On receiving a positive response the zone is added to the zones list.
        for zone in ALL_ZONES:
            self._connection.get(zone, "AVAIL")

        self._get("VERSION")  # Use version as a "sync" command
        if not self._initialized_event.wait(
            10
        ):  # Each command is 100ms (at least) and a lot are sent.
            raise YncaInitializationFailedException("Receiver initialization failed")

        logger.info("Receiver initialization done.")

        self._initialized = True
        self._call_registered_update_callbacks()

    def close(self):
        self._connection.unregister_message_callback(self._protocol_message_received)
        self._connection = None
        self._update_callbacks = set()

    def __str__(self):
        output = []
        for key in self.__dict__:
            output.append("{key}={value}".format(key=key, value=self.__dict__[key]))

        return "\n".join(output)

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        if status == YncaProtocolStatus.OK:
            if subunit == "SYS":
                self._sys_update(function_, value)
            elif not self._initialized:
                if subunit in ALL_ZONES and subunit not in self.zones:
                    self.zones.append(subunit)
                elif function_ == "AVAIL":
                    if subunit in SUBUNIT_INPUT_MAPPINGS:
                        self.inputs[
                            SUBUNIT_INPUT_MAPPINGS[subunit]
                        ] = SUBUNIT_INPUT_MAPPINGS[subunit]

    def _sys_update(self, function_: str, value: str):
        # Only PWR will change during normal operation
        # Others are only relevant during initializaiton
        # where we don't want all the update callbacks
        # And MODELNAME will be used for keepalive so we
        # don't want update callbacks for those responses
        # Hence default to updated = False
        updated = False

        if function_ == "PWR":
            if value == "On":
                self._power = True
            else:
                self._power = False
            updated = True
        elif function_ == "MODELNAME":
            self.model_name = value
        elif function_ == "VERSION":
            self.firmware_version = value
            if not self._initialized:
                self._initialized_event.set()
        elif function_.startswith("INPNAME"):
            input_id = function_[7:]
            if input_id == "VAUX":
                # Input ID used to set/get INP is actually V-AUX so compensate for that mismatch on the API
                input_id = "V-AUX"
            self.inputs[input_id] = value

        if updated:
            self._call_registered_update_callbacks()

    def _put(self, function_: str, value: str):
        self._connection.put("SYS", function_, value)

    def _get(self, function_: str):
        self._connection.get("SYS", function_)

    def register_update_callback(self, callback: Callable[[], None]):
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[], None]):
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self):
        if self._initialized:
            for callback in self._update_callbacks:
                callback()

    @property
    def on(self):
        """Get current on state"""
        return self._power

    @on.setter
    def on(self, value: bool):
        """Turn on/off receiver"""
        self._put("PWR", "On" if value is True else "Standby")
