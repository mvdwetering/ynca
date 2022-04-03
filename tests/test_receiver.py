from unittest import mock

import pytest
import ynca
from ynca.bt import Bt
from ynca.errors import YncaConnectionError, YncaInitializationFailedException
from ynca.system import System
from ynca.zone import Main

SYS = "SYS"
MAIN = "MAIN"
ZONE4 = "ZONE4"
BT = "BT"

RESTRICTED = "@RESTRICTED"

CONNECTION_CHECK_RESPONSES = [
    (
        (SYS, "MODELNAME"),
        [
            (SYS, "MODELNAME", "ModelName"),
        ],
    ),
]

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
        (SYS, "AVAIL"),
        [
            (RESTRICTED, None, None),
        ],
    ),
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
    # Receiver detect subunits sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
    # SYS Subunit init start
    (
        (SYS, "AVAIL"),
        [
            (RESTRICTED, None, None),
        ],
    ),
    (
        (SYS, "PWR"),
        [
            (SYS, "PWR", "Standby"),
        ],
    ),
    (
        (SYS, "MODELNAME"),
        [
            (SYS, "MODELNAME", "ModelName"),
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
    # BT Subunit init start
    (
        (BT, "AVAIL"),
        [
            (BT, "AVAIL", "Not Connected"),
        ],
    ),
    # BT Subunit iniatilize sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
    # MAIN Subunit init start
    (
        (MAIN, "AVAIL"),
        [
            (MAIN, "AVAIL", "Not Ready"),
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


def test_construct():

    r = ynca.Receiver("serial_url")
    assert len(r.inputs.keys()) == 0

    r.close()


def test_check_connection_check_success(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = CONNECTION_CHECK_RESPONSES

        disconnect_callback = mock.MagicMock()

        r = ynca.Receiver("serial_url", disconnect_callback)
        modelname = r.connection_check()
        assert modelname == "ModelName"

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_check_connection_check_fail_connect(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.connect.side_effect = YncaConnectionError("something is wrong")

        disconnect_callback = mock.MagicMock()

        r = ynca.Receiver("serial_url", disconnect_callback)
        with pytest.raises(YncaConnectionError):
            r.connection_check()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_check_connection_check_fail_no_response(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection

        disconnect_callback = mock.MagicMock()

        r = ynca.Receiver("serial_url", disconnect_callback)
        with pytest.raises(YncaConnectionError):
            r.connection_check()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


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

        assert isinstance(r.SYS, System)
        assert r.SYS.version == "Version"

        r.close()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_close(connection):

    with mock.patch.object(
        ynca.receiver.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        r = ynca.Receiver("serial_url")
        r.close()
        r.initialize()

        r.close()
        connection.close.assert_called_once()

        # Should be safe to call multiple times
        r.close()
        connection.close.assert_called_once()


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

        connection.close.assert_called_once()
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

        assert len(r.inputs.keys()) == 3
        assert r.inputs["ONE"] == "InputOne"
        assert r.inputs["TWO"] == "InputTwo"
        assert r.inputs["Bluetooth"] == "Bluetooth"

        assert len(r._subunits.keys()) == 3

        assert isinstance(r.SYS, System)
        assert r.SYS.modelname == "ModelName"
        assert r.SYS.version == "Version"

        assert isinstance(r.MAIN, Main)
        assert r.MAIN.name == "MainZoneName"
        assert isinstance(r.BT, Bt)
        assert r.ZONE2 is None
        assert r.ZONE3 is None
        assert r.ZONE4 is None

        assert r.AIRPLAY is None
        assert r.IPOD is None
        assert r.IPODUSB is None
        assert r.NAPSTER is None
        assert r.NETRADIO is None
        assert r.PANDORA is None
        assert r.PC is None
        assert r.RHAP is None
        assert r.SERVER is None
        assert r.SIRIUS is None
        assert r.SIRIUSIR is None
        assert r.SIRIUSXM is None
        assert r.SPOTIFY is None
        assert r.TUN is None
        assert r.UAW is None
        assert r.USB is None

        r.close()
