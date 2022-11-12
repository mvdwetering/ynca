from __future__ import annotations
from abc import ABC

from enum import Enum, Flag, auto
import logging
import threading
from typing import Any, Callable, Dict, Set, Type, TypeVar, Generic, cast

from .constants import Avail, Subunit
from .errors import YncaInitializationFailedException
from .connection import YncaConnection, YncaProtocol, YncaProtocolStatus

logger = logging.getLogger(__name__)


class CommandType(Flag):
    GET = auto()
    PUT = auto()


T = TypeVar("T")
E = TypeVar("E", bound=Enum)


class Converter(ABC, Generic[T]):
    def to_value(self, value_string: str) -> T:
        raise NotImplementedError("Implement in derived class")

    def to_str(self, value: T) -> str:
        raise NotImplementedError("Implement in derived class")


class EnumConverter(Converter, Generic[E]):
    def __init__(self, datatype: Type[E]) -> None:
        self.datatype = datatype

    def to_value(self, value_string: str) -> E:
        return self.datatype(value_string)

    def to_str(self, value: E) -> str:
        return cast(Enum, value).value


class BoolConverter(Converter):
    def __init__(self, true: str, false: str) -> None:
        self._true_string = true
        self._false_string = false

    def to_value(self, value_string: str) -> bool:
        return True if value_string == self._true_string else False

    def to_str(self, value: bool) -> str:
        return self._true_string if value else self._false_string


class IntConverter(Converter):
    def __init__(self, to_str: Callable[[int], str] | None = None) -> None:
        self._to_str = to_str

    def to_value(self, value_string: str) -> int:
        return int(value_string)

    def to_str(self, value: int) -> str:
        if self._to_str:
            return self._to_str(value)
        return str(value)


class FloatConverter(Converter):
    def __init__(self, to_str: Callable[[float], str] | None = None) -> None:
        self._to_str = to_str

    def to_value(self, value_string: str) -> float:
        return float(value_string)

    def to_str(self, value: float) -> str:
        if self._to_str:
            return self._to_str(value)
        return str(value)


class StrConverter(Converter):
    def __init__(self, min_len: int | None = None, max_len: int | None = None) -> None:
        self._min_len = min_len
        self._max_len = max_len

    def to_value(self, value_string: str) -> str:
        return value_string

    def to_str(self, value: str) -> str:
        if self._min_len and len(value) < self._min_len:
            raise ValueError(f"{value} has a minimum length of {self._min_len}")
        if self._max_len and len(value) > self._max_len:
            raise ValueError(f"{value} has a maxmimum length of {self._max_len}")
        return value


class YncaFunctionBase(ABC, Generic[T]):
    """
    Provides an easy way to specify all properties needed to handle a YNCA function.
    The resulting descriptor makes it easy to just read/write to the attributes and
    values will be read from cache or converted and sent to the device.
    """

    def __init__(
        self,
        function_name: str,
        converter: Converter,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        no_initialize: bool = False,
    ) -> None:
        self.function_name = function_name
        self.command_type = command_type
        self.converter = converter
        self.no_initialize = no_initialize

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
        instance._put(self.function_name, self.converter.to_str(value))

    def __delete__(self, instance: SubunitBase):
        # Don't think I have use for this
        pass


class YncaFunctionEnum(YncaFunctionBase, Generic[E]):
    def __init__(
        self,
        function_name: str,
        datatype: Type[E],
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        no_initialize: bool = False,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=EnumConverter[E](datatype),
            no_initialize=no_initialize,
        )


class YncaFunctionStr(YncaFunctionBase):
    def __init__(
        self,
        function_name: str,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        converter: StrConverter = StrConverter(),
        no_initialize: bool = False,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=converter,
            no_initialize=no_initialize,
        )


class YncaFunctionInt(YncaFunctionBase):
    def __init__(
        self,
        function_name: str,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        converter: Converter = IntConverter(),
        no_initialize: bool = False,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=converter,
            no_initialize=no_initialize,
        )


class YncaFunctionFloat(YncaFunctionBase):
    def __init__(
        self,
        function_name: str,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        converter: Converter = FloatConverter(),
        no_initialize: bool = False,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=converter,
            no_initialize=no_initialize,
        )


class YncaFunctionBool(YncaFunctionBase):
    def __init__(
        self,
        function_name: str,
        true: str,
        false: str,
        command_type=CommandType.GET | CommandType.PUT,
        no_initialize: bool = False,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=BoolConverter(true, false),
            no_initialize=no_initialize,
        )


class YncaFunctionHandler:
    """
    Keeps a value of a Function and handles conversions from str on updating.
    Note that it is not possible to store the value in the YncaFunction since it
    is a class instance which is shared by all instances.
    """

    def __init__(
        self,
        converter: Converter,
        no_initialize: bool,
    ) -> None:
        self.value = None
        self.converter = converter
        self.no_initialize = no_initialize

    def update(self, value_str: str):
        self.value = self.converter.to_value(value_str)


# TODO: Look at ABC (AbstractBaseClass)
class SubunitBase:

    # To be set in subclasses
    id: str = ""

    avail = YncaFunctionEnum[Avail]("AVAIL", Avail)

    def __init__(self, connection: YncaConnection) -> None:
        """
        Baseclass for Subunits, should be subclassed do not instantiate manually.
        """
        self._update_callbacks: Set[Callable[[str, str], None]] = set()

        self.function_handlers: Dict[str, YncaFunctionHandler] = {}

        # Note that we need to iterate over the _class_
        # otherwise the YncaFunction descriptors get/set functions would trigger.
        # Sort the list to have a deterministic/understandable order for easier testing
        for name in sorted(dir(self.__class__)):
            value = getattr(self.__class__, name)

            if isinstance(value, YncaFunctionBase):
                self.function_handlers[value.function_name] = YncaFunctionHandler(
                    value.converter, value.no_initialize
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
        for function_name, handler in self.function_handlers.items():
            if not handler.no_initialize:
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
        self, status: YncaProtocolStatus, function_name: str, value: str
    ) -> bool:
        """
        Called when a message for this subunit was received with no handler
        Implement in subclasses for cases where the standard handler is not enough.

        Return True if state was updated because of the message.
        """
        return False

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_name: str, value: str
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

        updated = False

        if handler := self.function_handlers.get(function_name, None):
            handler.update(value)
            updated = True
        else:
            updated = self.on_message_received_without_handler(
                status, function_name, value
            )

        if updated:
            self._call_registered_update_callbacks(function_name, value)

    def _put(self, function_name: str, value: str):
        self._connection.put(self.id, function_name, value)

    def _get(self, function_name: str):
        self._connection.get(self.id, function_name)

    def register_update_callback(self, callback: Callable[[str, str], None]):
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[str, str], None]):
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self, function_name: str, value: str):
        if self._initialized:
            for callback in self._update_callbacks:
                callback(function_name, value)
