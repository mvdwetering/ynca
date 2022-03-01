import threading
import logging

from typing import Dict, Optional, cast

from .connection import YncaConnection, YncaProtocolStatus
from .constants import ZONES, Subunit
from .errors import YncaInitializationFailedException
from .system import System
from .zone import Zone

logger = logging.getLogger(__name__)

# Map subunits to input names, this is used for discovering what inputs are available
# Inputs missing because unknown what subunit they map to: NET
SUBUNIT_INPUT_MAPPINGS: Dict[str, str] = {
    Subunit.TUN: "TUNER",
    Subunit.SIRIUS: "SIRIUS",
    Subunit.IPOD: "iPod",
    Subunit.BT: "Bluetooth",
    Subunit.RHAP: "Rhapsody",
    Subunit.SIRIUSIR: "SIRIUS InternetRadio",
    Subunit.PANDORA: "Pandora",
    Subunit.NAPSTER: "Napster",
    Subunit.PC: "PC",
    Subunit.NETRADIO: "NET RADIO",
    Subunit.IPODUSB: "iPod (USB)",
    Subunit.UAW: "UAW",
}


class YncaReceiver:
    def __init__(self, serial_url: str):
        """Create a YncaReceiver"""
        self._serial_url = serial_url
        self._connection: Optional[YncaConnection] = None
        self._available_subunits: Dict[str, bool] = {}
        self._initialized_event = threading.Event()

        # This is the list of instantiated Subunit classes
        self.subunits: Dict[str, Subunit] = {}

    @property
    def inputs(self) -> Dict[str, str]:
        # Receiver has the main inputs as discovered by System subunit
        # These are the externally connectable inputs like HDMI1, AV1 etc...
        inputs = cast(System, self.subunits[Subunit.SYS]).inputs

        # Next to that there are internal inputs provided by subunits
        # for example the "Tuner"input is provided by the TUN subunit
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

        # Figure out what subunits are available
        self._available_subunits = {}
        for subunit in Subunit:
            self._connection.get(subunit, "AVAIL")

        # Use @SYS:VERSION=? as end marker (even though this is not the SYS subunit)
        self._connection.get(Subunit.SYS, "VERSION")

        if not self._initialized_event.wait(
            (len(Subunit) + 1) * 0.125
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
        for zone_id in ZONES:
            try:
                if self._available_subunits[zone_id] is True:
                    zone = Zone(zone_id, connection)
                    zone.initialize()
                    self.subunits[zone.id] = zone
            except KeyError:
                pass

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        if function_ == "AVAIL":
            self._available_subunits[subunit] = status is YncaProtocolStatus.OK

        if subunit == Subunit.SYS and function_ == "VERSION":
            self._initialized_event.set()

    def close(self):
        for subunit in self.subunits.values():
            subunit.close()
        self._connection.close()
