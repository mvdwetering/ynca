import threading
import logging

from typing import Dict, List, Optional

from .connection import YncaConnection, YncaProtocolStatus
from .constants import ZONES, Subunit
from .errors import YncaInitializationFailedException
from .system import System
from .zone import YncaZone

logger = logging.getLogger(__name__)

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

NUM_POTENTIAL_SUBUNITS = len(SUBUNIT_INPUT_MAPPINGS.keys()) + len(ZONES)


class YncaReceiver:
    def __init__(self, serial_url: str):
        """Create a YncaReceiver"""
        self._serial_url = serial_url
        self._connection: Optional[YncaConnection] = None
        self.subunits: Dict[str, Subunit] = {}

        self._available_subunits: Dict[str, bool] = {}

        self._initialized_event = threading.Event()

    @property
    def inputs(self) -> Dict[str, str]:
        inputs = self.subunits[Subunit.SYS].inputs
        for subunit, available in self._available_subunits.items():
            if available and subunit in SUBUNIT_INPUT_MAPPINGS.keys():
                input_id = SUBUNIT_INPUT_MAPPINGS[subunit]
                inputs[input_id] = input_id
        return inputs

    def initialize(self):
        """
        Sets up a connection to the device and initializes the YncaReceiver.
        This call takes several seconds.
        """
        connection = YncaConnection(self._serial_url)
        connection.connect()
        self._connection = connection

        logger.debug("Subunit availability check start")
        self._initialized_event.clear()
        connection.register_message_callback(self._protocol_message_received)
        self._available_subunits = {}

        # Figure out what subunits are available

        # A device also can have a number of 'internal' inputs like the Tuner, USB, Napster etc..
        # There is no way to get a list of inputs that are supported by the device so just check all that we know of.
        for subunit in SUBUNIT_INPUT_MAPPINGS.keys():
            self._connection.get(subunit, "AVAIL")

        # There is no way to get a list of zones that are supported by the device to just try all possible.
        # On receiving a positive response the zone is added to the subunits list.
        for zone in ZONES:
            self._connection.get(zone, "AVAIL")

        # Use @SYS:VERSION=? as end marker (even though this is not the SYS subunit)
        self._connection.get("SYS", "VERSION")

        if not self._initialized_event.wait(
            NUM_POTENTIAL_SUBUNITS * 0.125
        ):  # Each command is ~100ms + some margin
            raise YncaInitializationFailedException(
                f"Subunit availability check failed"
            )

        connection.unregister_message_callback(self._protocol_message_received)
        logger.debug("Subunit availability check done")

        # Every receiver has a System subunit (can not even check for its existence)
        system = System(connection)
        system.initialize()
        self.subunits[system.id] = system

        # Initialize zones
        zones = {}
        for zone_id in ZONES:
            try:
                if self._available_subunits[zone_id] is True:
                    zone = YncaZone(zone_id, connection)
                    zone.initialize()
                    self.subunits[zone.id] = zone
            except KeyError:
                pass

        print(self._available_subunits)

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        if function_ == "AVAIL":
            self._available_subunits[subunit] = status is YncaProtocolStatus.OK

        if subunit == "SYS" and function_ == "VERSION":
            self._initialized_event.set()

    def close(self):
        for subunit in self.subunits.values():
            subunit.close()
        self._connection.close()
