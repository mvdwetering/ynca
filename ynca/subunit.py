from __future__ import annotations

from enum import Enum, Flag, auto
import inspect
import logging
import threading
from typing import Any, Callable, Dict, Set, Type, TypeVar, Generic

from .constants import Avail, Subunit
from .errors import YncaInitializationFailedException
from .connection import YncaConnection, YncaProtocol, YncaProtocolStatus

logger = logging.getLogger(__name__)


class CommandType(Flag):
    GET = auto()
    PUT = auto()


T = TypeVar("T")


class YncaFunction(Generic[T]):
    """
    Provides an easy way to specify all properties needed to handle a YNCA function.
    The resulting descriptor makes it easy to just read/write to the attributes and
    values will be read from cache or converted and sent to the device.
    """

    def __init__(
        self,
        function_name: str,
        datatype: Type | None = None,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        value_converter: Callable[[str], T] | None = None,
        str_converter: Callable[[T], str] | None = None,
    ):
        self.function_name = function_name
        self.datatype = datatype
        self.command_type = command_type
        self.value_converter = value_converter
        self._str_converter = str_converter

    def __get__(self, instance: SubunitBase, owner) -> T | None:
        if instance is None:
            return self

        if CommandType.GET not in self.command_type:
            raise AttributeError(
                f"Function {self.function_name} does not support GET command"
            )

        if handler := instance.function_handlers.get(self.function_name, None):
            return handler.value
        return None

    def __set__(self, instance, value: T):
        if CommandType.PUT not in self.command_type:
            raise AttributeError(
                f"Function {self.function_name} does not support PUT command"
            )
        instance._put(self.function_name, self._value_to_str(value))

    def __delete__(self, instance: SubunitBase):
        # Not entirely sure if this is correct :/
        instance.function_handlers[self.function_name] = None

    def _value_to_str(self, value: T) -> str:
        if self._str_converter:
            return self._str_converter(value)
        if issubclass(self.datatype, Enum):
            return value.value
        return str(value)


class YncaFunctionHandler:
    """
    Keeps a value of a Function and handles conversions form str on updating.
    Note that it is not possible to store the value in the YncaFunction since it
    is a class instance which is shared by all instances.
    """

    def __init__(
        self,
        datatype: Type,
        value_converter: Callable[[str], Any],
    ) -> None:
        self.value = None
        self.datatype = datatype
        self.value_converter = value_converter

    def update(self, value_str: str):
        if self.value_converter:
            self.value = self.value_converter(value_str)
        else:
            self.value = self.datatype(value_str)


class SubunitBase:

    # To be set in subclasses
    id: str = ""

    avail = YncaFunction[Avail]("AVAIL", Avail)

    def __init__(self, connection: YncaConnection):
        """
        Baseclass for Subunits, should be subclassed do not instantiate manually.
        """
        self._update_callbacks: Set[Callable[[], None]] = set()

        self.function_handlers: Dict[str, YncaFunctionHandler] = {}

        # Note that we need to iterate over the _class_
        # otherwise the YncaFunction descriptors get/set functions would trigger.
        # Sort the list to have a deterministic/understandable order for easier testing
        for name in sorted(dir(self.__class__)):
            value = getattr(self.__class__, name)

            if isinstance(value, YncaFunction):
                self.function_handlers[value.function_name] = YncaFunctionHandler(
                    value.datatype, value.value_converter
                )

        self._initialized = False
        self._initialized_event = threading.Event()

        self._connection = connection
        self._connection.register_message_callback(self._protocol_message_received)

        # self.function_mixin_initialize_function_attributes()

    def initialize(self):
        """
        Initializes the data for the subunit and makes sure to wait until done.
        This call can take a long time
        """

        logger.info("Subunit %s initialization start.", self.id)

        self._initialized_event.clear()
        self._initialized = False

        num_commands_sent_start = self._connection.num_commands_sent

        # Request YNCA functions
        for function_name in self.function_handlers.keys():
            self._get(function_name)

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

    def on_message_received_without_handler(
        self, status: YncaProtocolStatus, function_: str, value: str
    ) -> bool:
        """
        Called when a message for this subunit was received with no handler
        Implement in subclasses for cases where the standard handler is not enough.

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

        if handler := self.function_handlers.get(function_, None):
            handler.update(value)
        else:
            updated = self.on_message_received_without_handler(status, function_, value)

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
