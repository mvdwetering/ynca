from collections.abc import Callable
from typing import Any
from unittest import mock

import pytest

from tests.mock_yncaconnection import YncaConnectionMock
from ynca import HdmiOutOnOff, Party, PartyMute, Pwr, SpPattern, System

SYS = "SYS"

INITIALIZE_FULL_RESPONSES = [
    (
        (SYS, "AVAIL"),
        [
            (SYS, "AVAIL", "Ready"),
        ],
    ),
    (
        (SYS, "HDMIOUT1"),
        [
            (SYS, "HDMIOUT1", "On"),
        ],
    ),
    (
        (SYS, "HDMIOUT2"),
        [
            (SYS, "HDMIOUT2", "Off"),
        ],
    ),
    (
        (SYS, "HDMIOUT3"),
        [
            (SYS, "HDMIOUT3", "Off"),
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
            (SYS, "INPNAMEAV7", "InputAv7"),
            (SYS, "INPNAMEVAUX", "InputVAux"),
            (SYS, "INPNAMEAUDIO1", "InputAudio1"),
            (SYS, "INPNAMEAUDIO2", "InputAudio2"),
            (SYS, "INPNAMEAUDIO3", "InputAudio3"),
            (SYS, "INPNAMEAUDIO4", "InputAudio4"),
            (SYS, "INPNAMEDOCK", "InputDock"),
            (SYS, "INPNAMEUSB", "InputUsb"),
            (SYS, "INPNAMEMULTICH", "InputMultiCh"),
        ],
    ),
    (
        (SYS, "MODELNAME"),
        [
            (SYS, "MODELNAME", "ModelName"),
        ],
    ),
    (
        (SYS, "PARTY"),
        [
            (SYS, "PARTY", "On"),
        ],
    ),
    (
        (SYS, "PWR"),
        [
            (SYS, "PWR", "Standby"),
        ],
    ),
    (
        (SYS, "SPPATTERN"),
        [
            (SYS, "SPPATTERN", "Pattern 2"),
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
def initialized_system(connection: YncaConnectionMock) -> System:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES
    r = System(connection)
    r.initialize()
    return r


def test_construct(connection: YncaConnectionMock, update_callback: mock.Mock) -> None:
    System(connection)

    assert connection.register_message_callback.call_count == 1
    assert update_callback.call_count == 0


def test_initialize_minimal(
    connection: YncaConnectionMock, update_callback: Callable[[str, Any], None]
) -> None:
    connection.get_response_list = [
        (
            (SYS, "AVAIL"),
            [
                (SYS, "AVAIL", "Ready"),
            ],
        ),
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

    assert s.version == "Version"
    assert s.modelname is None
    assert s.hdmiout1 is None
    assert s.hdmiout2 is None
    assert s.hdmiout3 is None
    assert s.inpnameaudio1 is None
    assert s.inpnameaudio2 is None
    assert s.inpnameaudio3 is None
    assert s.inpnameaudio4 is None
    assert s.inpnameav1 is None
    assert s.inpnameav2 is None
    assert s.inpnameav3 is None
    assert s.inpnameav4 is None
    assert s.inpnameav5 is None
    assert s.inpnameav6 is None
    assert s.inpnameav7 is None
    assert s.inpnamedock is None
    assert s.inpnamehdmi1 is None
    assert s.inpnamehdmi2 is None
    assert s.inpnamehdmi3 is None
    assert s.inpnamehdmi4 is None
    assert s.inpnamehdmi5 is None
    assert s.inpnamehdmi6 is None
    assert s.inpnamehdmi7 is None
    assert s.inpnamemultich is None
    assert s.inpnamephono is None
    assert s.inpnameusb is None
    assert s.inpnamevaux is None
    assert s.pwr is None
    assert s.party is None
    assert s.sppattern is None


def test_initialize_full(
    connection: YncaConnectionMock, update_callback: mock.Mock
) -> None:
    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    s = System(connection)
    s.register_update_callback(update_callback)

    s.initialize()

    assert update_callback.call_count == 0
    assert s.version == "Version"
    assert s.modelname == "ModelName"

    assert s.hdmiout1 is HdmiOutOnOff.ON
    assert s.hdmiout2 is HdmiOutOnOff.OFF
    assert s.hdmiout3 is HdmiOutOnOff.OFF

    assert s.inpnameaudio1 == "InputAudio1"
    assert s.inpnameaudio2 == "InputAudio2"
    assert s.inpnameaudio3 == "InputAudio3"
    assert s.inpnameaudio4 == "InputAudio4"
    assert s.inpnameav1 == "InputAv1"
    assert s.inpnameav2 == "InputAv2"
    assert s.inpnameav3 == "InputAv3"
    assert s.inpnameav4 == "InputAv4"
    assert s.inpnameav5 == "InputAv5"
    assert s.inpnameav6 == "InputAv6"
    assert s.inpnameav7 == "InputAv7"
    assert s.inpnamedock == "InputDock"
    assert s.inpnamehdmi1 == "InputHdmi1"
    assert s.inpnamehdmi2 == "InputHdmi2"
    assert s.inpnamehdmi3 == "InputHdmi3"
    assert s.inpnamehdmi4 == "InputHdmi4"
    assert s.inpnamehdmi5 == "InputHdmi5"
    assert s.inpnamehdmi6 == "InputHdmi6"
    assert s.inpnamehdmi7 == "InputHdmi7"
    assert s.inpnamemultich == "InputMultiCh"
    assert s.inpnamephono == "InputPhono"
    assert s.inpnameusb == "InputUsb"
    assert s.inpnamevaux == "InputVAux"

    assert s.party == Party.ON
    assert s.pwr == Pwr.STANDBY
    assert s.sppattern == SpPattern.PATTERN_2


def test_hdmiout(connection: YncaConnectionMock, initialized_system: System) -> None:
    # Writing to device
    initialized_system.hdmiout1 = HdmiOutOnOff.ON
    connection.put.assert_called_with(SYS, "HDMIOUT1", "On")
    initialized_system.hdmiout2 = HdmiOutOnOff.OFF
    connection.put.assert_called_with(SYS, "HDMIOUT2", "Off")


def test_party(connection: YncaConnectionMock, initialized_system: System) -> None:
    # Writing to device
    initialized_system.party = Party.ON
    connection.put.assert_called_with(SYS, "PARTY", "On")
    initialized_system.party = Party.OFF
    connection.put.assert_called_with(SYS, "PARTY", "Off")


def test_partymute(connection: YncaConnectionMock, initialized_system: System) -> None:
    # Writing to device
    initialized_system.partymute = PartyMute.ON
    connection.put.assert_called_with(SYS, "PARTYMUTE", "On")
    initialized_system.partymute = PartyMute.OFF
    connection.put.assert_called_with(SYS, "PARTYMUTE", "Off")


def test_partyvol(connection: YncaConnectionMock, initialized_system: System) -> None:
    # Writing to device
    initialized_system.partyvol_up()
    connection.put.assert_called_with(SYS, "PARTYVOL", "Up")
    initialized_system.partyvol_down()
    connection.put.assert_called_with(SYS, "PARTYVOL", "Down")


def test_partyvol_method(
    connection: YncaConnectionMock, initialized_system: System
) -> None:
    # Writing to device
    initialized_system.partyvol_up()
    connection.put.assert_called_with(SYS, "PARTYVOL", "Up")
    initialized_system.partyvol_down()
    connection.put.assert_called_with(SYS, "PARTYVOL", "Down")


def test_remotecode(connection: YncaConnectionMock, initialized_system: System) -> None:
    initialized_system.remotecode("code1234")
    connection.put.assert_called_with(SYS, "REMOTECODE", "code1234")


def test_remotecode_wrong_length(initialized_system: System) -> None:
    with pytest.raises(ValueError, match="REMOTECODE value must be of length 8"):
        initialized_system.remotecode("7777777")
    with pytest.raises(ValueError, match="REMOTECODE value must be of length 8"):
        initialized_system.remotecode("999999999")


def test_unhandled_function(
    connection: YncaConnectionMock, initialized_system: System
) -> None:
    # Updates from device
    update_callback_1 = mock.MagicMock()
    initialized_system.register_update_callback(update_callback_1)
    connection.send_protocol_message(SYS, "UnknownFunction", "On")
    assert update_callback_1.call_count == 0
