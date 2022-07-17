from typing import Dict, cast
from .subunit import Subunit
from .system import System
from .ynca import Ynca

# Map subunits to input names, this is used for discovering what inputs are available
# Inputs missing because unknown what subunit they map to: NET
SUBUNIT_INPUT_MAPPINGS: Dict[Subunit, str] = {
    Subunit.TUN: "TUNER",
    Subunit.SIRIUS: "SIRIUS",
    Subunit.IPOD: "iPod",
    Subunit.BT: "Bluetooth",
    Subunit.RHAP: "Rhapsody",
    Subunit.SIRIUSIR: "SIRIUS InternetRadio",
    Subunit.PANDORA: "Pandora",
    Subunit.NAPSTER: "Napster",
    Subunit.PC: "PC",
    Subunit.NETRADIO: "NET RADIO",
    Subunit.USB: "USB",
    Subunit.IPODUSB: "iPod (USB)",
    Subunit.UAW: "UAW",
    Subunit.SPOTIFY: "Spotify",
    Subunit.SIRIUSXM: "SiriusXM",
    Subunit.SERVER: "SERVER",
    Subunit.AIRPLAY: "AirPlay",
}

# This list of inputs is used in case INPNAME is not reported by the device
# It contains all known inputs
FALLBACK_INPUTS = {
    "HDMI1": "HDMI1",
    "HDMI2": "HDMI2",
    "HDMI3": "HDMI3",
    "HDMI4": "HDMI4",
    "HDMI5": "HDMI5",
    "HDMI6": "HDMI6",
    "HDMI7": "HDMI7",
    "AV1": "AV1",
    "AV2": "AV2",
    "AV3": "AV3",
    "AV4": "AV4",
    "AV5": "AV5",
    "AV6": "AV6",
    "AV7": "AV7",
    "AUDIO1": "AUDIO1",
    "AUDIO2": "AUDIO2",
    "AUDIO3": "AUDIO3",
    "AUDIO4": "AUDIO4",
    "PHONO": "PHONO",
    "MULTI CH": "MULTI CH",
    "VAUX": "V-AUX",
}


def get_all_zone_inputs(ynca: Ynca) -> Dict[str, str]:
    """
    Returns a dictionary of all available inputs that can be used as
    input on the Zone subunits. Note that this does not mean that every zone
    can/will support all of the inputs. Typically the MAIN will support all
    other zones less. It is not possible to determine that mapping from the API.

    Key is the value to use for `input`,
    Value is the user given name if available, otherwise input name.

    For receivers that do _not_ respond to INPNAME a fallback list of inputs is returned containing all known options
    """
    inputs = {}

    # There are internal inputs provided by subunits
    # for example the "Tuner"input is provided by the TUN subunit
    for subunit in SUBUNIT_INPUT_MAPPINGS.keys():
        if getattr(ynca, subunit, None):
            input_id = SUBUNIT_INPUT_MAPPINGS[subunit]
            inputs[input_id] = input_id

    # The SYS subunit has the externally connectable inputs like HDMI1, AV1 etc...
    # try to detect which ones are available by looking at the INPNAMEs
    # Do this after subunits because USB and DOCK can be renamed
    if ynca.SYS:
        inp_names = cast(System, ynca._subunits[Subunit.SYS]).inp_names
        if len(inp_names) == 0:
            inputs.update(FALLBACK_INPUTS)
        else:
            inputs.update(inp_names)

    return inputs
