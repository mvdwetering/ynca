"""Test Zone subunit"""

from enum import Enum
from unittest import mock

import pytest

from ynca.ynca_function import (
    CommandType,
    YncaFunctionEnum,
    YncaFunctionFloat,
    YncaFunctionInt,
    YncaFunctionStr,
)
from ynca.subunit import SubunitBase

SUBUNIT = "TESTSUBUNIT"


class DummySubunit(SubunitBase):
    id = SUBUNIT

    function_put = YncaFunctionStr("FUNCTION_PUT", command_type=CommandType.PUT)
    function_get = YncaFunctionStr("FUNCTION_GET", command_type=CommandType.GET)
    # band = YncaFunctionEnum[Band]("BAND", Band)


def test_yncafunctionstr(connection):
    subunit = DummySubunit(connection)

    subunit.function_put = "value"
    connection.put.assert_called_with(SUBUNIT, "FUNCTION_PUT", "value")
    with pytest.raises(AttributeError):
        value = subunit.function_put

    assert subunit.function_get is None
    with pytest.raises(AttributeError):
        subunit.function_get = "value"
