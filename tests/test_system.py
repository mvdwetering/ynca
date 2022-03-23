"""Test SYS subunit"""

from typing import Callable
from unittest import mock
import pytest

from ynca.system import System

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
def initialized_system(connection) -> System:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    r = System(connection)
    r.initialize()
    return r


def test_construct(connection, update_callback):

    r = System(connection)

    assert connection.register_message_callback.call_count == 1
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

    s = System(connection)
    s.register_update_callback(update_callback)

    s.initialize()

    assert update_callback.call_count == 1
    assert s.version == "Version"
    assert s.on is None
    assert s.model_name is None
    assert len(s.inputs.keys()) == 0


def test_initialize_full(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    s = System(connection)
    s.register_update_callback(update_callback)

    s.initialize()

    assert update_callback.call_count == 1
    assert s.version == "Version"
    assert s.model_name == "ModelName"
    assert s.on is False

    assert len(s.inputs.keys()) == 19
    assert s.inputs["PHONO"] == "InputPhono"
    assert s.inputs["HDMI1"] == "InputHdmi1"
    assert s.inputs["HDMI2"] == "InputHdmi2"
    assert s.inputs["HDMI3"] == "InputHdmi3"
    assert s.inputs["HDMI4"] == "InputHdmi4"
    assert s.inputs["HDMI5"] == "InputHdmi5"
    assert s.inputs["HDMI6"] == "InputHdmi6"
    assert s.inputs["HDMI7"] == "InputHdmi7"
    assert s.inputs["AV1"] == "InputAv1"
    assert s.inputs["AV2"] == "InputAv2"
    assert s.inputs["AV3"] == "InputAv3"
    assert s.inputs["AV4"] == "InputAv4"
    assert s.inputs["AV5"] == "InputAv5"
    assert s.inputs["AV6"] == "InputAv6"
    assert s.inputs["V-AUX"] == "InputVAux"
    assert s.inputs["AUDIO1"] == "InputAudio1"
    assert s.inputs["AUDIO2"] == "InputAudio2"
    assert s.inputs["DOCK"] == "InputDock"
    assert s.inputs["USB"] == "InputUsb"


def test_registration(connection, initialized_system):

    update_callback_1 = mock.MagicMock()
    update_callback_2 = mock.MagicMock()

    # Register multiple callbacks, both get called
    initialized_system.register_update_callback(update_callback_1)
    initialized_system.register_update_callback(update_callback_2)
    connection.send_protocol_message(SYS, "PWR", "On")
    assert update_callback_1.call_count == 1
    assert update_callback_2.call_count == 1

    # Double registration (second gets ignored)
    initialized_system.register_update_callback(update_callback_2)
    connection.send_protocol_message(SYS, "PWR", "On")
    assert update_callback_1.call_count == 2
    assert update_callback_2.call_count == 2

    # Unregistration
    initialized_system.unregister_update_callback(update_callback_2)
    connection.send_protocol_message(SYS, "PWR", "On")
    assert update_callback_1.call_count == 3
    assert update_callback_2.call_count == 2


def test_on(connection, initialized_system):
    # Writing to device
    initialized_system.on = True
    connection.put.assert_called_with(SYS, "PWR", "On")
    initialized_system.on = False
    connection.put.assert_called_with(SYS, "PWR", "Standby")

    # Updates from device
    connection.send_protocol_message(SYS, "PWR", "On")
    assert initialized_system.on == True
    connection.send_protocol_message(SYS, "PWR", "Standby")
    assert initialized_system.on == False


def test_unhandled_function(connection, initialized_system):

    # Updates from device
    update_callback_1 = mock.MagicMock()
    initialized_system.register_update_callback(update_callback_1)
    connection.send_protocol_message(SYS, "UnknownFunction", "On")
    assert update_callback_1.call_count == 0
