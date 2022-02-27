"""Test YNCA Receiver"""

from typing import Callable
from unittest import mock
import pytest

from ynca.system import System
from ynca.errors import YncaInitializationFailedException

from .connectionmock import YncaConnectionMock

SYS = "SYS"

INITIALIZE_FULL_RESPONSES = [
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
            (SYS, "INPNAMEPHONO", "InputPhono"),
            (SYS, "INPNAMEHDMI1", "InputHdmi1"),
            (SYS, "INPNAMEHDMI2", "InputHdmi2"),
            (SYS, "INPNAMEHDMI3", "InputHdmi3"),
            (SYS, "INPNAMEHDMI4", "InputHdmi4"),
            (SYS, "INPNAMEHDMI5", "InputHdmi5"),
            (SYS, "INPNAMEHDMI6", "InputHdmi6"),
            (SYS, "INPNAMEHDMI7", "InputHdmi7"),
            (SYS, "INPNAMEAV1", "InputAv1"),
            (SYS, "INPNAMEAV2", "InputAv2"),
            (SYS, "INPNAMEAV3", "InputAv3"),
            (SYS, "INPNAMEAV4", "InputAv4"),
            (SYS, "INPNAMEAV5", "InputAv5"),
            (SYS, "INPNAMEAV6", "InputAv6"),
            (SYS, "INPNAMEVAUX", "InputVAux"),
            (SYS, "INPNAMEAUDIO1", "InputAudio1"),
            (SYS, "INPNAMEAUDIO2", "InputAudio2"),
            (SYS, "INPNAMEDOCK", "InputDock"),
            (SYS, "INPNAMEUSB", "InputUsb"),
        ],
    ),
    (
        ("TUN", "AVAIL"),
        [
            ("TUN", "AVAIL", "Not Ready"),
        ],
    ),
    (
        ("SIRIUS", "AVAIL"),
        [
            ("@RESTRICTED"),
        ],
    ),
    (
        ("IPOD", "AVAIL"),
        [
            ("IPOD", "AVAIL", "Not Connected"),
        ],
    ),
    (
        ("BT", "AVAIL"),
        [
            ("BT", "AVAIL", "Not Connected"),
        ],
    ),
    (
        ("RHAP", "AVAIL"),
        [
            ("@RESTRICTED"),
        ],
    ),
    (
        ("SIRIUSIR", "AVAIL"),
        [
            ("@RESTRICTED"),
        ],
    ),
    (
        ("PANDORA", "AVAIL"),
        [
            ("@RESTRICTED"),
        ],
    ),
    (
        ("NAPSTER", "AVAIL"),
        [
            ("NAPSTER", "AVAIL", "Not Connected"),
        ],
    ),
    (
        ("PC", "AVAIL"),
        [
            ("PC", "AVAIL", "Not Connected"),
        ],
    ),
    (
        ("NETRADIO", "AVAIL"),
        [
            ("NETRADIO", "AVAIL", "Not Connected"),
        ],
    ),
    (
        ("IPODUSB", "AVAIL"),
        [
            ("IPODUSB", "AVAIL", "Not Connected"),
        ],
    ),
    (
        ("UAW", "AVAIL"),
        [
            ("UAW", "AVAIL", "Not Connected"),
        ],
    ),
    (
        ("MAIN", "AVAIL"),
        [
            ("MAIN", "AVAIL", "Not Ready"),
        ],
    ),
    (
        ("ZONE2", "AVAIL"),
        [
            ("ZONE2", "AVAIL", "Not Ready"),
        ],
    ),
    (
        ("ZONE3", "AVAIL"),
        [
            ("@RESTRICTED"),
        ],
    ),
    (
        ("ZONE4", "AVAIL"),
        [
            ("@RESTRICTED"),
        ],
    ),
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


@pytest.fixture
def update_callback() -> Callable[[], None]:
    return mock.MagicMock()


@pytest.fixture
def initialized_receiver(connection) -> System:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    r = System(SYS, connection)
    r.initialize()
    return r


