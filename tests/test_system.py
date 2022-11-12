from unittest import mock
import pytest

from ynca.system import Party, PartyMute, PartyVol, Pwr, System

SYS = "SYS"

INITIALIZE_FULL_RESPONSES = [
    (
        (SYS, "AVAIL"),
        [
            (SYS, "AVAIL", "Ready"),
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
    assert s.pwr is None
    assert s.party is None
    assert len(s.inp_names.keys()) == 0


def test_initialize_full(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    s = System(connection)
    s.register_update_callback(update_callback)

    s.initialize()

    assert update_callback.call_count == 0
    assert s.version == "Version"
    assert s.modelname == "ModelName"
    assert s.pwr == Pwr.STANDBY
    assert s.party == Party.ON

    assert len(s.inp_names.keys()) == 19
    assert s.inp_names["PHONO"] == "InputPhono"
    assert s.inp_names["HDMI1"] == "InputHdmi1"
    assert s.inp_names["HDMI2"] == "InputHdmi2"
    assert s.inp_names["HDMI3"] == "InputHdmi3"
    assert s.inp_names["HDMI4"] == "InputHdmi4"
    assert s.inp_names["HDMI5"] == "InputHdmi5"
    assert s.inp_names["HDMI6"] == "InputHdmi6"
    assert s.inp_names["HDMI7"] == "InputHdmi7"
    assert s.inp_names["AV1"] == "InputAv1"
    assert s.inp_names["AV2"] == "InputAv2"
    assert s.inp_names["AV3"] == "InputAv3"
    assert s.inp_names["AV4"] == "InputAv4"
    assert s.inp_names["AV5"] == "InputAv5"
    assert s.inp_names["AV6"] == "InputAv6"
    assert s.inp_names["V-AUX"] == "InputVAux"
    assert s.inp_names["AUDIO1"] == "InputAudio1"
    assert s.inp_names["AUDIO2"] == "InputAudio2"
    assert s.inp_names["DOCK"] == "InputDock"
    assert s.inp_names["USB"] == "InputUsb"


def test_party(connection, initialized_system: System):
    # Writing to device
    initialized_system.party = Party.ON
    connection.put.assert_called_with(SYS, "PARTY", "On")
    initialized_system.party = Party.OFF
    connection.put.assert_called_with(SYS, "PARTY", "Off")


def test_partymute(connection, initialized_system: System):
    # Writing to device
    initialized_system.partymute = PartyMute.ON
    connection.put.assert_called_with(SYS, "PARTYMUTE", "On")
    initialized_system.partymute = PartyMute.OFF
    connection.put.assert_called_with(SYS, "PARTYMUTE", "Off")


def test_partyvol(connection, initialized_system: System):
    # Writing to device
    initialized_system.partyvol = PartyVol.UP
    connection.put.assert_called_with(SYS, "PARTYVOL", "Up")
    initialized_system.partyvol = PartyVol.DOWN
    connection.put.assert_called_with(SYS, "PARTYVOL", "Down")


def test_partyvol_method(connection, initialized_system: System):
    # Writing to device
    initialized_system.partyvol_up()
    connection.put.assert_called_with(SYS, "PARTYVOL", "Up")
    initialized_system.partyvol_down()
    connection.put.assert_called_with(SYS, "PARTYVOL", "Down")


def test_remotecode(connection, initialized_system: System):
    initialized_system.remotecode = "code1234"
    connection.put.assert_called_with(SYS, "REMOTECODE", "code1234")


def test_remotecode_wrong_length(connection, initialized_system: System):
    with pytest.raises(ValueError):
        initialized_system.remotecode = "7777777"
    with pytest.raises(ValueError):
        initialized_system.remotecode = "999999999"


def test_unhandled_function(connection, initialized_system: System):

    # Updates from device
    update_callback_1 = mock.MagicMock()
    initialized_system.register_update_callback(update_callback_1)
    connection.send_protocol_message(SYS, "UnknownFunction", "On")
    assert update_callback_1.call_count == 0
