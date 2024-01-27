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


class FunctionMixinBase(ABC, Generic[T]):
    """
    Provides an easy way to specify all properties needed to handle a YNCA function.

    The resulting descriptor makes it easy to just read/write to the attributes and
    values will be read from cache or converted and sent to the device.

    The function mixins have to be used/mixedin with SubunitBase subclasses to work
    """

    def __init__(
        self,
        converter: ConverterBase,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        name_override: str | None = None,
        init: str | None = None,
        no_initialize: bool = False,
    ) -> None:
        """
        converter:
            Converter to use for value to/from str conversions
        cmd:
            Operations the command supports. PUT and/or GET
        name_override:
            Optional name_override useful in case where function name can not be a valid Python attribute name e.g. 2CHDECODER
        init:
            Name of function to use for initialize. Only needed if the function name to initialize is different from the function name itself. E.g. METAINFO for ARTIST, ALBUM and SONG to reduce amount of commands needed
        no_initialize:
            Do not initialize this function, very specific usecase, do _not_ use unless you know what you are doing!
        """
        self.converter = converter
        self.cmd = cmd
        self.initializer = init
        self.no_initialize = no_initialize

        # Name will be set in __set_name__, provide typehint to help the linter
        self.name: str
        self._name_override = name_override

    @overload
    def __get__(self, instance: None, owner) -> FunctionMixinBase[T]:  # pragma: no cover
        ...

    @overload
    def __get__(self, instance: SubunitBase, owner) -> T | None:  # pragma: no cover
        ...

    def __get__(
        self, instance: SubunitBase | None, owner
    ) -> T | None | FunctionMixinBase[T]:
        if instance is None:
            return self

        if Cmd.GET not in self.cmd:
            raise AttributeError(f"Function {self.name} does not support GET command")

        return instance.function_handlers[self.name].value

    def __set__(self, instance, value: T):
        if Cmd.PUT not in self.cmd:
            raise AttributeError(f"Function {self.name} does not support PUT command")
        instance._put(self.name, self.converter.to_str(value))

    def __delete__(self, instance: SubunitBase):
        del instance.function_handlers[self.name]

    def __set_name__(self, owner, name):
        self.name = name.upper() if not self._name_override else self._name_override


class EnumFunctionMixin(FunctionMixinBase[E], Generic[E]):
    def __init__(
        self,
        datatype: Type[E],
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        name_override: str | None = None,
        init=None,
    ) -> None:
        super().__init__(
            name_override=name_override,
            cmd=cmd,
            converter=EnumConverter[E](datatype),
            init=init,
        )


class StrFunctionMixin(FunctionMixinBase[str]):
    def __init__(
        self,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        converter: ConverterBase = StrConverter(),
        name_override: str | None = None,
        init=None,
    ) -> None:
        super().__init__(
            name_override=name_override,
            cmd=cmd,
            converter=converter,
            init=init,
        )


class IntFunctionMixin(FunctionMixinBase[int]):
    def __init__(
        self,
        command_type: Cmd = Cmd.GET | Cmd.PUT,
        converter: ConverterBase = IntConverter(),
        name_override: str | None = None,
        init=None,
    ) -> None:
        super().__init__(
            name_override=name_override,
            cmd=command_type,
            converter=converter,
            init=init,
        )


class FloatFunctionMixin(FunctionMixinBase[float]):
    def __init__(
        self,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        converter: ConverterBase = FloatConverter(),
        name_override: str | None = None,
        init=None,
    ) -> None:
        super().__init__(
            name_override=name_override,
            cmd=cmd,
            converter=converter,
            init=init,
        )


class EnumOrFloatFunctionMixin(FunctionMixinBase, Generic[E]):
    def __init__(
        self,
        datatype: Type[E],
        converter: MultiConverter | None = None,
        cmd: Cmd = Cmd.GET | Cmd.PUT,
        name_override: str | None = None,
        init=None,
    ) -> None:
        super().__init__(
            name_override=name_override,
            cmd=cmd,
            converter=converter
            or MultiConverter([EnumConverter[E](datatype), FloatConverter()]),
            init=init,
        )
