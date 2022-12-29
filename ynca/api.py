from __future__ import annotations

from dataclasses import dataclass, field
import logging
import threading
from typing import Callable, Dict, List, Optional, Set, cast

from .connection import YncaConnection, YncaProtocol, YncaProtocolStatus
from .constants import Subunit
from .errors import YncaConnectionError, YncaInitializationFailedException
from .helpers import all_subclasses
from .subunit import SubunitBase
from .subunits.airplay import Airplay
from .subunits.bt import Bt
from .subunits.dab import Dab
from .subunits.ipod import Ipod
from .subunits.ipodusb import IpodUsb
from .subunits.napster import Napster
from .subunits.netradio import NetRadio
from .subunits.pandora import Pandora
from .subunits.pc import Pc
from .subunits.rhap import Rhap
from .subunits.server import Server
from .subunits.sirius import Sirius, SiriusIr, SiriusXm
from .subunits.spotify import Spotify
from .subunits.system import System
from .subunits.tun import Tun
from .subunits.uaw import Uaw
from .subunits.usb import Usb
from .subunits.zone import Main, Zone2, Zone3, Zone4

logger = logging.getLogger(__name__)

CONNECTION_CHECK_TIMEOUT = 1.5


@dataclass
class YncaConnectionCheckResult:
    modelname: str = ""
    zones: List[str] = field(default_factory=list)


