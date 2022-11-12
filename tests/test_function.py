"""Test Zone subunit"""


import pytest

from ynca.function import (
    Cmd,
    StrFunction,
)
from ynca.subunit import SubunitBase

SUBUNIT = "TESTSUBUNIT"


class DummySubunit(SubunitBase):
    id = SUBUNIT

    function_put = StrFunction("FUNCTION_PUT", cmd=Cmd.PUT)
    function_get = StrFunction("FUNCTION_GET", cmd=Cmd.GET)


def test_yncafunctionstr(connection):
    subunit = DummySubunit(connection)

    subunit.function_put = "value"
    connection.put.assert_called_with(SUBUNIT, "FUNCTION_PUT", "value")
    with pytest.raises(AttributeError):
        value = subunit.function_put

    assert subunit.function_get is None
    with pytest.raises(AttributeError):
        subunit.function_get = "value"
