from __future__ import annotations

import logging
from abc import ABC
from enum import Enum, Flag, auto
from typing import TYPE_CHECKING, Generic, Type, TypeVar, overload

if TYPE_CHECKING:  # pragma: no cover
    from .subunit import SubunitBase

from .converters import (
    ConverterBase,
    EnumConverter,
    FloatConverter,
    IntConverter,
    MultiConverter,
    StrConverter,
)

logger = logging.getLogger(__name__)


class Cmd(Flag):
    GET = auto()
    PUT = auto()


T = TypeVar("T")
E = TypeVar("E", bound=Enum)


class FunctionBase(ABC, Generic[T]):
    """
    Provides an easy way to specify all properties needed to handle a YNCA function.
    The resulting descriptor makes it easy to just read/write to the attributes and
    values will be read from cache or converted and sent to the device.
    """

    def __init__(
        self,
        name: str,
        converter: ConverterBase,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        init: str | None = None,
        no_initialize: bool = False,
    ) -> None:
        """
        name:
            Name of the function
        converter:
            Converter to use for value to/from str conversions
        cmd:
            Operations the command supports. PUT and/or GET
        init:
            Name of function to use for initialize. Only needed if the function name to initialize is different from the function name itself. E.g. METAINFO for ARTIST, ALBUM and SONG to reduce amount of commands needed
        no_initialize:
            Do not initialize this function, very specific usecase, do _not_ use unless you know what you are doing!
        """
        self.name = name
        self.cmd = cmd
        self.converter = converter
        self.no_initialize = no_initialize
        self.initializer = init

    @overload
    def __get__(self, instance: None, owner) -> FunctionBase[T]:  # pragma: no cover
        ...

    @overload
    def __get__(self, instance: SubunitBase, owner) -> T | None:  # pragma: no cover
        ...

    def __get__(
        self, instance: SubunitBase | None, owner
    ) -> T | None | FunctionBase[T]:
        if instance is None:
            return self

        if Cmd.GET not in self.cmd:
            raise AttributeError(f"Function {self.name} does not support GET command")

        return instance.function_handlers[self.name].value

    def __set__(self, instance, value: T):
        if Cmd.PUT not in self.cmd:
            raise AttributeError(f"Function {self.name} does not support PUT command")
        instance._put(self.name, self.converter.to_str(value))

    def __delete__(self, instance: SubunitBase):  # pragma: no cover
        # Don't think I have use for this
        pass


class EnumFunction(FunctionBase[E], Generic[E]):
    def __init__(
        self,
        name: str,
        datatype: Type[E],
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        init=None,
    ) -> None:
        super().__init__(
            name,
            cmd=cmd,
            converter=EnumConverter[E](datatype),
            init=init,
        )


class StrFunction(FunctionBase[str]):
    def __init__(
        self,
        name: str,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        converter: ConverterBase = StrConverter(),
        init=None,
    ) -> None:
        super().__init__(
            name,
            cmd=cmd,
            converter=converter,
            init=init,
        )


class IntFunction(FunctionBase[int]):
    def __init__(
        self,
        name: str,
        command_type: Cmd = Cmd.GET | Cmd.PUT,
        converter: ConverterBase = IntConverter(),
        init=None,
    ) -> None:
        super().__init__(
            name,
            cmd=command_type,
            converter=converter,
            init=init,
        )


class FloatFunction(FunctionBase[float]):
    def __init__(
        self,
        name: str,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        converter: ConverterBase = FloatConverter(),
        init=None,
    ) -> None:
        super().__init__(
            name,
            cmd=cmd,
            converter=converter,
            init=init,
        )


class EnumOrFloatFunction(FunctionBase, Generic[E]):
    def __init__(
        self,
        name: str,
        datatype: Type[E],
        converter: MultiConverter | None = None,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        init=None,
    ) -> None:
        super().__init__(
            name,
            cmd=cmd,
            converter=converter
            or MultiConverter([EnumConverter[E](datatype), FloatConverter()]),
            init=init,
        )
