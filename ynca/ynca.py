from __future__ import annotations

import logging
import threading
from typing import Callable, Dict, List, Optional, Set, Type, cast

from .airplay import Airplay
from .bt import Bt
from .connection import YncaConnection, YncaProtocol, YncaProtocolStatus
from .constants import Subunit
from .errors import YncaConnectionError, YncaInitializationFailedException
from .helpers import all_subclasses
from .mediaplayback_subunits import (
    Ipod,
    IpodUsb,
    Napster,
    Pc,
    Rhap,
    Spotify,
    Usb,
    Server,
)
from .netradio import NetRadio
from .pandora import Pandora
from .sirius import Sirius, SiriusIr, SiriusXm
from .subunit import SubunitBase
from .system import System
from .tun import Tun
from .uaw import Uaw
from .zone import Main, Zone2, Zone3, Zone4

logger = logging.getLogger(__name__)


class Ynca:
    def __init__(
        self,
        serial_url: str,
        disconnect_callback: Callable[[], None] = None,
        communication_log_size: int = 0,
    ):
        """
        Create a YNCA API instance

        serial_url:
            Can be a devicename (e.g. /dev/ttyUSB0 or COM3),
            but also any of supported url handlers by pyserial
            https://pyserial.readthedocs.io/en/latest/url_handlers.html
            This allows to setup IP connections with socket://ip:50000
            or select a specific usb-2-serial with hwgrep:// which is
            useful when the links to ttyUSB# change randomly.

        disconnect_callback:
            Callable that gets called when the connection gets disconnected.

        communication_log_size:
            Amount of communication items to log. Useful for debugging.
            Get the logged items with the `get_communication_log_items` method
        """
        self._serial_url = serial_url
        self._connection: Optional[YncaConnection] = None
        self._available_subunits: Set = set()
        self._initialized_event = threading.Event()
        self._disconnect_callback = disconnect_callback
        self._communication_log_size = communication_log_size

        # This is the list of instantiated Subunit classes
        self._subunits: Dict[Subunit, Type[SubunitBase]] = {}

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

        # Take command spacing into account and apply large margin
        # Large margin is needed in practice on slower/busier systems
        num_commands_sent = self._connection.num_commands_sent - num_commands_sent_start
        if not self._initialized_event.wait(
            2 + (num_commands_sent * (YncaProtocol.COMMAND_SPACING * 5))
        ):
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
            connection.connect(self._disconnect_callback, self._communication_log_size)
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
        Sets up a connection to the device and initializes the Ynca API.
        This call takes quite a while (~10 seocnds on a simple 2 zone receiver).

        If initialize was successful the client should call the `close()`
        method when done with the Ynca API object to cleanup.
        """
        assert self._connection == None, "Can only initialize once!"

        is_initialized = False

        connection = YncaConnection.create_from_serial_url(self._serial_url)
        connection.connect(self._disconnect_callback, self._communication_log_size)
        self._connection = connection

        try:
            self._detect_available_subunits()
            self._initialize_available_subunits()
            is_initialized = True
        finally:
            if not is_initialized:
                self.close()

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        if function_ == "AVAIL":
            self._available_subunits.add(subunit)

        if subunit == Subunit.SYS and function_ == "VERSION":
            self._initialized_event.set()

    def get_communication_log_items(self) -> List[str]:
        """Get a list of logged communication items."""
        return (
            self._connection.get_communication_log_items() if self._connection else []
        )

    def close(self):
        """
        Cleanup the internal resources.
        Safe to be called at any time.

        Ynca object should _not_ be reused after being closed!
        """
        # Convert to list to avoid issues when deleting while iterating
        for id in list(self._subunits.keys()):
            subunit = self._subunits.pop(id, None)
            subunit.close()
        if self._connection:
            self._connection.close()
            self._connection = None

    # Add properties for all known subunits
    # The amount is limited as defined by the spec and it is easy to access as a user of the library
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
    def IPODUSB(self) -> IpodUsb | None:
        return cast(IpodUsb, self._subunits.get(Subunit.IPODUSB, None))

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

    @property
    def SPOTIFY(self) -> Spotify | None:
        return cast(Spotify, self._subunits.get(Subunit.SPOTIFY, None))

    @property
    def SERVER(self) -> Server | None:
        return cast(Server, self._subunits.get(Subunit.SERVER, None))

    @property
    def SIRIUSXM(self) -> SiriusXm | None:
        return cast(SiriusXm, self._subunits.get(Subunit.SIRIUSXM, None))

    @property
    def AIRPLAY(self) -> Airplay | None:
        return cast(Airplay, self._subunits.get(Subunit.AIRPLAY, None))
