from unittest import mock
import pytest

import ynca

from ynca.system import System
from ynca.zone import Zone
from ynca.errors import YncaInitializationFailedException

from .connectionmock import YncaConnectionMock

SYS = "SYS"
MAIN = "MAIN"
ZONE4 = "ZONE4"
NETRADIO = "NETRADIO"
BT = "BT"

RESTRICTED = "@RESTRICTED"

INITIALIZE_MINIMAL_RESPONSES = [
    # Receiver detect subunits sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
    # SYS Subunit initialize sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
]


INITIALIZE_FULL_RESPONSES = [
    (
        (MAIN, "AVAIL"),
        [
            (MAIN, "AVAIL", "Not Ready"),
        ],
    ),
    (
        (ZONE4, "AVAIL"),
        [
            (RESTRICTED, None, None),
        ],
    ),
    (
        (BT, "AVAIL"),
        [
            (BT, "AVAIL", "Not Connected"),
        ],
    ),
    (
        (NETRADIO, "AVAIL"),
        [
            (NETRADIO, "AVAIL", "Not Ready"),
        ],
    ),
    # Receiver detect subunits sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
    (
        (SYS, "MODELNAME"),
        [
            (SYS, "MODELNAME", "ModelName"),
        ],
    ),
    (
        (SYS, "PWR"),
        [
            (SYS, "PWR", "Standby"),
        ],
    ),
    (
        (SYS, "INPNAME"),
        [
            (SYS, "INPNAMEONE", "InputOne"),
            (SYS, "INPNAMETWO", "InputTwo"),
        ],
    ),
    # SYS Subunit iniatilize sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
    (
        (MAIN, "ZONENAME"),
        [
            (MAIN, "ZONENAME", "MainZoneName"),
        ],
    ),
    # MAIN Subunit iniatilize sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
]


@pytest.fixture
def connection():
    c = YncaConnectionMock()
    c.setup_responses()
    return c


def test_construct():

    r = ynca.Receiver("serial_url")
    assert len(r.subunits.keys()) == 0
    assert len(r.inputs.keys()) == 0

    r.close()


def test_initialize_minimal(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        disconnect_callback = mock.MagicMock()

        r = ynca.Receiver("serial_url", disconnect_callback)
        r.initialize()

        assert len(r.inputs.keys()) == 0

        assert len(r.subunits.keys()) == 1
        assert isinstance(r.subunits[SYS], System)
        assert r.subunits[SYS].version == "Version"

        r.close()

        disconnect_callback.assert_not_called()


def test_initialize_fail(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = []

        disconnect_callback = mock.MagicMock()

        r = ynca.Receiver("serial_url", disconnect_callback)
        with pytest.raises(YncaInitializationFailedException):
            r.initialize()

        disconnect_callback.assert_not_called()


def test_disconnect_callback(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        disconnect_callback = mock.MagicMock()

        r = ynca.Receiver("serial_url", disconnect_callback)
        r.initialize()

        # Report disconnect from connection by using callback registered in connect call
        connection.connect.call_args.args[0]()
        disconnect_callback.assert_called_once()

        r.close()


def test_initialize_full(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection

        connection.get_response_list = INITIALIZE_FULL_RESPONSES

        r = ynca.Receiver("serial_url")
        r.initialize()

        assert len(r.inputs.keys()) == 4
        assert r.inputs["ONE"] == "InputOne"
        assert r.inputs["TWO"] == "InputTwo"
        assert r.inputs["NET RADIO"] == "NET RADIO"
        assert r.inputs["Bluetooth"] == "Bluetooth"

        assert len(r.subunits.keys()) == 2

        assert isinstance(r.subunits[SYS], System)
        assert r.subunits[SYS].model_name == "ModelName"
        assert r.subunits[SYS].version == "Version"

        assert isinstance(r.subunits[MAIN], Zone)
        assert r.subunits[MAIN].name == "MainZoneName"

        r.close()