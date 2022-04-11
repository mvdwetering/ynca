from __future__ import annotations
import logging
import threading

from typing import Callable, Optional, Set

from ynca.function_mixins import FunctionMixinBase

from .constants import Avail, Subunit
from .errors import YncaInitializationFailedException

from .connection import YncaConnection, YncaProtocol, YncaProtocolStatus

logger = logging.getLogger(__name__)


class SubunitBase(FunctionMixinBase):

    # To be set in subclasses
    id: str = ""

    def __init__(self, connection: YncaConnection):
        """
        Baseclass for Subunits, should be subclassed do not instantiate manually.
        """
        self._update_callbacks: Set[Callable[[], None]] = set()

        self._attr_avail: Avail | None = None

        self._initialized = False
        self._initialized_event = threading.Event()

        self._connection = connection
        self._connection.register_message_callback(self._protocol_message_received)

        self.function_mixin_initialize_function_attributes()

    def initialize(self):
        """
        Initializes the data for the subunit and makes sure to wait until done.
        This call can take a long time
        """

        logger.debug("Subunit %s initialization start.", self.id)

        self._initialized_event.clear()
        self._initialized = False

        num_commands_sent_start = self._connection.num_commands_sent

        # Build list of YNCA functions to request
        functions = ["AVAIL"]
        functions.extend(self.function_mixin_functions())

        # Request YNCA functions
        for function in functions:
            self._connection.get(self.id, function)

        # Invoke subunit specific initialization implemented in the derived classes
        self.on_initialize()

        # Use SYS:VERSION as a sync since it is available on all receivers
        # and has a guarenteed response
        self._connection.get(Subunit.SYS, "VERSION")

        # Take command spacing into account and apply large margin
        # Large margin is needed in practice on slower/busier systems
        num_commands_sent = self._connection.num_commands_sent - num_commands_sent_start
        if self._initialized_event.wait(
            2 + num_commands_sent * (YncaProtocol.COMMAND_SPACING * 5)
        ):
            self._initialized = True
        else:
            raise YncaInitializationFailedException(
                f"Subunit {self.id} initialization failed"
            )

        logger.debug("Subunit %s initialization done.", self.id)
        self._call_registered_update_callbacks()

    def on_initialize(self):
        """
        Initializes the data for the subunit.
        Can be implemented in derived classes.
        """
        pass

    def close(self):
        if self._connection:
            self._connection.unregister_message_callback(
                self._protocol_message_received
            )
            self._connection = None
            self._update_callbacks = set()

    def _subunit_message_received_without_handler(
        self, status: YncaProtocolStatus, function_: str, value: str
    ) -> bool:
        """
        Called when a message for this subunit was received with no handler
        Implement in subclasses for cases where a simple handler is not enough.

        Return True if state was updated because of the message.
        """
        return False

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        if status is not YncaProtocolStatus.OK:
            # Can't really handle errors since at this point we can't see to what command it belonged
            return

        # During initialization SYS:VERSION is used to signal that initialization is done
        if not self._initialized and subunit == Subunit.SYS and function_ == "VERSION":
            self._initialized_event.set()

        if self.id != subunit:
            return

        updated = False

        if hasattr(self, f"_attr_{function_.lower()}"):
            setattr(self, f"_attr_{function_.lower()}", value)
            updated = True
        elif handler := getattr(self, f"_handle_{function_.lower()}", None):
            handler(value)
            updated = True
        else:
            updated = self._subunit_message_received_without_handler(
                status, function_, value
            )

        if updated:
            self._call_registered_update_callbacks()

    def _put(self, function_: str, value: str):
        self._connection.put(self.id, function_, value)

    def _get(self, function_: str):
        self._connection.get(self.id, function_)

    def register_update_callback(self, callback: Callable[[], None]):
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[], None]):
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self):
        if self._initialized:
            for callback in self._update_callbacks:
                callback()

    @property
    def avail(self) -> Optional[Avail]:
        """Get avail status"""
        return self._attr_avail
