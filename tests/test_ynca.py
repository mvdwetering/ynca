from unittest import mock

import pytest
import ynca
from ynca.bt import Bt
from ynca.errors import YncaConnectionError, YncaInitializationFailedException
from ynca.get_all_zone_inputs import FALLBACK_INPUTS
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
    y = ynca.Ynca("serial_url")
    y.close()


def test_check_connection_check_success(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = CONNECTION_CHECK_RESPONSES

        disconnect_callback = mock.MagicMock()

        y = ynca.Ynca("serial_url", disconnect_callback, 123)
        modelname = y.connection_check()
        assert modelname == "ModelName"

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_check_connection_check_fail_connect(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.connect.side_effect = YncaConnectionError("something is wrong")

        disconnect_callback = mock.MagicMock()

        y = ynca.Ynca("serial_url", disconnect_callback)
        with pytest.raises(YncaConnectionError):
            y.connection_check()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_check_connection_check_fail_no_response(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection

        disconnect_callback = mock.MagicMock()

        y = ynca.Ynca("serial_url", disconnect_callback)
        with pytest.raises(YncaConnectionError):
            y.connection_check()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_initialize_minimal(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        disconnect_callback = mock.MagicMock()

        y = ynca.Ynca("serial_url", disconnect_callback)
        y.initialize()

        assert isinstance(y.SYS, System)
        assert y.SYS.version == "Version"

        inputs = ynca.get_inputinfo_list(y)
        assert sorted([inp.input for inp in inputs]) == sorted(FALLBACK_INPUTS.keys())
        assert sorted([inp.name for inp in inputs]) == sorted(FALLBACK_INPUTS.values())

        y.close()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_close(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        y = ynca.Ynca("serial_url")
        y.close()
        y.initialize()

        y.close()
        connection.close.assert_called_once()

        # Should be safe to call multiple times
        y.close()
        connection.close.assert_called_once()


def test_initialize_fail(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = []

        disconnect_callback = mock.MagicMock()

        y = ynca.Ynca("serial_url", disconnect_callback)
        with pytest.raises(YncaInitializationFailedException):
            y.initialize()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_disconnect_callback(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        disconnect_callback = mock.MagicMock()

        y = ynca.Ynca("serial_url", disconnect_callback)
        y.initialize()

        # Report disconnect from connection by using callback registered in connect call
        connection.connect.call_args.args[0]()
        disconnect_callback.assert_called_once()

        y.close()


def test_initialize_full(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection

        connection.get_response_list = INITIALIZE_FULL_RESPONSES

        y = ynca.Ynca("serial_url")
        y.initialize()

        inputs = ynca.get_inputinfo_list(y)

        assert len(inputs) == 3
        assert [inp for inp in inputs if inp.input == "ONE"][0].name == "InputOne"
        assert [inp for inp in inputs if inp.input == "TWO"][0].name == "InputTwo"
        assert [inp for inp in inputs if inp.input == "Bluetooth"][
            0
        ].name == "Bluetooth"

        assert len(y._subunits.keys()) == 3

        assert isinstance(y.SYS, System)
        assert y.SYS.modelname == "ModelName"
        assert y.SYS.version == "Version"

        assert isinstance(y.MAIN, Main)
        assert y.MAIN.zonename == "MainZoneName"
        assert isinstance(y.BT, Bt)
        assert y.ZONE2 is None
        assert y.ZONE3 is None
        assert y.ZONE4 is None

        assert y.AIRPLAY is None
        assert y.IPOD is None
        assert y.IPODUSB is None
        assert y.NAPSTER is None
        assert y.NETRADIO is None
        assert y.PANDORA is None
        assert y.PC is None
        assert y.RHAP is None
        assert y.SERVER is None
        assert y.SIRIUS is None
        assert y.SIRIUSIR is None
        assert y.SIRIUSXM is None
        assert y.SPOTIFY is None
        assert y.TUN is None
        assert y.UAW is None
        assert y.USB is None

        y.close()


def test_initialize_full_deprecated_receiver(connection):

    with mock.patch.object(
        ynca.ynca.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection

        connection.get_response_list = INITIALIZE_FULL_RESPONSES

        y = ynca.Receiver("serial_url")
        y.initialize()

        inputs = y.inputs

        assert len(inputs.keys()) == 3
        assert inputs["ONE"] == "InputOne"
        assert inputs["TWO"] == "InputTwo"
        assert inputs["Bluetooth"] == "Bluetooth"

        assert len(y._subunits.keys()) == 3

        assert isinstance(y.SYS, System)
        assert y.SYS.modelname == "ModelName"
        assert y.SYS.version == "Version"

        assert isinstance(y.MAIN, Main)
        assert y.MAIN.zonename == "MainZoneName"
        assert isinstance(y.BT, Bt)
        assert y.ZONE2 is None
        assert y.ZONE3 is None
        assert y.ZONE4 is None

        assert y.AIRPLAY is None
        assert y.IPOD is None
        assert y.IPODUSB is None
        assert y.NAPSTER is None
        assert y.NETRADIO is None
        assert y.PANDORA is None
        assert y.PC is None
        assert y.RHAP is None
        assert y.SERVER is None
        assert y.SIRIUS is None
        assert y.SIRIUSIR is None
        assert y.SIRIUSXM is None
        assert y.SPOTIFY is None
        assert y.TUN is None
        assert y.UAW is None
        assert y.USB is None

        y.close()
