import threading
import logging

from typing import Callable, Dict, List, Set

from .connection import YncaConnection, YncaProtocolStatus
from .errors import YncaInitializationFailedException
from .subunit import Subunit

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


class System(Subunit):
    def __init__(self, subunit_id: str, connection: YncaConnection):
        """
        Constructor for a Receiver object.
        """
        super().__init__(subunit_id, connection)
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

    def __str__(self):
        output = []
        for key in self.__dict__:
            output.append("{key}={value}".format(key=key, value=self.__dict__[key]))

        return "\n".join(output)

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        super()._protocol_message_received(status, subunit, function_, value)

        # TODO move this handling aout of the SYS subunit
        if not self._initialized:
            if subunit in ALL_ZONES and subunit not in self.zones:
                self.zones.append(subunit)
            elif function_ == "AVAIL":
                if subunit in SUBUNIT_INPUT_MAPPINGS:
                    self.inputs[
                        SUBUNIT_INPUT_MAPPINGS[subunit]
                    ] = SUBUNIT_INPUT_MAPPINGS[subunit]

    def _unhandled_subunit_message_received(
        self, status: YncaProtocolStatus, function_: str, value: str
    ) -> bool:
        updated = True

        if function_.startswith("INPNAME"):
            input_id = function_[7:]
            if input_id == "VAUX":
                # Input ID used to set/get INP is actually V-AUX so compensate for that mismatch on the API
                input_id = "V-AUX"
            self.inputs[input_id] = value
        else:
            updated = False

        return updated

    def _handle_pwr(self, value: str):
        self._power = value == "On"

    def _handle_modelname(self, value: str):
        self.model_name = value

    def _handle_version(self, value: str):
        self.firmware_version = value

        # During initialization this is used to signal
        # that initialization is done
        if not self._initialized:
            self._initialized_event.set()

    @property
    def on(self):
        """Get current on state"""
        return self._power

    @on.setter
    def on(self, value: bool):
        """Turn on/off receiver"""
        self._put("PWR", "On" if value is True else "Standby")
