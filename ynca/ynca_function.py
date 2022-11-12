from __future__ import annotations

import logging
from abc import ABC
from enum import Enum, Flag, auto
from typing import TYPE_CHECKING, Generic, Type, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from .subunit import SubunitBase

from .converters import (
    ConverterBase,
    EnumConverter,
    FloatConverter,
    IntConverter,
    StrConverter,
)

logger = logging.getLogger(__name__)


class CommandType(Flag):
    GET = auto()
    PUT = auto()


T = TypeVar("T")
E = TypeVar("E", bound=Enum)


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

    def __get__(self, instance: SubunitBase, owner) -> T | None | YncaFunctionBase[T]:
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

    def __delete__(self, instance: SubunitBase):  # pragma: no cover
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
        converter: ConverterBase = StrConverter(),
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
