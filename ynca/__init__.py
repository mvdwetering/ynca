import logging
from typing import Callable, Dict, cast

from ynca.system import System

from .connection import YncaConnection, YncaConnectionError
from .constants import (
    Avail,
    Band,
    Mute,
    Playback,
    PlaybackInfo,
    Repeat,
    SoundPrg,
    Subunit,
)
from .ynca import (
    SUBUNIT_INPUT_MAPPINGS,
    Ynca,
    YncaInitializationFailedException,
)


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


logging.getLogger(__name__).addHandler(logging.NullHandler())


class Receiver(Ynca):
    """
    Receiver class has been deprecated and replaced by the Ynca class.
    The Ynca class is basically a renamed Receiver without the "inputs" method which does exist in the YNCA API.
    The inputs method on the Receiver class has been replaced by the "get_all_zone_inputs" helper function.
    """

    def __init__(self, serial_url: str, disconnect_callback: Callable[[], None] = None):
        logging.warning("Receiver class is deprecated. Use Ynca class instead.")
        super().__init__(serial_url, disconnect_callback)

    @property
    def inputs(self) -> Dict[str, str]:
        logging.warning(
            "This method is deprecated. Use 'get_all_zone_inputs' helper function instead."
        )

        return get_all_zone_inputs(self)
