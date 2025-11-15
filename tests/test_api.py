from unittest import mock

import pytest

from tests.mock_yncaconnection import YncaConnectionMock
import ynca
from ynca.errors import (
    YncaConnectionError,
    YncaException,
    YncaInitializationFailedException,
)

SYS = "SYS"
MAIN = "MAIN"
ZONE2 = "ZONE2"
ZONE3 = "ZONE3"
ZONE4 = "ZONE4"
BT = "BT"
USB = "USB"

RESTRICTED = "@RESTRICTED"

CONNECTION_CHECK_RESPONSES_NO_ZONES = [
    (
        (SYS, "MODELNAME"),
        [
            (SYS, "MODELNAME", "ModelName"),
        ],
    ),
]

CONNECTION_CHECK_RESPONSES_ALL_ZONES = [
    (
        (MAIN, "AVAIL"),
        [
            (MAIN, "AVAIL", "Not Ready"),
        ],
    ),
    (
        (ZONE2, "AVAIL"),
        [
            (ZONE2, "AVAIL", "Not Ready"),
        ],
    ),
    (
        (ZONE3, "AVAIL"),
        [
            (ZONE3, "AVAIL", "Not Ready"),
        ],
    ),
    (
        (ZONE4, "AVAIL"),
        [
            (ZONE4, "AVAIL", "Not Ready"),
        ],
    ),
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
            (RESTRICTED, "", ""),
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
            (RESTRICTED, "", ""),
        ],
    ),
    (
        (BT, "AVAIL"),
        [
            (BT, "AVAIL", "Not Connected"),
        ],
    ),
    (
        (USB, "AVAIL"),
        [
            (USB, "AVAIL", "Not Connected"),
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
            (RESTRICTED, "", ""),
        ],
    ),
    (
        (SYS, "INPNAME"),
        [
            (SYS, "INPNAMEHDMI1", "InputHdmi1One"),
            (SYS, "INPNAMEUSB", "InputUsb"),
            (SYS, "INPNAMEUNKNOWN", "InputUnknown"),
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
    # SYS Subunit initialize sync
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
    # BT Subunit initialize sync
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
    # USB Subunit init start
    (
        (USB, "AVAIL"),
        [
            (USB, "AVAIL", "Not Connected"),
        ],
    ),
    # USB Subunit iniatilize sync
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
]


def test_construct() -> None:
    y = ynca.YncaApi("serial_url")
    y.close()


def test_check_connection_check_success_all_zones(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = CONNECTION_CHECK_RESPONSES_ALL_ZONES

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback, 123)
        result = y.connection_check()
        assert result.modelname == "ModelName"
        assert len(result.zones) == 4
        assert "MAIN" in result.zones
        assert "ZONE2" in result.zones
        assert "ZONE3" in result.zones
        assert "ZONE4" in result.zones

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_check_connection_check_success_no_zones(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = CONNECTION_CHECK_RESPONSES_NO_ZONES

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback, 123)
        result = y.connection_check()
        assert result.modelname == "ModelName"
        assert len(result.zones) == 0

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_check_connection_check_fail_connect(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.connect.side_effect = YncaConnectionError("something is wrong")

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback)
        with pytest.raises(YncaConnectionError):
            y.connection_check()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_check_connection_check_fail_no_response(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback)
        with pytest.raises(YncaConnectionError):
            y.connection_check()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_initialize_minimal(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback)
        y.initialize()

        assert isinstance(y.sys, ynca.System)
        assert y.sys.version == "Version"

        y.close()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_initialize_twice(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback)
        y.initialize()

        assert isinstance(y.sys, ynca.System)
        assert y.sys.version == "Version"

        with pytest.raises(YncaInitializationFailedException):
            y.initialize()


def test_initialize_fail(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = []

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback)
        with pytest.raises(YncaInitializationFailedException):
            y.initialize()

        connection.close.assert_called_once()
        disconnect_callback.assert_not_called()


def test_close(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        y = ynca.YncaApi("serial_url")
        y.close()
        y.initialize()

        y.close()
        connection.close.assert_called_once()

        # Should be safe to call multiple times
        y.close()
        connection.close.assert_called_once()


def test_disconnect_callback(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        disconnect_callback = mock.MagicMock()

        y = ynca.YncaApi("serial_url", disconnect_callback)
        y.initialize()

        # Report disconnect from connection by using callback registered in connect call
        connection.connect.call_args.args[0]()
        disconnect_callback.assert_called_once()

        y.close()


def test_get_communication_log_items(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        y = ynca.YncaApi("serial_url")
        assert y.get_communication_log_items() == []
        y.initialize()

        connection.get_communication_log_items.return_value = [
            "communication log items"
        ]
        assert y.get_communication_log_items() == ["communication log items"]

        y.close()


def test_send_raw(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        y = ynca.YncaApi("serial_url")
        y.send_raw("not initialized, silently ignored")
        y.initialize()

        y.send_raw("raw data")
        connection.raw.assert_called_with("raw data")

        y.close()


def test_get_connection(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection
        connection.get_response_list = INITIALIZE_MINIMAL_RESPONSES

        y = ynca.YncaApi("serial_url")

        with pytest.raises(YncaException):
            y.get_raw_connection()

        y.initialize()

        assert y.get_raw_connection() is connection

        y.close()


def test_initialize_full(
    connection: YncaConnectionMock,
) -> None:
    with mock.patch.object(
        ynca.api.YncaConnection, "create_from_serial_url"
    ) as create_from_serial_url:
        create_from_serial_url.return_value = connection

        connection.get_response_list = INITIALIZE_FULL_RESPONSES

        y = ynca.YncaApi("serial_url")
        y.initialize()

        assert isinstance(y.sys, ynca.System)
        assert y.sys.modelname == "ModelName"
        assert y.sys.version == "Version"
        assert y.sys.inpnameusb == "InputUsb"

        assert isinstance(y.main, ynca.Main)
        assert y.main.zonename == "MainZoneName"
        assert isinstance(y.bt, ynca.Bt)
        assert isinstance(y.usb, ynca.Usb)
        assert y.zone2 is None
        assert y.zone3 is None
        assert y.zone4 is None

        assert y.airplay is None
        assert y.dab is None
        assert y.deezer is None
        assert y.ipod is None
        assert y.ipodusb is None
        assert y.mclink is None
        assert y.napster is None
        assert y.netradio is None
        assert y.pandora is None
        assert y.pc is None
        assert y.rhap is None
        assert y.server is None
        assert y.sirius is None
        assert y.siriusir is None
        assert y.siriusxm is None
        assert y.spotify is None
        assert y.tidal is None
        assert y.tun is None
        assert y.uaw is None

        y.close()
