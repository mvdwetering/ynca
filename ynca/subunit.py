from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from enum import Enum, Flag, auto
from typing import Any, Callable, Dict, Set, TypeVar

from ynca.ynca_function import YncaFunctionBase, YncaFunctionEnum

from .connection import YncaConnection, YncaProtocol, YncaProtocolStatus
from .constants import Avail, Subunit
from .errors import YncaInitializationFailedException

logger = logging.getLogger(__name__)


class CommandType(Flag):
    GET = auto()
    PUT = auto()


T = TypeVar("T")
E = TypeVar("E", bound=Enum)


class YncaFunctionHandler:
    """
    Keeps a value of a Function and handles conversions from str on updating.
    Note that it is not possible to store the value in the YncaFunction since it
    is a class instance which is shared by all instances.
    """

    def __init__(
        self,
        function: YncaFunctionBase,
    ) -> None:
        self.value = None
        self.function = function

    def update(self, value_str: str):
        self.value = self.function.converter.to_value(value_str)


class SubunitBase(ABC):
    """
    Baseclass for Subunits, should be subclassed do not instantiate manually.
    """

    avail = YncaFunctionEnum[Avail]("AVAIL", Avail)

    @property
    @abstractmethod
    def id(self) -> str:  # pragma: no cover
        # Force subunits to set the ID
        pass

    def __init__(self, connection: YncaConnection) -> None:
        self._update_callbacks: Set[Callable[[str, Any], None]] = set()

        self.function_handlers: Dict[str, YncaFunctionHandler] = {}

        # Note that we need to iterate over the _class_
        # otherwise the YncaFunction descriptors get/set functions would trigger.
        # Sort the list to have a deterministic/understandable order for easier testing
        for attribute_name in sorted(dir(self.__class__)):
            attribute = getattr(self.__class__, attribute_name)
            if isinstance(attribute, YncaFunctionBase):
                self.function_handlers[attribute.function_name] = YncaFunctionHandler(
                    attribute
                )

        self._initialized = False
        self._initialized_event = threading.Event()

        self._connection = connection
        self._connection.register_message_callback(self._protocol_message_received)

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
        initialized_function_names = []
        for function_name, handler in self.function_handlers.items():
            if not handler.function.no_initialize:
                function_name = (
                    handler.function.initialize_function_name
                    if handler.function.initialize_function_name is not None
                    else function_name
                )
                if function_name not in initialized_function_names:
                    self._get(function_name)
                    initialized_function_names.append(function_name)

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

        logger.info("Subunit %s initialization done.", self.id)

    def close(self):
        if self._connection:
            self._connection.unregister_message_callback(
                self._protocol_message_received
            )
            self._connection = None
            self._update_callbacks = set()

    def _protocol_message_received(
        self,
        status: YncaProtocolStatus,
        subunit: str,
        function_name: str,
        value_str: str,
    ):
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

        if handler := self.function_handlers.get(function_name, None):
            handler.update(value_str)
            self._call_registered_update_callbacks(function_name, handler.value)

    def _put(self, function_name: str, value: str):
        self._connection.put(self.id, function_name, value)

    def _get(self, function_name: str):
        self._connection.get(self.id, function_name)

    def register_update_callback(self, callback: Callable[[str, Any], None]):
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[str, Any], None]):
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self, function_name: str, value: Any):
        if self._initialized:
            for callback in self._update_callbacks:
                callback(function_name, value)
