from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Generic, List, Type, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")
E = TypeVar("E", bound=Enum)


class ConverterBase(ABC, Generic[T]):
    @abstractmethod
    def to_value(self, value_string: str) -> T:  # pragma: no cover
        pass

    @abstractmethod
    def to_str(self, value: T) -> str:  # pragma: no cover
        pass


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
        # Make sure it is an int compatible types to be usable with MultiConverter
        int(value)

        if self._to_str:
            return str(self._to_str(value))
        return str(value)


class FloatConverter(ConverterBase):
    def __init__(self, to_str: Callable[[float], str] | None = None) -> None:
        self._to_str = to_str

    def to_value(self, value_string: str) -> float:
        return float(value_string)

    def to_str(self, value: float) -> str:
        # Make sure it is a float compatible types to be usable with MultiConverter
        float(value)

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
        # Make sure it is a str compatible types to be usable with MultiConverter
        str(value)

        if self._min_len and len(value) < self._min_len:
            raise ValueError(f"{value} has a minimum length of {self._min_len}")
        if self._max_len and len(value) > self._max_len:
            raise ValueError(f"{value} has a maxmimum length of {self._max_len}")
        return value


class MultiConverter(ConverterBase):
    """
    Multiconverter allows to try multiple converters.
    This is sometimes needed as value can be a number or enum.
    MultiConverter will go through the converters in oreder and the first result will be used.
    Errors have to be indicated by the converters by throwing an exception (any exception is fine).
    """

    def __init__(self, converters: List[ConverterBase]) -> None:
        self._converters = converters

    def to_value(self, value_string: str) -> Any:
        for converter in self._converters:
            try:
                return converter.to_value(value_string)
            except:
                pass
        raise ValueError(f"No converter could convert '{value_string}' to value")

    def to_str(self, value: Any) -> str:
        for converter in self._converters:
            try:
                return converter.to_str(value)
            except:
                pass
        raise ValueError(f"No converter could convert {value} to string")