def test_construct(connection, update_callback):

    r = System(SYS, connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_fail(connection, update_callback):

    r = System(SYS, connection)
    r.register_update_callback(update_callback)

    with pytest.raises(YncaInitializationFailedException):
        r.initialize()

    assert update_callback.call_count == 0


def test_initialize_minimal(connection, update_callback):
    connection.get_response_list = [
        (
            (SYS, "VERSION"),
            [
                (SYS, "VERSION", "Version"),
            ],
        ),
    ]

    r = System(SYS, connection)
    r.register_update_callback(update_callback)

    r.initialize()

    assert update_callback.call_count == 1
    assert r.firmware_version == "Version"
    assert r.on is None
    assert r.model_name is None
    assert len(r.inputs.keys()) == 0
    assert len(r.zones) == 0


def test_initialize_full(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    r = System(SYS, connection)
    r.register_update_callback(update_callback)

    r.initialize()

    assert update_callback.call_count == 1
    assert r.firmware_version == "Version"
    assert r.model_name == "ModelName"
    assert r.on is False
    assert r.zones == ["MAIN", "ZONE2"]

    assert len(r.inputs.keys()) == 27
    assert r.inputs["PHONO"] == "InputPhono"
    assert r.inputs["HDMI1"] == "InputHdmi1"
    assert r.inputs["HDMI2"] == "InputHdmi2"
    assert r.inputs["HDMI3"] == "InputHdmi3"
    assert r.inputs["HDMI4"] == "InputHdmi4"
    assert r.inputs["HDMI5"] == "InputHdmi5"
    assert r.inputs["HDMI6"] == "InputHdmi6"
    assert r.inputs["HDMI7"] == "InputHdmi7"
    assert r.inputs["AV1"] == "InputAv1"
    assert r.inputs["AV2"] == "InputAv2"
    assert r.inputs["AV3"] == "InputAv3"
    assert r.inputs["AV4"] == "InputAv4"
    assert r.inputs["AV5"] == "InputAv5"
    assert r.inputs["AV6"] == "InputAv6"
    assert r.inputs["V-AUX"] == "InputVAux"
    assert r.inputs["AUDIO1"] == "InputAudio1"
    assert r.inputs["AUDIO2"] == "InputAudio2"
    assert r.inputs["DOCK"] == "InputDock"
    assert r.inputs["USB"] == "InputUsb"
    assert r.inputs["TUNER"] == "TUNER"
    assert r.inputs["iPod"] == "iPod"
    assert r.inputs["Bluetooth"] == "Bluetooth"
    assert r.inputs["Napster"] == "Napster"
    assert r.inputs["PC"] == "PC"
    assert r.inputs["NET RADIO"] == "NET RADIO"
    assert r.inputs["iPod (USB)"] == "iPod (USB)"
    assert r.inputs["UAW"] == "UAW"


def test_on(connection, initialized_receiver):
    # Writing to device
    initialized_receiver.on = True
    connection.put.assert_called_with(SYS, "PWR", "On")
    initialized_receiver.on = False
    connection.put.assert_called_with(SYS, "PWR", "Standby")

    # Updates from device
    connection.send_protocol_message(SYS, "PWR", "On")
    assert initialized_receiver.on == True
    connection.send_protocol_message(SYS, "PWR", "Standby")
    assert initialized_receiver.on == False


def test_callbacks(connection, initialized_receiver, update_callback):
    update_callback_2 = mock.MagicMock()

    # Register multiple callbacks, both get called
    initialized_receiver.register_update_callback(update_callback)
    initialized_receiver.register_update_callback(update_callback_2)
    connection.send_protocol_message(SYS, "PWR", "On")
    assert update_callback.call_count == 1
    assert update_callback_2.call_count == 1

    # Double registration (second gets ignored)
    initialized_receiver.register_update_callback(update_callback_2)
    connection.send_protocol_message(SYS, "PWR", "On")
    assert update_callback.call_count == 2
    assert update_callback_2.call_count == 2

    # Unregistration
    initialized_receiver.unregister_update_callback(update_callback_2)
    connection.send_protocol_message(SYS, "PWR", "On")
    assert update_callback.call_count == 3
    assert update_callback_2.call_count == 2
