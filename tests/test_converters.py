"""Test Zone subunit"""

from enum import Enum

import pytest

from ynca.converters import (
    EnumConverter,
    FloatConverter,
    IntConverter,
    MultiConverter,
    StrConverter,
)


def test_strconverter():
    c = StrConverter(min_len=3, max_len=6)
    assert c.to_str("123") == "123"
    assert c.to_str("123456") == "123456"
    with pytest.raises(ValueError):
        c.to_str("12")
    with pytest.raises(ValueError):
        c.to_str("1234567")

    assert c.to_value("test") == "test"


def test_intconverter():
    c = IntConverter()
    assert c.to_str(123) == "123"
    assert c.to_value("123") == 123

    c = IntConverter(to_str=lambda v: str(v * 2))
    assert c.to_str(123) == "246"
    assert c.to_value("123") == 123


def test_floatconverter():
    c = FloatConverter()
    assert c.to_str(1.23) == "1.23"
    assert c.to_value("1.23") == 1.23

    c = FloatConverter(to_str=lambda v: str(v * 2))
    assert c.to_str(1.23) == "2.46"
    assert c.to_value("1.23") == 1.23


def test_enumconverter():
    class TestEnum(Enum):
        ONE = "One"
        TWO = "Two"

    c = EnumConverter(TestEnum)
    assert c.to_str(TestEnum.ONE) == "One"
    assert c.to_value("Two") == TestEnum.TWO


def test_multiconverter():
    class TestEnum(Enum):
        ONE = "One"
        TWO = "Two"

    c = MultiConverter(
        [EnumConverter[TestEnum](TestEnum), FloatConverter(to_str=lambda v: str(v * 2))]
    )
    assert c.to_str(TestEnum.ONE) == "One"
    assert c.to_str(1.23) == "2.46"
    with pytest.raises(ValueError):
        c.to_str("Invalid")

    assert c.to_value("Two") == TestEnum.TWO
    assert c.to_value("1.23") == 1.23
    with pytest.raises(ValueError):
        c.to_value("Invalid")
