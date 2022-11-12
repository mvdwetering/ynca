from __future__ import annotations
from abc import ABC, abstractmethod

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


class ConverterBase(ABC, Generic[T]):
    @abstractmethod
    def to_value(self, value_string: str) -> T:
        raise NotImplementedError("Implement in derived class")

    @abstractmethod
    def to_str(self, value: T) -> str:
        raise NotImplementedError("Implement in derived class")


class EnumConverter(ConverterBase, Generic[E]):
    def __init__(self, datatype: Type[E]) -> None:
        self.datatype = datatype

    def to_value(self, value_string: str) -> E:
        return self.datatype(value_string)

    def to_str(self, value: E) -> str:
        return cast(Enum, value).value


class IntConverter(ConverterBase):
    def __init__(self, to_str: Callable[[int], str] | None = None) -> None:
        self._to_str = to_str

    def to_value(self, value_string: str) -> int:
        return int(value_string)

    def to_str(self, value: int) -> str:
        if self._to_str:
            return self._to_str(value)
        return str(value)


class FloatConverter(ConverterBase):
    def __init__(self, to_str: Callable[[float], str] | None = None) -> None:
        self._to_str = to_str

    def to_value(self, value_string: str) -> float:
        return float(value_string)

    def to_str(self, value: float) -> str:
        if self._to_str:
            return self._to_str(value)
        return str(value)


class StrConverter(ConverterBase):
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
        converter: ConverterBase,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        initialize_function_name: str | None = None,
        no_initialize: bool = False,
    ) -> None:
        """
        function_name:
            Name of the function
        converter:
            Converter to use for value to/from str conversions
        command_type:
            Operations the command supports. PUT and/or GET
        initialize_function_name:
            Set this if the name to initialize this function is different from the function name itself. E.g. METAINFO for artist, album and song to reduce amount of commands needed
        no_initialize:
            Do not initialize this function, very specific usecase, do _not_ use unless you know what you are doing
        """
        self.function_name = function_name
        self.command_type = command_type
        self.converter = converter
        self.no_initialize = no_initialize
        self.initialize_function_name = initialize_function_name

    def __get__(self, instance: SubunitBase, owner) -> T | None:
        if instance is None:
            return self

        if CommandType.GET not in self.command_type:
            raise AttributeError(
                f"Function {self.function_name} does not support GET command"
            )

        return instance.function_handlers[self.function_name].value

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
        initialize_function_name=None,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=EnumConverter[E](datatype),
            no_initialize=no_initialize,
            initialize_function_name=initialize_function_name,
        )


class YncaFunctionStr(YncaFunctionBase):
    def __init__(
        self,
        function_name: str,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        converter: StrConverter = StrConverter(),
        no_initialize: bool = False,
        initialize_function_name=None,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=converter,
            no_initialize=no_initialize,
            initialize_function_name=initialize_function_name,
        )


class YncaFunctionInt(YncaFunctionBase):
    def __init__(
        self,
        function_name: str,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        converter: ConverterBase = IntConverter(),
        no_initialize: bool = False,
        initialize_function_name=None,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=converter,
            no_initialize=no_initialize,
            initialize_function_name=initialize_function_name,
        )


class YncaFunctionFloat(YncaFunctionBase):
    def __init__(
        self,
        function_name: str,
        command_type: CommandType = CommandType.GET | CommandType.PUT,
        converter: ConverterBase = FloatConverter(),
        no_initialize: bool = False,
        initialize_function_name=None,
    ) -> None:
        super().__init__(
            function_name,
            command_type=command_type,
            converter=converter,
            no_initialize=no_initialize,
            initialize_function_name=initialize_function_name,
        )


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

    # To be set in subclasses
    id: str = ""

    avail = YncaFunctionEnum[Avail]("AVAIL", Avail)

    def __init__(self, connection: YncaConnection) -> None:
        """
        Baseclass for Subunits, should be subclassed do not instantiate manually.
        """
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

        updated = False

        if handler := self.function_handlers.get(function_name, None):
            handler.update(value_str)
            self._call_registered_update_callbacks(function_name, handler.value)
        else:
            self.on_message_received_without_handler(status, function_name, value_str)
            logger.warning("Update callback _not_ called for '%s'" % function_name)
            # TODO: Can probably get rid of the "without" handler after completing rework

        # if updated:
        #     self._call_registered_update_callbacks(
        #         function_name, value_str
        #     )

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
