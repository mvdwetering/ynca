from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
import logging
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")
E = TypeVar("E", bound=Enum)


class ConverterBase(ABC, Generic[T]):
    """Base class for converters. Note that converters should be stateless."""

    @abstractmethod
    def to_value(self, value_string: str) -> T:  # pragma: no cover
        pass

    @abstractmethod
    def to_str(self, value: T) -> str:  # pragma: no cover
        pass


class EnumConverter(ConverterBase, Generic[E]):
    def __init__(self, datatype: type[E]) -> None:
        self.datatype = datatype

    def to_value(self, value_string: str) -> E:
        return self.datatype(value_string)

    def to_str(self, value: E) -> str:
        return cast(Enum, value).value


class IntConverter(ConverterBase):
    def __init__(self, to_str: Callable[[int], str] | None = None) -> None:
        self._to_str = to_str or str

    def to_value(self, value_string: str) -> int:
        return int(value_string)

    def to_str(self, value: int) -> str:
        # Make sure it is an int compatible types to be usable with MultiConverter
        int(value)
        return self._to_str(value)


class IntOrNoneConverter(ConverterBase):
    def __init__(self, to_str: Callable[[int], str] | None = None) -> None:
        self._to_str = to_str or str

    def to_value(self, value_string: str) -> int | None:
        try:
            return int(value_string)
        except ValueError:
            return None

    def to_str(self, value: int) -> str:
        # Make sure it is an int compatible types to be usable with MultiConverter
        int(value)
        return self._to_str(value)


class FloatConverter(ConverterBase):
    def __init__(self, to_str: Callable[[float], str] | None = None) -> None:
        self._to_str = to_str or str

    def to_value(self, value_string: str) -> float:
        return float(value_string)

    def to_str(self, value: float) -> str:
        # Make sure it is a float compatible types to be usable with MultiConverter
        float(value)
        return self._to_str(value)


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
            msg = f"'{value}' is too short, minimum length is {self._min_len}"
            raise ValueError(msg)
        if self._max_len and len(value) > self._max_len:
            msg = f"'{value}' is too long, maximum length is {self._max_len}"
            raise ValueError(msg)
        return value


class TimedeltaOrNoneConverter(ConverterBase):
    def to_value(self, value_string: str) -> timedelta | None:
        try:
            minutes, seconds = map(int, value_string.split(":"))
            return timedelta(minutes=minutes, seconds=seconds)
        except (ValueError, TypeError, OverflowError):
            return None

    def to_str(self, value: timedelta | None) -> str:
        if value is None:
            return ""

        total_seconds = int(value.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"


class MultiConverter(ConverterBase):
    """Multiconverter allows to try multiple converters.

    This is sometimes needed as value can be a number or enum.
    MultiConverter will go through the converters in order and the first result will be used.
    Errors have to be indicated by the converters by throwing an exception (any exception is fine).
    """

    def __init__(self, converters: list[ConverterBase]) -> None:
        self._converters = converters

    def to_value(self, value_string: str) -> Any:
        for converter in self._converters:
            try:
                return converter.to_value(value_string)
            except:  # noqa: E722, S110
                pass
        msg = f"No converter could convert '{value_string}' to value"
        raise ValueError(msg)

    def to_str(self, value: Any) -> str:
        for converter in self._converters:
            try:
                return converter.to_str(value)
            except:  # noqa: E722, S110
                pass
        msg = f"No converter could convert '{value}' to string"
        raise ValueError(msg)
