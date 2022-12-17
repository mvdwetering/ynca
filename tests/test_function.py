"""Test function"""


import pytest

from ynca.enums import Avail, PartyMute
from ynca.subunits.system import System

SUBUNIT = "SYS"


def test_yncafunction_put_only(connection):
    subunit = System(connection)

    subunit.partymute = PartyMute.OFF
    connection.put.assert_called_with(SUBUNIT, "PARTYMUTE", "Off")
    with pytest.raises(AttributeError):
        value = subunit.partymute


def test_yncafunction_get_only(connection):
    subunit = System(connection)

    assert subunit.avail is None
    with pytest.raises(AttributeError):
        subunit.avail = Avail.NOT_CONNECTED