class YncaApi:
    def __init__(
        self,
        serial_url: str,
        disconnect_callback: Callable[[], None] | None = None,
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
        self._subunits: Dict[Subunit, SubunitBase] = {}

    def _detect_available_subunits(self, connection: YncaConnection):
        logger.info("Subunit availability check begin")
        self._initialized_event.clear()
        connection.register_message_callback(self._protocol_message_received)

        # Figure out what subunits are available
        num_commands_sent_start = connection.num_commands_sent
        self._available_subunits = set()
        for subunit_id in Subunit:
            connection.get(subunit_id, "AVAIL")

        # Use @SYS:VERSION=? as end marker (even though this is not the SYS subunit)
        connection.get(Subunit.SYS, "VERSION")

        # Take command spacing into account and apply large margin
        # Large margin is needed in practice on slower/busier systems
        num_commands_sent = connection.num_commands_sent - num_commands_sent_start
        if not self._initialized_event.wait(
            2 + (num_commands_sent * (YncaProtocol.COMMAND_SPACING * 5))
        ):
            raise YncaInitializationFailedException(
                f"Subunit availability check failed"
            )

        connection.unregister_message_callback(self._protocol_message_received)
        logger.info("Subunit availability check end")

    def _get_subunit_class(self, subunit_id):
        subunit_classes = all_subclasses(SubunitBase)
        for subunit_class in subunit_classes:
            try:
                if subunit_class.id == subunit_id:
                    return subunit_class
            except AttributeError:
                # Intermediate Subunit classes like ZoneBase don't have an ID
                pass

    def _initialize_available_subunits(self, connection: YncaConnection):
        # Every receiver has a System subunit
        # It also does not respond to AVAIL=? so it will not end up in _available_subunits
        system = System(connection)
        system.initialize()
        self._subunits[system.id] = system

        # Initialize detected subunits
        for subunit_id in sorted(self._available_subunits):
            if subunit_class := self._get_subunit_class(subunit_id):
                subunit_instance = subunit_class(connection)
                subunit_instance.initialize()
                self._subunits[subunit_instance.id] = subunit_instance

    def connection_check(self) -> YncaConnectionCheckResult:
        """
        Does a quick connection check by setting up a connection and requesting some basic info.
        Connection gets closed again automatically.

        This is a fast way to check the connection and if it is a YNCA device
        without executing the timeconsuming `initialize()` method.
        """
        result: YncaConnectionCheckResult = YncaConnectionCheckResult()
        connection = None
        connection_check_event = threading.Event()

        def _connection_check_message_received(
            status: YncaProtocolStatus, subunit: str, function_: str, value: str
        ):
            if subunit == Subunit.SYS and function_ == "MODELNAME":
                result.modelname = value
                connection_check_event.set()
            if function_ == "AVAIL":
                result.zones.append(subunit)

        try:
            connection = YncaConnection.create_from_serial_url(self._serial_url)
            connection.connect(self._disconnect_callback, self._communication_log_size)
            connection.register_message_callback(_connection_check_message_received)
            connection.get(Subunit.MAIN, "AVAIL")
            connection.get(Subunit.ZONE2, "AVAIL")
            connection.get(Subunit.ZONE3, "AVAIL")
            connection.get(Subunit.ZONE4, "AVAIL")
            connection.get(Subunit.SYS, "MODELNAME")

            # Give it a bit of time to receive a response
            if not connection_check_event.wait(CONNECTION_CHECK_TIMEOUT):
                raise YncaConnectionError(
                    "Connectioncheck failed, no valid response in time from device"
                )
        finally:
            if connection:
                connection.unregister_message_callback(
                    _connection_check_message_received
                )
                connection.close()

        return result

    def initialize(self):
        """
        Sets up a connection to the device and initializes the Ynca API.
        This call takes quite a while (~10 seconds on a simple 2 zone receiver).

        If initialize was successful the client should call the `close()`
        method when done with the Ynca API object to cleanup.
        """
        assert self._connection == None, "Can only initialize once!"

        is_initialized = False

        connection = YncaConnection.create_from_serial_url(self._serial_url)
        connection.connect(self._disconnect_callback, self._communication_log_size)
        self._connection = connection

        try:
            self._detect_available_subunits(connection)
            self._initialize_available_subunits(connection)
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

    def send_raw(self, raw_ynca_data: str):
        """
        Send raw YNCA data
        Intended for debugging only
        """
        if self._connection:
            self._connection.raw(raw_ynca_data)

    def close(self):
        """
        Cleanup the internal resources.
        Safe to be called at any time.

        YncaApi object should _not_ be reused after being closed!
        """
        # Convert to list to avoid issues when deleting while iterating
        for id in list(self._subunits.keys()):
            subunit = self._subunits.pop(id)
            subunit.close()
        if self._connection:
            self._connection.close()
            self._connection = None

    # Add properties for all known subunits
    # The amount is limited as defined by the spec and it is easy to access as a user of the library
    # Also helps with typing compared to using generic SubunitBase types

    @property
    def airplay(self) -> Optional[Airplay]:
        return cast(Airplay, self._subunits.get(Subunit.AIRPLAY, None))

    @property
    def bt(self) -> Optional[Bt]:
        return cast(Bt, self._subunits.get(Subunit.BT, None))

    @property
    def dab(self) -> Optional[Dab]:
        return cast(Dab, self._subunits.get(Subunit.DAB, None))

    @property
    def ipod(self) -> Optional[Ipod]:
        return cast(Ipod, self._subunits.get(Subunit.IPOD, None))

    @property
    def ipodusb(self) -> Optional[IpodUsb]:
        return cast(IpodUsb, self._subunits.get(Subunit.IPODUSB, None))

    @property
    def main(self) -> Optional[Main]:
        return cast(Main, self._subunits.get(Subunit.MAIN, None))

    @property
    def napster(self) -> Optional[Napster]:
        return cast(Napster, self._subunits.get(Subunit.NAPSTER, None))

    @property
    def netradio(self) -> Optional[NetRadio]:
        return cast(NetRadio, self._subunits.get(Subunit.NETRADIO, None))

    @property
    def pandora(self) -> Optional[Pandora]:
        return cast(Pandora, self._subunits.get(Subunit.PANDORA, None))

    @property
    def pc(self) -> Optional[Pc]:
        return cast(Pc, self._subunits.get(Subunit.PC, None))

    @property
    def rhap(self) -> Optional[Rhap]:
        return cast(Rhap, self._subunits.get(Subunit.RHAP, None))

    @property
    def server(self) -> Optional[Server]:
        return cast(Server, self._subunits.get(Subunit.SERVER, None))

    @property
    def sirius(self) -> Optional[Sirius]:
        return cast(Sirius, self._subunits.get(Subunit.SIRIUS, None))

    @property
    def siriusir(self) -> Optional[SiriusIr]:
        return cast(SiriusIr, self._subunits.get(Subunit.SIRIUSIR, None))

    @property
    def siriusxm(self) -> Optional[SiriusXm]:
        return cast(SiriusXm, self._subunits.get(Subunit.SIRIUSXM, None))

    @property
    def spotify(self) -> Optional[Spotify]:
        return cast(Spotify, self._subunits.get(Subunit.SPOTIFY, None))

    @property
    def sys(self) -> Optional[System]:
        return cast(System, self._subunits.get(Subunit.SYS, None))

    @property
    def tun(self) -> Optional[Tun]:
        return cast(Tun, self._subunits.get(Subunit.TUN, None))

    @property
    def uaw(self) -> Optional[Uaw]:
        return cast(Uaw, self._subunits.get(Subunit.UAW, None))

    @property
    def usb(self) -> Optional[Usb]:
        return cast(Usb, self._subunits.get(Subunit.USB, None))

    @property
    def zone2(self) -> Optional[Zone2]:
        return cast(Zone2, self._subunits.get(Subunit.ZONE2, None))

    @property
    def zone3(self) -> Optional[Zone3]:
        return cast(Zone3, self._subunits.get(Subunit.ZONE3, None))

    @property
    def zone4(self) -> Optional[Zone4]:
        return cast(Zone4, self._subunits.get(Subunit.ZONE4, None))
