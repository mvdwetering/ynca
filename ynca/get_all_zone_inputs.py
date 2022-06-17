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


def get_all_zone_inputs(ynca: Ynca) -> Dict[str, str]:
    """
    Returns a dictionary of all available inputs that can be used as
    input on the Zone subunits. Note that this does not mean that every zone
    can/will support all of the inputs. Typically the MAIN will support all
    other zones less. It is not possible to determine that mapping from the API.

    Key is the value to use for `input`,
    Value is the user given name if available, otherwise input name.
    """
    inputs = {}

    # The SYS subunit has the externally connectable inputs like HDMI1, AV1 etc...
    if ynca.SYS:
        inputs = cast(System, ynca._subunits[Subunit.SYS]).inputs

    # Next to that there are internal inputs provided by subunits
    # for example the "Tuner"input is provided by the TUN subunit
    for subunit in SUBUNIT_INPUT_MAPPINGS.keys():
        if getattr(ynca, subunit, None):
            input_id = SUBUNIT_INPUT_MAPPINGS[subunit]
            inputs[input_id] = input_id

    return dict(inputs)
