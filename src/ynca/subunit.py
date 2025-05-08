from __future__ import annotations

from abc import ABC
from enum import Flag, auto
import logging
import threading
from typing import TYPE_CHECKING, Any, Protocol

from .connection import YncaConnection, YncaProtocol, YncaProtocolStatus
from .constants import Subunit
from .enums import Avail
from .errors import YncaInitializationFailedException
from .function import Cmd, EnumFunctionMixin, FunctionMixinBase

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class CommandType(Flag):
    GET = auto()
    PUT = auto()


class YncaFunctionHandler:
    """YNCA Function Handler.

    Keeps a value of a Function and handles conversions from str on updating.
    Note that it is not possible to store the value in the YncaFunction since it
    is a class instance which is shared by all instances.
    """

    def __init__(
        self,
        function: FunctionMixinBase,
    ) -> None:
        self.value = None
        self.function = function

    def update(self, value_str: str) -> None:
        self.value = self.function.converter.to_value(value_str)


class SubunitBaseMixinProtocol(Protocol):  # pragma: no cover
    """Describes the available methods and attributes that Mixins can use to interact with a SubunitBase instance. This helps out with typing."""

    def _put(self, function_name: str, value: str) -> None:
        pass


class SubunitBase(ABC):
    """Baseclass for Subunits, should be subclassed do not instantiate manually."""

    id: Subunit  # Just typed, needs to be set in subclasses

    avail = EnumFunctionMixin[Avail](Avail, Cmd.GET)

    def __init__(self, connection: YncaConnection) -> None:
        self._update_callbacks: set[Callable[[str, Any], None]] = set()

        self.function_handlers: dict[str, YncaFunctionHandler] = {}

        # Note that we need to iterate over the _class_
        # otherwise the YncaFunction descriptors get/set functions would trigger.
        # Sort the list to have a deterministic/understandable order for easier testing
        for attribute_name in sorted(dir(self.__class__)):
            attribute = getattr(self.__class__, attribute_name, None)
            if isinstance(attribute, FunctionMixinBase):
                self.function_handlers[attribute.name] = YncaFunctionHandler(attribute)

        self._initialized = False
        self._initialized_event = threading.Event()

        self._connection = connection
        self._connection.register_message_callback(self._protocol_message_received)

    def initialize(self) -> None:
        """Initialize the data for the subunit and makes sure to wait until done. This call can take a long time."""
        if not self._connection:  # pragma: no cover
            msg = "No valid connection"
            raise YncaInitializationFailedException(msg)

        logger.info("Subunit %s initialization begin.", self.id)

        self._initialized_event.clear()
        self._initialized = False

        num_commands_sent_start = self._connection.num_commands_sent

        # Setup YNCA function handlers
        initialized_function_names = []
        for function_name, handler in self.function_handlers.items():
            if not handler.function.no_initialize:
                function_initializer_name = (
                    handler.function.initializer
                    if handler.function.initializer is not None
                    else function_name
                )
                if function_initializer_name not in initialized_function_names:
                    self._get(function_initializer_name)
                    initialized_function_names.append(function_initializer_name)

        # Use SYS:VERSION as a sync since it is available on all receivers
        self._connection.get(Subunit.SYS, "VERSION")

        # Take command spacing into account and apply large margin
        # Large margin is needed in practice on slower/busier systems
        num_commands_sent = self._connection.num_commands_sent - num_commands_sent_start
        if self._initialized_event.wait(
            2 + num_commands_sent * (YncaProtocol.COMMAND_SPACING * 5)
        ):
            self._initialized = True
        else:
            msg = f"Subunit {self.id} initialization failed"
            raise YncaInitializationFailedException(msg)

        logger.info("Subunit %s initialization end.", self.id)

    def close(self) -> None:
        if self._connection:
            self._connection.unregister_message_callback(
                self._protocol_message_received
            )
            self._update_callbacks = set()

    def _protocol_message_received(
        self,
        status: YncaProtocolStatus,
        subunit: str | None,
        function_name: str | None,
        value_str: str | None,
    ) -> None:
        if status is not YncaProtocolStatus.OK:
            # Can't really handle errors since at this point we can't see to what command it belonged
            return

        # During initialization SYS:VERSION is used to signal that initialization is done
        if (
            not self._initialized
            and subunit == Subunit.SYS
            and function_name == "VERSION"
        ):
            self._initialized_event.set()

        if self.id != subunit:
            return

        if (
            function_name is not None
            and value_str is not None
            and (handler := self.function_handlers.get(function_name, None))
        ):
            handler.update(value_str)
            self._call_registered_update_callbacks(function_name, handler.value)

    def _put(self, function_name: str, value: str) -> None:
        if self._connection:
            self._connection.put(self.id, function_name, value)

    def _get(self, function_name: str) -> None:
        if self._connection:
            self._connection.get(self.id, function_name)

    def register_update_callback(self, callback: Callable[[str, Any], None]) -> None:
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[str, Any], None]) -> None:
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self, function_name: str, value: Any) -> None:
        if self._initialized:
            for callback in self._update_callbacks:
                callback(function_name, value)
