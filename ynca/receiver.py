from __future__ import annotations

import logging
import threading
from typing import Callable, Dict, Optional, Set, Type, cast

from .bt import Bt
from .connection import YncaConnection, YncaProtocolStatus
from .constants import Subunit
from .errors import YncaConnectionError, YncaInitializationFailedException
from .helpers import all_subclasses
from .mediaplayback_subunits import Ipod, Pc, Rhap, Usb, Napster
from .netradio import NetRadio
from .pandora import Pandora
from .sirius import Sirius, SiriusIr
from .subunit import SubunitBase
from .system import System
from .tun import Tun
from .uaw import Uaw
from .zone import Main, Zone2, Zone3, Zone4

logger = logging.getLogger(__name__)

# Map subunits to input names, this is used for discovering what inputs are available
# Inputs missing because unknown what subunit they map to: NET
SUBUNIT_INPUT_MAPPINGS: Dict[Subunit, str] = {
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
    Subunit.USB: "USB",
    Subunit.IPODUSB: "iPod (USB)",
    Subunit.UAW: "UAW",
}


class Receiver:
    def __init__(self, serial_url: str, disconnect_callback: Callable[[], None] = None):
        """Create a Receiver"""
        self._serial_url = serial_url
        self._connection: Optional[YncaConnection] = None
        self._available_subunits: Set = set()
        self._initialized_event = threading.Event()
        self._disconnect_callback = disconnect_callback

        # This is the list of instantiated Subunit classes
        self._subunits: Dict[Subunit, Type[SubunitBase]] = {}

    @property
    def inputs(self) -> Dict[str, str]:
        # Receiver has the main inputs as discovered by System subunit
        # These are the externally connectable inputs like HDMI1, AV1 etc...
        inputs = {}

        if Subunit.SYS in self._subunits:
            inputs = cast(System, self._subunits[Subunit.SYS]).inputs

        # Next to that there are internal inputs provided by subunits
        # for example the "Tuner"input is provided by the TUN subunit
        for subunit in self._available_subunits:
            if subunit in SUBUNIT_INPUT_MAPPINGS.keys():
                input_id = SUBUNIT_INPUT_MAPPINGS[subunit]
                inputs[input_id] = input_id
        return inputs

    def _detect_available_subunits(self):
        logger.debug("Subunit availability check start")
        self._initialized_event.clear()
        self._connection.register_message_callback(self._protocol_message_received)

        # Figure out what subunits are available
        num_commands_sent_start = self._connection.num_commands_sent
        self._available_subunits = set()
        for subunit_id in Subunit:
            self._connection.get(subunit_id, "AVAIL")

        # Use @SYS:VERSION=? as end marker (even though this is not the SYS subunit)
        self._connection.get(Subunit.SYS, "VERSION")

        if not self._initialized_event.wait(
            (self._connection.num_commands_sent - num_commands_sent_start) * 0.150
        ):  # Each command is ~100ms + some margin
            raise YncaInitializationFailedException(
                f"Subunit availability check failed"
            )

        self._connection.unregister_message_callback(self._protocol_message_received)
        logger.debug("Subunit availability check done")

    def _get_subunit_class(self, subunit_id):
        subunit_classes = all_subclasses(SubunitBase)
        for subunit_class in subunit_classes:
            if subunit_class.id == subunit_id:
                return subunit_class

    def _initialize_available_subunits(self):
        # Every receiver has a System subunit
        # It also does not respond to AVAIL=? so it will not end up in _available_subunits
        system = System(self._connection)
        system.initialize()
        self._subunits[system.id] = system

        # Initialize detected subunits
        for subunit_id in sorted(self._available_subunits):
            if subunit_class := self._get_subunit_class(subunit_id):
                subunit_instance = subunit_class(self._connection)
                subunit_instance.initialize()
                self._subunits[subunit_instance.id] = subunit_instance

    def connection_check(self) -> str:
        """
        Does a quick connection check by setting up a connection and requesting the modelname.
        Connection gets closed again automatically.

        This is a fast way to check the connection and if it is a YNCA device without
        executing the timeconsuming `initialize()` method.
        """
        connection_check_event = threading.Event()
        modelname = ""

        def _connection_check_message_received(
            status: YncaProtocolStatus, subunit: str, function_: str, value: str
        ):
            if subunit == Subunit.SYS and function_ == "MODELNAME":
                nonlocal modelname
                modelname = value
                connection_check_event.set()

        try:
            connection = YncaConnection.create_from_serial_url(self._serial_url)
            connection.connect(self._disconnect_callback)
            connection.register_message_callback(_connection_check_message_received)
            connection.get(Subunit.SYS, "MODELNAME")

            # Give it a bit of time to receive a response
            if not connection_check_event.wait(0.5):
                raise YncaConnectionError(
                    "Connectioncheck failed, no valid response in time from device"
                )
        finally:
            if connection:
                connection.unregister_message_callback(
                    _connection_check_message_received
                )
                connection.close()
        return modelname

    def initialize(self):
        """
        Sets up a connection to the device and initializes the Receiver.
        This call takes several seconds.
        """
        connection = YncaConnection.create_from_serial_url(self._serial_url)
        connection.connect(self._disconnect_callback)
        self._connection = connection

        self._detect_available_subunits()
        self._initialize_available_subunits()

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        if function_ == "AVAIL":
            self._available_subunits.add(subunit)

        if subunit == Subunit.SYS and function_ == "VERSION":
            self._initialized_event.set()

    def close(self):
        for subunit in self._subunits.values():
            subunit.close()
        if self._connection:
            self._connection.close()

    # Add properties for all known subunits
    # They are limited as defined by the spec and it is easy to access as a user of the library
    # Also helps with typing compared to using generic SubunitBase types

    @property
    def SYS(self) -> System | None:
        return cast(System, self._subunits.get(Subunit.SYS, None))

    @property
    def MAIN(self) -> Main | None:
        return cast(Main, self._subunits.get(Subunit.MAIN, None))

    @property
    def ZONE2(self) -> Zone2 | None:
        return cast(Zone2, self._subunits.get(Subunit.ZONE2, None))

    @property
    def ZONE3(self) -> Zone3 | None:
        return cast(Zone3, self._subunits.get(Subunit.ZONE3, None))

    @property
    def ZONE4(self) -> Zone4 | None:
        return cast(Zone4, self._subunits.get(Subunit.ZONE4, None))

    @property
    def PC(self) -> Pc | None:
        return cast(Pc, self._subunits.get(Subunit.PC, None))

    @property
    def NETRADIO(self) -> NetRadio | None:
        return cast(NetRadio, self._subunits.get(Subunit.NETRADIO, None))

    @property
    def USB(self) -> Usb | None:
        return cast(Usb, self._subunits.get(Subunit.USB, None))

    @property
    def TUN(self) -> Tun | None:
        return cast(Tun, self._subunits.get(Subunit.TUN, None))

    @property
    def SIRIUS(self) -> Sirius | None:
        return cast(Sirius, self._subunits.get(Subunit.SIRIUS, None))

    @property
    def SIRIUSIR(self) -> SiriusIr | None:
        return cast(SiriusIr, self._subunits.get(Subunit.SIRIUSIR, None))

    @property
    def IPOD(self) -> Ipod | None:
        return cast(Ipod, self._subunits.get(Subunit.IPOD, None))

    @property
    def BT(self) -> Bt | None:
        return cast(Bt, self._subunits.get(Subunit.BT, None))

    @property
    def RHAP(self) -> Rhap | None:
        return cast(Rhap, self._subunits.get(Subunit.RHAP, None))

    @property
    def PANDORA(self) -> Pandora | None:
        return cast(Pandora, self._subunits.get(Subunit.PANDORA, None))

    @property
    def UAW(self) -> Uaw | None:
        return cast(Uaw, self._subunits.get(Subunit.UAW, None))

    @property
    def NAPSTER(self) -> Napster | None:
        return cast(Napster, self._subunits.get(Subunit.NAPSTER, None))
