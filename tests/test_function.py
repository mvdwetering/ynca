"""Test function."""

import pytest

from tests.mock_yncaconnection import YncaConnectionMock
from ynca.enums import PartyMute
from ynca.subunits.system import System

SUBUNIT = "SYS"


def test_yncafunction_put_only(connection: YncaConnectionMock) -> None:
    subunit = System(connection)

    subunit.partymute = PartyMute.OFF
    connection.put.assert_called_with(SUBUNIT, "PARTYMUTE", "Off")

    with pytest.raises(AttributeError):
        value = subunit.partymute  # noqa: F841


def test_yncafunction_get_only(connection: YncaConnectionMock) -> None:
    subunit = System(connection)

    subunit.function_handlers["MODELNAME"].value = "TEST VALUE"
    assert subunit.modelname == "TEST VALUE"

    with pytest.raises(AttributeError):
        subunit.modelname = "NEW NAME"


def test_yncafunction_delete(connection: YncaConnectionMock) -> None:
    subunit = System(connection)

    assert "MODELNAME" in subunit.function_handlers
    delattr(subunit, "modelname")
    assert "MODELNAME" not in subunit.function_handlers
